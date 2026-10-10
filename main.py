from fastapi import FastAPI, Request, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from google import genai

app = FastAPI()

# ==================== 請在此填入你的憑證 ====================
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")# ==========================================================

# 初始化 LINE 與 Gemini 客戶端
handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)


@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = (await request.body()).decode("utf-8")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    
    try:
        # 呼叫 Gemini 模型（預設使用 gemini-3.5-flash）
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=user_message,
        config={
                "system_instruction": "請一律使用繁體中文（Traditional Chinese）回覆使用者的所有訊息。"
            }
        )
        reply_text = response.text
    except Exception as e:
        reply_text = "抱歉，目前 AI 伺服器連線發生異常，請稍後再試。"
   
 # 將 Gemini 回應的內容透過 LINE Reply API 傳回給使用者
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )