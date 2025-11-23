import streamlit as st
import time
import re
from google import genai
from PIL import Image

# --- 1. ページ設定 ---
st.set_page_config(page_title="Sci-Core AI", page_icon="⚛️", layout="wide")

# 強制ダークモード & スマホ最適化 & デザイン
st.markdown("""
<style>
    .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }
    .stChatInput textarea { background-color: #262730 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #161B22 !important; }
    body, p, div, span, h1, h2, h3, li { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }
    .katex { color: #58A6FF !important; font-size: 1.2em !important; }
    .stButton button { background-color: #238636; color: white !important; font-weight: bold; border: none; }
    
    /* 画像アップローダーの枠線を見やすく */
    [data-testid="stFileUploader"] {
        padding: 10px;
        border: 1px dashed #4E5359;
        border-radius: 10px;
        background-color: #161B22;
    }
</style>
""", unsafe_allow_html=True)

# --- APIキー ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 エラー: APIキー設定が必要です")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI脳みそ (画像対応) ---
def call_science_model(client, prompt, image=None, role="solver"):
    try:
        if role == "solver":
            sys_instruction = """
            あなたは世界最高峰の科学技術計算AIです。
            数式は必ず `$$` で囲み、`\\begin{align}` は使用しないでください。
            画像が与えられた場合は、その画像内の数式や現象を解析してください。
            暗算禁止。途中式を丁寧に書いてください。
            """
        else: # Judge
            sys_instruction = """
            あなたは厳格な査読者です。
            3つのAIの回答を比較し、最も正確で分かりやすい最終回答を作成してください。
            """
        
        if image:
            contents = [prompt, image]
        else:
            contents = prompt
            
        res = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=contents,
            config={"system_instruction": sys_instruction}
        )
        return res.text.strip()
    except:
        return None

# --- サイドバー (ステータス表示のみ) ---
with st.sidebar:
    st.title("⚛️ Sci-Core AI")
    st.caption("v3.2 Open Edition")
    
    # かっこいいステータスモニター
    st.markdown("### 🖥️ System Status")
    col1, col2, col3 = st.columns(3)
    col1.metric("Core A", "🟢")
    col2.metric("Core B", "🟢")
    col3.metric("Core C", "🟢")
    st.success("👨‍⚖️ Judge System: Active")
    
    st.markdown("---")
    st.info("📸 画像解析モジュール搭載")
    
    if st.button("🗑️ 履歴を消去", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
st.title("👁️ Sci-Core Lens")
st.markdown("#### 画像解析 × 超高精度計算")

# 履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message:
            st.image(message["image"], width=250)
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 解析プロセス"):
                st.markdown(message["details"])

# --- 入力エリア ---
# 画像アップロード
uploaded_file = st.file_uploader("📸 画像をアップロード (数式、グラフ、図など)", type=["jpg", "png", "jpeg"])
# 質問入力
question = st.chat_input("質問を入力 (例: この数式を解いて)...")

if question:
    # 画像の処理
    image = None
    if uploaded_file:
        image = Image.open(uploaded_file)
    
    # ユーザーの投稿を表示
    with st.chat_message("user"):
        if image:
            st.image(image, width=250)
        st.markdown(question)
    
    # 履歴に保存
    msg_data = {"role": "user", "content": question}
    if image: msg_data["image"] = image
    st.session_state.messages.append(msg_data)

    # AIの処理
    with st.chat_message("assistant"):
        status = st.empty()
        status.info("⚡ 3つのAIが解析中...")
        
        # 1. ソルバー実行
        res_a = call_science_model(client, question, image, "solver")
        res_b = call_science_model(client, question, image, "solver")
        res_c = call_science_model(client, question, image, "solver")
        
        ans_a = res_a if res_a else "Error"
        ans_b = res_b if res_b else "Error"
        ans_c = res_c if res_c else "Error"
        
        # 2. 査読
        status.info("👨‍⚖️ 査読中...")
        
        log_text = f"**A:** {ans_a}\n**B:** {ans_b}\n**C:** {ans_c}"

        judge_prompt = f"""
        ユーザーの質問: {question}
        【回答A】{ans_a}
        【回答B】{ans_b}
        【回答C】{ans_c}
        
        上記を統合し、正しい回答を作成せよ。数式は$$を使用せよ。
        """
        
        final_answer = call_science_model(client, judge_prompt, None, "judge")
        
        if final_answer:
            status.empty()
            st.markdown(final_answer)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_answer, 
                "details": log_text
            })
        else:
            status.error("解析失敗")
