import streamlit as st
import re
import unicodedata
import time
from google import genai

# --- ページ設定 ---
st.set_page_config(page_title="Zombie AI Enterprise", page_icon="🛡️", layout="wide")

# --- APIキー ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 エラー: Secrets設定が必要です")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 関数 ---
def call_ai_robust(client, model, prompt, retries=3):
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
    st.title("🛡️ Zombie AI")
    st.caption("v4.0 Strict Enterprise")
    
    st.markdown("---")
    st.warning("⚠️ Strict Mode: Active")
    st.caption("不確実な情報は一切排除されます。")
    
    if st.button("🗑️ リセット", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
st.title("🛡️ Zombie AI System")
st.caption("「推測」ではなく「確実性」のみを提供する産業用モデル。")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 監査ログ"):
                st.markdown(message["details"])

question = st.chat_input("質問を入力...")

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        status = st.empty()
        status.info("⚡ Tier 1: Flashモデルによる並列監査中...")
        
        # 1. Flash実行
        res_a = call_ai_robust(client, "gemini-2.0-flash", f"{question} (簡潔に)")
        res_c = call_ai_robust(client, "gemini-2.0-flash", f"{question} (簡潔に)")
        
        text_a = res_a if res_a else "Error"
        text_c = res_c if res_c else "Error"
        
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
                log_text += "✅ **Audit Passed:** 意見一致 (Tier 1採用)"
        
        # 3. 分岐
        if match:
            status.empty()
            st.success("✅ 承認されました")
            st.markdown(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer, "details": log_text})
        
        else:
            status.warning("🚨 意見不一致を検知。最高権限(Pro)による裁定を要求中...")
            log_text += "🚨 **Alert:** 不一致検知 -> Proモデル承認待ち\n\n"
            
            # Pro呼び出し
            res_pro = call_ai_robust(client, "gemini-2.0-pro-exp-02-05", f"{question} (専門家として厳密に)")
            
            status.empty()
            
            if res_pro:
                # Pro成功
                st.success("🏆 最高権限による承認完了")
                st.markdown(res_pro)
                log_text += f"**🏆 Pro Decision:** {res_pro}"
                st.session_state.messages.append({"role": "assistant", "content": res_pro, "details": log_text})
            
            else:
                # 💀 Pro失敗 -> ここが企業向けポイント
                # 適当な答えを出さず、システムをロックする
                error_message = """
                ⛔ **SYSTEM HALTED: 信頼性担保不能**
                
                Tier 1での意見不一致に対し、Tier 2(Pro)による裁定を試みましたが、
                API応答制限により確実な検証ができませんでした。
                
                本システムは「不確実な回答」によるリスクを回避するため、
                回答出力を拒否しました。しばらく待って再試行してください。
                """
                
                st.error(error_message)
                log_text += "⛔ **CRITICAL:** 監査プロセス未完了のため出力拒否"
                
                st.session_state.messages.append({"role": "assistant", "content": error_message, "details": log_text})
