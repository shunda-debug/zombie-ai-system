import streamlit as st
import time
import re
from google import genai

# --- 1. ページ設定 ---
st.set_page_config(page_title="Sci-Core AI", page_icon="⚛️", layout="wide")

# --- 2. デザイン強制注入 (Force Dark Mode) ---
st.markdown("""
<style>
    /* =================================
       1. 強制ダークモード設定
       ================================= */
    /* 全体の背景を黒にする */
    .stApp {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }
    
    /* ヘッダー（上のバー）も黒くする */
    header[data-testid="stHeader"] {
        background-color: #0E1117 !important;
    }

    /* =================================
       2. サイドバーを見えるようにする
       ================================= */
    /* サイドバーの背景色 */
    [data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D;
    }
    
    /* 【重要】サイドバーを開くボタン（>）を白くする */
    [data-testid="collapsedControl"] {
        color: #FFFFFF !important;
    }
    
    /* スマホでサイドバーを閉じる「X」ボタンも白くする */
    button[kind="header"] {
        color: #FFFFFF !important;
    }

    /* =================================
       3. 文字と入力欄の視認性アップ
       ================================= */
    /* 全ての文字を白く、太く */
    body, p, div, span, label, h1, h2, h3, h4, h5, h6, li {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important; /* スマホ用強制白 */
    }

    /* 入力欄（チャット）の背景をグレーに */
    .stChatInput textarea {
        background-color: #262730 !important;
        color: #FFFFFF !important;
        caret-color: #FFFFFF !important; /* カーソル */
        border: 1px solid #4E5359 !important;
    }
    
    /* チャットメッセージの箱 */
    .stChatMessage {
        background-color: #1E2329 !important;
        border: 1px solid #30363D;
    }

    /* 数式（LaTeX）を青く光らせる */
    .katex {
        color: #58A6FF !important;
        font-size: 1.2em !important;
    }

    /* ボタンのデザイン */
    .stButton button {
        background-color: #238636;
        color: white !important;
        font-weight: bold;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- APIキー ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 APIキー設定が必要です")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 履歴管理 ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI脳みそ ---
def call_science_model(client, prompt, role="solver"):
    try:
        if role == "solver":
            sys_instruction = """
            あなたは世界最高峰の科学技術計算AIです。
            数式は必ず `$$` で囲み、`\\begin{align}` は使用しないでください。
            暗算禁止。途中式を丁寧に書き、単位を正確に記述してください。
            """
        else: # Judge
            sys_instruction = """
            あなたは厳格な数学査読者です。
            3つの回答を比較し、最も正確で分かりやすい最終回答を作成してください。
            `\\begin{align}` は使用禁止。すべての数式は `$$` または `$` で囲んでください。
            """
        
        res = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt,
            config={"system_instruction": sys_instruction}
        )
        return res.text.strip()
    except:
        return None

# --- サイドバー ---
with st.sidebar:
    st.title("⚛️ Sci-Core AI")
    st.caption("v2.4 Dark Mode Force")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("A", "🟢")
    col2.metric("B", "🟢")
    col3.metric("C", "🟢")
    
    st.markdown("---")
    
    # 新しい会話ボタン
    if st.button("➕ 新しい会話", use_container_width=True):
        if st.session_state.messages:
            summary = st.session_state.messages[0]["content"][:15] + "..." if st.session_state.messages else "No Data"
            st.session_state.chat_history.append({"title": summary, "log": st.session_state.messages})
        st.session_state.messages = []
        st.rerun()

    st.markdown("### 📚 History")
    if st.session_state.chat_history:
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"📝 {chat['title']}"):
                for msg in chat["log"]:
                    st.text(f"{msg['role']}: {msg['content']}")
    else:
        st.caption("履歴なし")

# --- メイン画面 ---
st.title("⚛️ Sci-Core Solver")
st.markdown("#### 理系特化・高精度計算AI")

# 履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 計算プロセス"):
                st.markdown(message["details"])

# 質問入力
question = st.chat_input("質問を入力...")

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        status = st.empty()
        status.info("⚡ 3つのAIが並列計算中...")
        
        # 1. ソルバー実行
        res_a = call_science_model(client, question, "solver")
        res_b = call_science_model(client, question, "solver")
        res_c = call_science_model(client, question, "solver")
        
        ans_a = res_a if res_a else "Error"
        ans_b = res_b if res_b else "Error"
        ans_c = res_c if res_c else "Error"
        
        # 2. 査読
        status.info("👨‍⚖️ 査読者が検算中...")
        
        log_text = f"""
        **Solver A:** {ans_a}
        **Solver B:** {ans_b}
        **Solver C:** {ans_c}
        """

        # 3. 最終回答
        judge_prompt = f"""
        【問題】{question}
        【解法A】{ans_a}
        【解法B】{ans_b}
        【解法C】{ans_c}
        
        上記を統合し、正しい計算結果を回答してください。
        数式は必ず `$$` で囲み、align環境は使わないでください。
        """
        
        final_answer = call_science_model(client, judge_prompt, "judge")
        
        if final_answer:
            status.empty()
            st.markdown(final_answer)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_answer, 
                "details": log_text
            })
        else:
            status.error("💀 計算失敗")
