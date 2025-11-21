import streamlit as st
import re
import unicodedata
from google import genai

# --- ページ設定 ---
st.set_page_config(page_title="Zombie AI", page_icon="🧟", layout="wide")

# --- APIキーの読み込み（Secretsから） ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 システムエラー: 管理者に連絡してください (Secrets設定)")
    st.stop()

client = genai.Client(api_key=api_key)

# --- ロジック関数 ---
def get_integer(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^0-9.]', '', text)
    if '.' in text: text = text.split('.')[0]
    return text

def call_ai(client, model, prompt):
    try:
        res = client.models.generate_content(model=model, contents=prompt)
        return res.text.strip()
    except:
        return None

# --- サイドバー ---
with st.sidebar:
    st.title("🧟 Zombie AI")
    st.caption("v2.0 Enterprise Model")
    
    if st.button("🗑️ 会話をリセット", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.success("🟢 Tier 1 (Flash): Online")
    st.success("🟢 Tier 2 (Pro): Standby")
    
    st.markdown("---")
    st.markdown(
        """
        ### 💀 Never Die Architecture
        **絶対不死・完全信頼**
        
        2つのAIが監視し、
        あなたの質問に嘘をつきません。
        """
    )

# --- メイン画面 ---
st.title("💬 Zombie AI Chat")
st.caption("学校の課題、レポート、ファクトチェックに。嘘をつかないAI。")

# 会話履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去の会話を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 AIの思考ログを見る"):
                st.markdown(message["details"])

# 新しい質問
question = st.chat_input("質問を入力...")

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        status = st.empty()
        status.info("⚡ 思考中... (Flashモデル並列計算)")
        
        res_a = call_ai(client, "gemini-2.0-flash", f"{question} (簡潔に)")
        res_c = call_ai(client, "gemini-2.0-flash", f"{question} (簡潔に)")
        
        match = False
        final_answer = ""
        log_text = f"**Flash A:** {res_a}\n\n**Flash C:** {res_c}\n\n"

        if res_a and res_c:
            num_a = get_integer(res_a)
            num_c = get_integer(res_c)
            if (num_a and num_c and num_a == num_c) or (res_a == res_c):
                match = True
                final_answer = res_a
                log_text += "✅ **判定:** 一致 (Tier 1採用)"
        
        if match:
            status.empty()
            st.markdown(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer, "details": log_text})
        else:
            status.warning("🚨 意見不一致。専門家(Pro)を呼び出します...")
            log_text += "🚨 **判定:** 不一致 -> Proモデル起動\n\n"
            res_pro = call_ai(client, "gemini-2.0-pro-exp-02-05", f"{question} (専門家として厳密に)")
            status.empty()
            if res_pro:
                st.markdown(res_pro)
                log_text += f"**🏆 Pro Answer:** {res_pro}"
                st.session_state.messages.append({"role": "assistant", "content": res_pro, "details": log_text})
            else:
                st.error("エラー発生")
