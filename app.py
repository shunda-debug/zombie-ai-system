import streamlit as st
from google import genai
from PIL import Image

# --- 1. ページ設定 (最初に行う) ---
st.set_page_config(page_title="Sci-Core AI", page_icon="⚛️", layout="wide")

# --- 2. デザインの強制適用 (CSSハック) ---
# ライトモードを排除し、最強のダークモードを強制します
st.markdown("""
<style>
    /* 全体の背景を漆黒に */
    .stApp {
        background-color: #050505 !important;
        color: #E0E0E0 !important;
    }
    
    /* サイドバーの背景 */
    [data-testid="stSidebar"] {
        background-color: #0F0F0F !important;
        border-right: 1px solid #333;
    }
    
    /* 入力欄（LINE風）のスタイル調整 */
    .stChatInputContainer {
        background-color: #050505 !important;
    }
    
    /* ヘッダーの非表示（スッキリさせる） */
    header {visibility: hidden;}
    
    /* 数式の文字色（ネオンブルー） */
    .katex { color: #4DA6FF !important; }
    
    /* ユーザーの吹き出し */
    .stChatMessage[data-testid="user"] {
        background-color: #1E1E1E;
        border-radius: 15px;
        padding: 10px;
    }
    
    /* AIの吹き出し */
    .stChatMessage[data-testid="assistant"] {
        background-color: #000000;
        border: 1px solid #333;
        border-radius: 15px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- APIキー ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Key Missing")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI関数 ---
def call_science_model(client, prompt, image=None, role="solver"):
    try:
        sys_instruction = "あなたは科学技術計算AIです。数式は$$を使用し、論理的かつ簡潔に答えてください。"
        if role == "judge":
            sys_instruction = "あなたは査読者です。複数の回答を統合し、完璧な最終回答を作成してください。"
        
        contents = [prompt, image] if image else prompt
        res = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=contents,
            config={"system_instruction": sys_instruction}
        )
        return res.text.strip()
    except:
        return None

# --- サイドバー ---
with st.sidebar:
    st.title("⚛️ Sci-Core")
    st.caption("Autonomous Reasoning System")
    
    st.markdown("---")
    # 画像アップロードをサイドバーに隠してスッキリさせる
    st.markdown("### 📎 画像解析")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"], label_visibility="collapsed")
    
    st.markdown("---")
    if st.button("🗑️ 履歴クリア", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
st.markdown("## ⚛️ Sci-Core AI Project")
st.caption("Multi-Agent Reasoning Engine")

# チャット履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"]:
            st.image(message["image"], width=250)
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 思考プロセス (3機のAIによる推論)"):
                st.markdown(message["details"])

# --- 入力エリア (最新のチャットインターフェース) ---
# これがスマホでも使いやすい「送信ボタン付き」の入力欄です
prompt = st.chat_input("質問を入力... (Shift+Enterで改行)")

if prompt:
    # 画像の処理
    image = Image.open(uploaded_file) if uploaded_file else None
    
    # ユーザー表示
    with st.chat_message("user"):
        if image: st.image(image, width=250)
        st.markdown(prompt)
    
    # 履歴保存
    msg_data = {"role": "user", "content": prompt}
    if image: msg_data["image"] = image
    st.session_state.messages.append(msg_data)
    
    # AI処理
    with st.chat_message("assistant"):
        status = st.empty()
        status.markdown("`⚡ Sci-Core is thinking...`")
        
        # 並列処理風の演出
        res_a = call_science_model(client, prompt, image, "solver")
        res_b = call_science_model(client, prompt, image, "solver")
        
        status.markdown("`👨‍⚖️ Judge is verifying...`")
        
        judge_prompt = f"質問: {prompt}\n回答A: {res_a}\n回答B: {res_b}\nこれらを統合し、洗練された回答を作成せよ。"
        final_answer = call_science_model(client, judge_prompt, None, "judge")
        
        if final_answer:
            status.empty()
            st.markdown(final_answer)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_answer,
                "details": f"**Core A:** {res_a}\n\n**Core B:** {res_b}"
            })
        else:
            status.error("System Error")
