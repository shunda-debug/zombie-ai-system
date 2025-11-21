import streamlit as st
import re
import unicodedata
import time
from google import genai

# --- ページ設定 ---
st.set_page_config(page_title="Zombie AI", page_icon="🧟", layout="wide")

# --- APIキー ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 エラー: Secrets設定が必要です")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 関数 ---
def call_ai_robust(client, model, prompt, retries=2):
    # Proモデルの時はリトライ回数を減らす（待たせすぎないため）
    for i in range(retries):
        try:
            res = client.models.generate_content(model=model, contents=prompt)
            return res.text.strip()
        except:
            time.sleep(1)
    return None

def get_integer(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^0-9.]', '', text)
    if '.' in text: text = text.split('.')[0]
    return text

# --- サイドバー ---
with st.sidebar:
    st.title("🧟 Zombie AI")
    st.caption("v3.5 Honest Architecture")
    if st.button("🗑️ 会話をリセット", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
st.title("💬 Zombie AI Chat")
st.caption("信頼性第一。判定不能な場合は正直に両論を表示します。")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # もし「喧嘩両成敗モード」のログなら、左右に分けて表示
        if message.get("type") == "split":
            st.warning("⚠️ Proモデル応答なしのため、両論を併記します")
            col1, col2 = st.columns(2)
            with col1:
                st.info("🤖 Flash Aの意見")
                st.markdown(message["content_a"])
            with col2:
                st.info("🤖 Flash Cの意見")
                st.markdown(message["content_c"])
        else:
            st.markdown(message["content"])
        
        if "details" in message:
            with st.expander("🔍 思考ログ"):
                st.markdown(message["details"])

question = st.chat_input("質問を入力...")

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        status = st.empty()
        status.info("⚡ 思考中... (Flash並列計算)")
        
        # 1. Flash実行
        res_a = call_ai_robust(client, "gemini-2.0-flash", f"{question} (簡潔に)")
        res_c = call_ai_robust(client, "gemini-2.0-flash", f"{question} (簡潔に)")
        
        text_a = res_a if res_a else "エラー"
        text_c = res_c if res_c else "エラー"
        
        match = False
        final_answer = ""
        log_text = f"**Flash A:** {text_a}\n\n**Flash C:** {text_c}\n\n"

        # 2. 判定
        if res_a and res_c:
            num_a = get_integer(res_a)
            num_c = get_integer(res_c)
            if (num_a and num_c and num_a == num_c) or (res_a == res_c):
                match = True
                final_answer = res_a
                log_text += "✅ **判定:** 一致 (Tier 1採用)"
        
        # 3. 分岐
        if match:
            # 一致ならそのまま表示
            status.empty()
            st.markdown(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer, "details": log_text})
        
        else:
            status.warning("🚨 意見不一致。Proモデルを呼び出し中...")
            log_text += "🚨 **判定:** 不一致 -> Proモデル起動\n\n"
            
            res_pro = call_ai_robust(client, "gemini-2.0-pro-exp-02-05", f"{question} (専門家として厳密に)")
            
            status.empty()
            
            if res_pro:
                # Pro成功
                st.markdown(res_pro)
                log_text += f"**🏆 Pro Answer:** {res_pro}"
                st.session_state.messages.append({"role": "assistant", "content": res_pro, "details": log_text})
            
            else:
                # 💀 Pro失敗 -> 正直に「左右分割」で表示！
                st.warning("⚠️ Proモデルが混雑しているため、判定を保留しました。")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info("🤖 Flash Aの意見")
                    st.markdown(text_a)
                with col2:
                    st.info("🤖 Flash Cの意見")
                    st.markdown(text_c)
                
                log_text += "💀 **Pro Status:** 応答なし\n🛡️ **Fallback:** 両論併記モード"
                
                # 履歴には「特殊な形式」で保存する
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "split", # ここが目印
                    "content_a": text_a,
                    "content_c": text_c,
                    "content": "（両論併記を表示中）", # ログ用テキスト
                    "details": log_text
                })
