import streamlit as st
from google import genai
from PIL import Image

# --- 1. ページ設定 ---
st.set_page_config(page_title="Sci-Core AI", page_icon="⚛️", layout="wide")

# --- 2. デザイン (Dark Mode & UI調整) ---
st.markdown("""
<style>
    /* 全体をダークモードに固定 */
    .stApp {
        background-color: #0E1117 !important;
        color: #E0E0E0 !important;
    }
    
    /* 入力エリアの背景色 */
    .stTextArea textarea {
        background-color: #262730 !important;
        color: #FFFFFF !important;
        border: 1px solid #4E5359;
    }
    
    /* 送信ボタンを緑色にして目立たせる */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #238636;
        color: white !important;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    
    /* 数式の文字色 */
    .katex { color: #4DA6FF !important; font-size: 1.1em !important; }
</style>
""", unsafe_allow_html=True)

# --- APIキー ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 エラー: SecretsにAPIキーが設定されていません。")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI関数 (エラー詳細表示付き) ---
def call_science_model(client, prompt, image=None, role="solver"):
    try:
        # 役割定義
        if role == "solver":
            sys_instruction = "あなたは科学技術計算AIです。数式は$$を使用し、論理的かつ簡潔に答えてください。"
        else:
            sys_instruction = "あなたは査読者です。複数の回答を統合し、完璧な最終回答を作成してください。"
        
        # 画像がある場合とない場合で分岐
        contents = [prompt, image] if image else prompt
        
        # モデルを安定版(1.5-flash)に固定
        res = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=contents,
            config={"system_instruction": sys_instruction}
        )
        return res.text.strip()
    except Exception as e:
        # エラーの正体を返す
        return f"ERROR: {str(e)}"

# --- サイドバー ---
with st.sidebar:
    st.title("⚛️ Sci-Core")
    st.caption("v4.1 Stable Edition")
    
    st.success("🟢 System: Online")
    
    st.markdown("---")
    # リセットボタン
    if st.button("🗑️ 会話をリセット", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
st.title("⚛️ Sci-Core AI Project")

# 履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"]:
            st.image(message["image"], width=250)
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 思考プロセス"):
                st.markdown(message["details"])

# --- 入力エリア (フォーム形式に戻しました) ---
st.markdown("---")

with st.form(key="chat_form", clear_on_submit=True):
    # スマホでも改行しやすいテキストエリア
    user_input = st.text_area("質問を入力...", height=100, placeholder="スマホなら「改行」で次の行へ。送信はボタンで。")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        # 画像アップロード
        uploaded_file = st.file_uploader("画像", type=["jpg", "png"], label_visibility="collapsed")
    with col2:
        # 送信ボタン (これが欲しかったやつです！)
        submit_btn = st.form_submit_button("🚀 送信 (Analyze)")

# --- 処理実行 ---
if submit_btn and user_input:
    # 画像処理
    image = Image.open(uploaded_file) if uploaded_file else None
    
    # ユーザー表示
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
        status.info("Sci-Core is thinking...")
        
        # Solver実行
        res_a = call_science_model(client, user_input, image, "solver")
        res_b = call_science_model(client, user_input, image, "solver")
        
        # もしエラーが返ってきていたら表示する
        if "ERROR:" in res_a:
            status.error(f"通信エラーが発生しました: {res_a}")
        else:
            status.info("Judge is verifying...")
            judge_prompt = f"質問: {user_input}\n回答A: {res_a}\n回答B: {res_b}\nこれらを統合し、回答せよ。"
            final_answer = call_science_model(client, judge_prompt, None, "judge")
            
            if final_answer and "ERROR:" not in final_answer:
                status.empty()
                st.markdown(final_answer)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": final_answer,
                    "details": f"**Core A:** {res_a}\n\n**Core B:** {res_b}"
                })
            else:
                status.error(f"最終判定でエラー: {final_answer}")
    
    # 処理が終わったらリロードして表示を更新
    st.rerun()
