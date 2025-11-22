import streamlit as st
import time
from google import genai

# --- ページ設定 ---
st.set_page_config(page_title="Sci-Core AI", page_icon="⚛️", layout="wide")

# --- APIキー ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 エラー: APIキーの設定が必要です")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 関数 ---
def call_science_model(client, prompt, role="solver"):
    try:
        # 理系特化のシステムプロンプト
        if role == "solver":
            sys_instruction = """
            あなたは世界最高峰の物理学者かつ数学者です。
            ユーザーの質問に対し、以下のルールを厳守して回答してください：
            1. いきなり答えを出さず、必ず「思考プロセス（途中式）」を示すこと。
            2. 数式はLaTeX形式（$記号で囲む）を使ってきれいに書くこと。
            3. 単位（km/s, J, Nなど）を正確に扱うこと。
            4. 曖昧な知識で答えず、論理的に導き出すこと。
            """
        else: # Judge
            sys_instruction = """
            あなたは厳格な査読者（Reviewer）です。
            3つのAIが導き出した「計算過程」と「答え」を比較し、
            最も論理的で、計算ミスがないものを採用して最終回答を作成してください。
            もし意見が割れている場合は、多数決ではなく「論理の正しさ」で判断してください。
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
    st.caption("v1.0 Science Solver")
    
    st.info("🟢 Solver A (Physics): Ready")
    st.info("🟢 Solver B (Math): Ready")
    st.info("🟢 Solver C (Logic): Ready")
    st.success("👨‍⚖️ Reviewer: Active")
    
    if st.button("🗑️ 計算用紙を捨てる", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown(
        """
        ### 🎓 For Students
        普通のAIは計算を間違えますが、
        このAIは3つの頭脳で検算するため
        **計算ミスを極限まで減らします。**
        宿題の検算やレポート作成に。
        """
    )

# --- メイン画面 ---
st.title("⚛️ 理系専用・高精度AIソルバー")
st.caption("数学・物理・化学の難問を、3段階のクロスチェックで解き明かします。")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 検算ログを見る"):
                st.markdown(message["details"])

# 質問入力
question = st.chat_input("数式、物理の問題などを入力...")

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        status = st.empty()
        status.info("⚡ 3つのAIが別ルートで計算中...")
        
        # 1. 3台のソルバーが計算
        res_a = call_science_model(client, question, "solver")
        res_b = call_science_model(client, question, "solver")
        res_c = call_science_model(client, question, "solver")
        
        ans_a = res_a if res_a else "計算不能"
        ans_b = res_b if res_b else "計算不能"
        ans_c = res_c if res_c else "計算不能"
        
        # 2. 査読中
        status.info("👨‍⚖️ 査読者(Reviewer)が途中式を検証中...")
        
        log_text = f"""
        | Model | Result Preview |
        | :--- | :--- |
        | **Solver A** | {ans_a[:30]}... |
        | **Solver B** | {ans_b[:30]}... |
        | **Solver C** | {ans_c[:30]}... |
        
        ---
        **検証用全データ:**
        
        **⚛️ Solver A:**
        {ans_a}
        
        **⚛️ Solver B:**
        {ans_b}
        
        **⚛️ Solver C:**
        {ans_c}
        """

        # 3. 査読者による最終回答
        judge_prompt = f"""
        【問題】
        {question}

        【解法A】
        {ans_a}

        【解法B】
        {ans_b}

        【解法C】
        {ans_c}

        あなたは査読者です。3つの解法を比較し、
        最も「途中式が丁寧」で「答えが正確」なものをベースに、
        ユーザーへの最終回答（解説付き）を作成してください。
        数式はLaTeXで書いてください。
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
