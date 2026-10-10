import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. 設定網頁標題與圖示
st.set_page_config(page_title="我的 AI 全能助理", page_icon="🤖", layout="wide")

st.title("🤖 我的專屬 AI 全能助理 (全功能解鎖版)")

# ==================== 側邊欄控制面板 ====================
with st.sidebar:
    st.header("⚙️ 控制面板與設定")
    st.write("在這裡管理你的聊天室與 AI 人格。")
    
    # 【第四階段新增】選擇 AI 的專屬人格
    persona_choice = st.selectbox(
        "🎭 選擇 AI 的對話風格與人格",
        [
            "友善貼心的日常助理",
            "嚴格專業的軟體工程師",
            "幽默風趣的搞笑諧星",
            "博學多聞的歷史教授"
        ]
    )
    
    # 根據選擇轉換成給 AI 的系統指令 (System Instruction)
    if persona_choice == "友善貼心的日常助理":
        system_prompt = "你是一個溫柔、有耐心、說話親切的AI助理，總是給使用者溫暖的鼓勵。"
    elif persona_choice == "嚴格專業的軟體工程師":
        system_prompt = "你是一個嚴格、講求邏輯與效率的資深軟體工程師，說話精簡切中要害，會嚴格要求程式碼品質。"
    elif persona_choice == "幽默風趣的搞笑諧星":
        system_prompt = "你是一個超級搞笑、喜歡講冷笑話跟幽默梗的諧星，回話總是充滿歡樂與趣味。"
    else:
        system_prompt = "你是一個博學多聞的歷史教授，說話充滿智慧、喜歡用歷史故事來比喻現況。"

    st.divider()
    
    # 聯網搜尋開關
    enable_search = st.checkbox("🌐 開啟 Google 即時聯網搜尋", value=False)
    
    # 清除對話按鈕
    if st.button("🗑️ 清除對話紀錄", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    st.markdown("### 💡 功能進度")
    st.success("階段一：側邊欄與清除對話 (已完成)")
    st.success("階段二：Google 聯網搜尋開關 (已完成)")
    st.success("階段三：多模態圖片上傳辨識 (已完成)")
    st.success("階段四：AI 專屬人格設定 (已解鎖大功告成！)")

# ================================================================

# 2. 初始化 Google GenAI Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. 初始化對話歷史紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 畫出過去的對話歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], caption="上傳的圖片", width=300)
        st.markdown(message["content"])

# ==================== 圖片上傳介面 ====================
uploaded_file = st.file_uploader("選擇要讓 AI 看到的圖片 (選填，支援 JPG, PNG)", type=["jpg", "jpeg", "png"])

# 5. 聊天輸入框
if prompt := st.chat_input("請輸入你想問的問題..."):
    
    # 紀錄並顯示使用者訊息
    message_data = {"role": "user", "content": prompt, "image": uploaded_file}
    st.session_state.messages.append(message_data)
    
    with st.chat_message("user"):
        if uploaded_file is not None:
            st.image(uploaded_file, caption="上傳的圖片", width=300)
        st.markdown(prompt)

    # 6. 呼叫 Google GenAI 取得回答
    with st.chat_message("assistant"):
        spinner_text = "AI 正在上網查資料並思考中..." if enable_search else "AI 正在認真思考中..."
        with st.spinner(spinner_text):
            try:
                contents_to_send = []
                
                # 如果有上傳圖片，加入圖片
                if uploaded_file is not None:
                    img = Image.open(uploaded_file)
                    contents_to_send.append(img)
                
                # 加入文字提問
                contents_to_send.append(prompt)
                
                # 建立完整的設定包（包含系統提示詞與思考設定）
                config_params = {
                    "system_instruction": system_prompt, # 注入專屬人格
                    "thinking_config": types.ThinkingConfig(thinking_level="minimal")
                }
                
                # 如果有勾選聯網搜尋，加入工具
                if enable_search:
                    config_params["tools"] = [{"google_search": {}}]
                
                # 呼叫模型
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=contents_to_send,
                    config=types.GenerateContentConfig(**config_params)
                )
                
                ai_reply = response.text
                st.markdown(ai_reply)
                
                # 紀錄 AI 回答
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                
            except Exception as e:
                st.error(f"發生錯誤：{e}")
