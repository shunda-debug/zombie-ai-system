import streamlit as st
import time
import re
from google import genai

# --- 1. ページ設定 & デザイン注入（スマホ完全対応版） ---
st.set_page_config(page_title="Sci-Core AI", page_icon="⚛️", layout="wide")

st.markdown("""
<style>
    /* 全体の背景と基本フォント設定 */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF !important;
    }
    
    /* スマホ対策: 入力欄の色を強制的にダークにする */
    .stChatInput textarea {
        background-color: #161B22 !important; /* 背景を濃いグレーに */
        color: #FFFFFF !important; /* 文字を白に */
        caret-color: #FFFFFF !important; /* カーソルも白に */
    }
    /* 入力欄のコンテナ自体も黒く */
    div[data-testid="stChatInput"] {
        background-color: #0E1117 !important;
    }

    /* 文字を全体的にくっきりさせる */
    body, p, div, span, label, h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        -webkit-font-smoothing: antialiased;
    }

    /* チャットメッセージの箱 */
    .stChatMessage {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 15px;
    }

    /* 数式（LaTeX）の設定 */
    .katex {
        font-size: 1.3em !important;
        color: #58A6FF !important;
    }

    /* サイドバー */
    [data-testid="stSidebar"] {
        background-color: #010409;
        border-right: 1px solid #30363D;
    }
    
    /* ボタン */
    .stButton button {
        background-color: #238636;
        color: white !important;
        border-radius: 5px;
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

# --- 2. 履歴管理システム ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # 過去のセッションを保存するリスト

if "messages" not in st.session_state:
    st.session_state.messages = [] # 現在の会話

# --- 3. 理系特化の脳みそ ---
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
    st.caption("v2.3 History & Mobile")
    
    # ステータス表示
    col1, col2, col3 = st.columns(3)
    col1.metric("A", "🟢")
    col2.metric("B", "🟢")
    col3.metric("C", "🟢")
    
    st.markdown("---")
    
    # 🆕 新しい会話ボタン（履歴に保存してからリセット）
    if st.button("➕ 新しい会話を始める", use_container_width=True):
        if st.session_state.messages:
            # 現在の会話を履歴リストに保存
            summary = st.session_state.messages[0]["content"][:20] + "..." if st.session_state.messages else "No Data"
            st.session_state.chat_history.append({"title": summary, "log": st.session_state.messages})
        # 現在の会話をクリア
        st.session_state.messages = []
        st.rerun()

    st.markdown("### 📚 過去の会話履歴")
    if not st.session_state.chat_history:
        st.caption("履歴はありません")
    else:
        # 過去の会話をアコーディオンで表示
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"📝 {chat['title']}"):
                for msg in chat["log"]:
                    st.text(f"{msg['role']}: {msg['content']}")

    st.info("💡 スマホの方は、左上の「>」または「≡」を押すとこのメニューが開きます。")

# --- メイン画面 ---
st.title("⚛️ Sci-Core Solver")
st.markdown("#### 究極の計算精度と、美しい数式表示。")

# 現在の履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 計算プロセスを見る"):
                st.markdown(message["details"])

# 質問入力
question = st.chat_input("数式、物理法則、計算問題を入力...")

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        status = st.empty()
        status.info("⚡ 3つのAI脳が並列演算中...")
        
        # 1. ソルバー実行
        res_a = call_science_model(client, question, "solver")
        res_b = call_science_model(client, question, "solver")
        res_c = call_science_model(client, question, "solver")
        
        ans_a = res_a if res_a else "計算エラー"
        ans_b = res_b if res_b else "計算エラー"
        ans_c = res_c if res_c else "計算エラー"
        
        # 2. 査読
        status.info("👨‍⚖️ 査読者が数式を整形・検算中...")
        
        log_text = f"""
        **Solver A:** {ans_a}
        **Solver B:** {ans_b}
        **Solver C:** {ans_c}
        """

        # 3. 最終回答生成
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
            status.error("💀 計算処理に失敗しました")
