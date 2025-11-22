import streamlit as st
import time
from google import genai

# --- 1. ページ設定 & デザイン注入 ---
st.set_page_config(page_title="Sci-Core AI", page_icon="⚛️", layout="wide")

# カスタムCSS（見た目を洗練させる魔法）
st.markdown("""
<style>
    /* 全体の背景とフォント */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* チャットの見た目 */
    .stChatMessage {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 15px;
    }
    /* 数式（LaTeX）を大きく綺麗に */
    .katex {
        font-size: 1.2em !important;
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
        color: white;
        border-radius: 5px;
        font-weight: bold;
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

# --- 2. 理系特化の脳みそ（プロンプト） ---
def call_science_model(client, prompt, role="solver"):
    try:
        if role == "solver":
            # 計算ミスを防ぎ、数式をきれいにする命令
            sys_instruction = """
            あなたは世界最高峰の科学技術計算AIです。
            ユーザーの質問に対し、以下のルールを絶対厳守してください。

            【ルール1：数式の美化】
            - 出力の数式はすべてLaTeX形式（$記号）で記述せよ。
            - 分数は `a/b` ではなく `\\frac{a}{b}` を使え。
            - 乗数は `^2` ではなく `^2` (上付き文字)としてレンダリングされるよう書け。
            - 積分やシグマも見やすく整形せよ。

            【ルール2：計算プロセスの厳格化】
            - 暗算は禁止する。複雑な計算はステップごとに分解せよ。
            - 単位（SI単位系）の変換に注意せよ。
            - 最終的な答えを出す前に、自分の計算が論理的に正しいか再確認せよ。
            """
        else: # Judge (Reviewer)
            sys_instruction = """
            あなたは厳格な数学査読者です。
            3つのAIの回答を比較し、以下の基準で最終回答を作成してください。
            1. 「計算結果」が一致しているか確認する。一致しない場合は再計算し、正しい方を採用する。
            2. 最も「数式が見やすく（LaTeX）」、「解説が丁寧」なものをベースにする。
            3. ユーザーへの回答は、教科書のように美しく整形された数式で出力する。
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
    st.caption("v2.0 Professional Design")
    
    st.markdown("### 📊 Status")
    col1, col2, col3 = st.columns(3)
    col1.metric("Solver A", "ON")
    col2.metric("Solver B", "ON")
    col3.metric("Solver C", "ON")
    
    st.markdown("---")
    if st.button("🗑️ 黒板を消す（リセット）", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.info("💡 ヒント: `x^2` や `sqrt(x)` と入力しても、AIは綺麗な数式 `$\\sqrt{x}$` に変換して返します。")

# --- メイン画面 ---
st.title("⚛️ Sci-Core Solver")
st.markdown("#### 究極の計算精度と、美しい数式表示。")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 履歴表示
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
        **Solver A Output:**
        {ans_a}
        
        **Solver B Output:**
        {ans_b}
        
        **Solver C Output:**
        {ans_c}
        """

        # 3. 最終回答生成
        judge_prompt = f"""
        【問題】{question}
        【解法A】{ans_a}
        【解法B】{ans_b}
        【解法C】{ans_c}
        
        上記を統合し、正しい計算結果と最も美しい数式表現を用いて回答してください。
        """
        
        final_answer = call_science_model(client, judge_prompt, "judge")
        
        if final_answer:
            status.empty()
            st.markdown(final_answer) # ここでLaTeXが綺麗に表示されます
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_answer, 
                "details": log_text
            })
        else:
            status.error("💀 計算処理に失敗しました")
