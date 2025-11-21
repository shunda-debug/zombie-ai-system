import streamlit as st
import re
import unicodedata
import time
from google import genai

# --- ページ設定 ---
st.set_page_config(page_title="Zombie AI", page_icon="🧟", layout="wide")

# --- APIキー読み込み ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 エラー: Secrets設定が必要です。")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 関数: 頑丈なAI呼び出し (リトライ機能付き) ---
def call_ai_robust(client, model, prompt, retries=3):
    for i in range(retries):
        try:
            res = client.models.generate_content(model=model, contents=prompt)
            return res.text.strip()
        except Exception as e:
            # エラーが出たら少し待って再挑戦
            time.sleep(1) # 1秒待機
            if i == retries - 1: # 最後の挑戦でもダメなら
                print(f"Final Error in {model}: {e}")
                return None
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
    st.caption("v3.0 Stability Model")
    if st.button("🗑️ 会話をリセット", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.success("Auto-Retry: ON")

# --- メイン画面 ---
st.title("💬 Zombie AI Chat")
st.caption("アクセス集中時も自動で回避する高安定版。")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
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
        
        # 1. Flash実行 (リトライ付きで呼び出す)
        res_a = call_ai_robust(client, "gemini-2.0-flash", f"{question} (簡潔に)")
        res_c = call_ai_robust(client, "gemini-2.0-flash", f"{question} (簡潔に)")
        
        # 万が一Flashすら失敗した時の保険
        text_a = res_a if res_a else "読み込み失敗"
        text_c = res_c if res_c else "読み込み失敗"
        
        match = False
        final_answer = ""
        log_text = f"**Flash A:** {text_a}\n\n**Flash C:** {text_c}\n\n"

        # 2. 判定
        if res_a and res_c:
            num_a = get_integer(res_a)
            num_c = get_integer(res_c)
            # 数字一致 または 文章完全一致
            if (num_a and num_c and num_a == num_c) or (res_a == res_c):
                match = True
                final_answer = res_a
                log_text += "✅ **判定:** 一致 (Tier 1採用)"
        
        # 3. 結果表示またはPro呼び出し
        if match:
            status.empty()
            st.markdown(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer, "details": log_text})
        
        else:
            status.warning("🚨 意見不一致。Proモデルに接続試行中...")
            log_text += "🚨 **判定:** 不一致 -> Proモデル起動\n\n"
            
            # Pro呼び出し (ここもリトライ付き)
            res_pro = call_ai_robust(client, "gemini-2.0-pro-exp-02-05", f"{question} (専門家として厳密に)")
            
            status.empty()
            
            if res_pro:
                # Pro成功！
                st.markdown(res_pro)
                log_text += f"**🏆 Pro Answer:** {res_pro}"
                st.session_state.messages.append({"role": "assistant", "content": res_pro, "details": log_text})
            
            else:
                # Pro失敗...でもエラー画面にはしない！
                # Flash Aの回答を代わりに表示する (ここが安定の鍵)
                fallback = res_a if res_a else "申し訳ありません。現在アクセス集中により回答を生成できません。"
                
                st.warning("⚠️ Proモデルが混雑中。Flashモデルの回答を表示します。")
                st.markdown(fallback)
                
                log_text += "💀 **Pro Status:** 応答なし(混雑中)\n"
                log_text += "🛡️ **Safety Mode:** Flash Aの回答を採用"
                
                st.session_state.messages.append({"role": "assistant", "content": fallback, "details": log_text})
