import streamlit as st
import time
from google import genai

# --- ページ設定 ---
st.set_page_config(page_title="Zombie AI Quad", page_icon="⚖️", layout="wide")

# --- APIキー読み込み ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 エラー: SecretsにAPIキーを設定してください。")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 関数: 頑丈なAI呼び出し ---
def call_flash(client, prompt, role="analysis"):
    try:
        # 役割に応じてシステムプロンプトを変える
        sys_instruction = "あなたは簡潔に事実のみを答えるAIです。"
        if role == "judge":
            sys_instruction = "あなたは公平な裁判官です。提示された複数の回答を比較し、最も正確で論理的な最終回答を作成してください。"
        
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
    st.title("⚖️ Zombie AI")
    st.caption("v5.0 Quad-Core Architecture")
    
    st.info("🟢 Worker A: Online")
    st.info("🟢 Worker B: Online")
    st.info("🟢 Worker C: Online")
    st.success("👨‍⚖️ Judge: Active")
    
    if st.button("🗑️ リセット", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
st.title("⚖️ Zombie AI System")
st.caption("3台の実行部隊と1台の裁判官による、プロ不要の完全合議システム。")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 3者の意見と裁判記録を見る"):
                st.markdown(message["details"])

# 質問入力
question = st.chat_input("質問を入力...")

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        status = st.empty()
        status.info("⚡ 3台のFlashモデルが並列調査中...")
        
        # 1. 3台のワーカーが一斉に回答を作成
        # (Streamlitは基本直列ですが、Flashは高速なのでユーザーには一瞬に見えます)
        res_a = call_flash(client, question, "analysis")
        res_b = call_flash(client, question, "analysis")
        res_c = call_flash(client, question, "analysis")
        
        # エラーハンドリング（万が一失敗したらエラー表示）
        ans_a = res_a if res_a else "回答不能"
        ans_b = res_b if res_b else "回答不能"
        ans_c = res_c if res_c else "回答不能"
        
        # 2. 画面に3人の意見を表示（透明性）
        status.info("👨‍⚖️ 裁判官(Judge)が3つの意見を審議中...")
        
        # ログ用テキスト作成
        log_text = f"""
        | Model | Answer Summary |
        | :--- | :--- |
        | **Worker A** | {ans_a[:50]}... |
        | **Worker B** | {ans_b[:50]}... |
        | **Worker C** | {ans_c[:50]}... |
        
        ---
        **詳細な回答:**
        
        **🤖 Flash A:**
        {ans_a}
        
        **🤖 Flash B:**
        {ans_b}
        
        **🤖 Flash C:**
        {ans_c}
        """

        # 3. 裁判官による最終決定 (Judge Step)
        judge_prompt = f"""
        【ユーザーの質問】
        {question}

        【AI-Aの回答】
        {ans_a}

        【AI-Bの回答】
        {ans_b}

        【AI-Cの回答】
        {ans_c}

        【あなたの仕事】
        あなたは最高裁判官です。上記3つの回答を比較し、
        最も正確で、矛盾がなく、信頼できる「最終回答」を作成してください。
        もし3つの意見が食い違っている場合は、多数決の論理を用いて正解を導き出してください。
        回答は、ユーザーに対する返答のみを出力してください。
        """
        
        final_answer = call_flash(client, judge_prompt, "judge")
        
        if final_answer:
            status.empty()
            st.markdown(final_answer)
            
            # ログに裁判官のコメントを追加
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_answer, 
                "details": log_text
            })
        else:
            status.error("💀 裁判官が倒れました（システムエラー）")
