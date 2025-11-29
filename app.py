import streamlit as st
import time
from google import genai
from PIL import Image

# --- 1. ページ設定 ---
st.set_page_config(page_title="Sci-Core AI", page_icon="⚛️", layout="wide")

# --- 2. テーマ管理とCSS ---
# サイドバーでテーマ切り替え
with st.sidebar:
    st.title("⚛️ Sci-Core AI")
    st.caption("v3.3 Refined UI")
    
    # テーマ選択
    theme_mode = st.radio("🎨 Theme Color", ["Dark", "Light"], horizontal=True)

# CSSの動的生成
if theme_mode == "Dark":
    bg_color = "#0E1117"
    text_color = "#FFFFFF"
    input_bg = "#262730"
    border_color = "#4E5359"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    input_bg = "#F0F2F6"
    border_color = "#D0D0D0"

st.markdown(f"""
<style>
    /* 全体の背景と文字色 */
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    
    /* 文字色を強制適用（pタグやhタグなど） */
    p, h1, h2, h3, h4, h5, h6, li, span, div {{ color: {text_color} !important; }}
    
    /* 入力エリアのスタイル */
    .stTextArea textarea {{ background-color: {input_bg} !important; color: {text_color} !important; border: 1px solid {border_color}; }}
    
    /* サイドバーの背景 */
    [data-testid="stSidebar"] {{ background-color: {input_bg} !important; }}
    
    /* 数式の文字色（青系で統一） */
    .katex {{ color: #4B91F1 !important; font-size: 1.2em !important; }}
    
    /* 送信ボタンを目立たせる */
    div[data-testid="stFormSubmitButton"] button {{
        background-color: #238636; 
        color: white !important; 
        border: none;
        width: 100%;
    }}
    
    /* アップローダーを目立たなくスタイリッシュに */
    [data-testid="stFileUploader"] {{
        padding: 0px;
    }}
</style>
""", unsafe_allow_html=True)

# --- APIキー ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("⚠️ APIキーが設定されていません")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI脳みそ ---
def call_science_model(client, prompt, image=None, role="solver"):
    try:
        if role == "solver":
            sys_instruction = "あなたは科学技術計算AIです。数式は$$を使用し、途中式を丁寧に記述してください。"
        else: 
            sys_instruction = "あなたは査読者です。複数の回答を比較し、最適な最終回答を作成してください。"
        
        contents = [prompt, image] if image else prompt
        res = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=contents,
            config={"system_instruction": sys_instruction}
        )
        return res.text.strip()
    except:
        return None

# --- サイドバー (機能) ---
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🖥️ System Status")
    col1, col2, col3 = st.columns(3)
    col1.metric("A", "on-line")
    col2.metric("B", "on-line")
    col3.metric("C", "on-line")
    
    if st.button("🗑️ 履歴を消去"):
        st.session_state.messages = []
        st.rerun()

# --- メインチャット画面 ---
st.title("zombie-AI v1.1")

# チャット履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message:
            st.image(message["image"], width=250)
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 解析詳細"):
                st.markdown(message["details"])

# --- 新しい入力エリア (画面下部に固定) ---
st.markdown("---")
# フォームを使うことで「送信ボタンを押すまで送信されない」を実現
with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([8, 1])
    
    # テキスト入力エリア (Enterで改行される)
    user_input = st.text_area("質問を入力...", height=100, label_visibility="collapsed", placeholder="Ctrl+Enterで送信はできませんが、Enterで改行できます。")
    
    # 画像アップロードと送信ボタンを横並びっぽく配置
    c1, c2 = st.columns([1, 4])
    with c1:
        # アップロードボタン
        uploaded_file = st.file_uploader("📷 画像", type=["jpg", "png"], label_visibility="collapsed")
    with c2:
        # 送信ボタン
        submit_btn = st.form_submit_button("🚀 送信")

# --- 処理実行 ---
if submit_btn and user_input:
    image = Image.open(uploaded_file) if uploaded_file else None
    
    # ユーザー投稿表示
    with st.chat_message("user"):
        if image: st.image(image, width=250)
        st.markdown(user_input)
    
    # 履歴保存
    msg_data = {"role": "user", "content": user_input}
    if image: msg_data["image"] = image
    st.session_state.messages.append(msg_data)
    
    # AI処理
    with st.chat_message("assistant"):
        status = st.empty()
        status.info("⚡ Sci-Core Processing...")
        
        # Solver & Judge (簡易化のため直列処理に見せていますがロジックは維持)
        res_a = call_science_model(client, user_input, image, "solver")
        res_b = call_science_model(client, user_input, image, "solver")
        
        judge_prompt = f"質問: {user_input}\n回答A: {res_a}\n回答B: {res_b}\nこれらを統合して回答せよ。"
        final_answer = call_science_model(client, judge_prompt, None, "judge")
        
        if final_answer:
            status.empty()
            st.markdown(final_answer)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_answer,
                "details": f"**A:** {res_a}\n\n**B:** {res_b}"
            })
        else:
            status.error("Error occurred")
            
    st.rerun()
