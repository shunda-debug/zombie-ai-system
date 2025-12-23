import streamlit as st
import requests
import json
import concurrent.futures

# --- 1. ページ設定 ---
st.set_page_config(page_title="Sci-Core", page_icon="⚛️", layout="wide")

# --- 2. デザイン (Dark Minimal) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .stChatInputContainer { background-color: #0E1117; border-top: 1px solid #333; }
    .stChatMessage[data-testid="user"] { background-color: #262730; border: none; }
    .stChatMessage[data-testid="assistant"] { background-color: transparent; border: none; }
    .streamlit-expanderHeader { background-color: #161B22; color: #888; font-size: 0.9em; border-radius: 5px; }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- APIキー設定 ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 エラー: SecretsにAPIキーが設定されていません。")
    st.stop()

# --- 履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI脳みそ (直接HTTP通信版 - ライブラリ不要) ---
def call_ai_direct(prompt, role):
    # エンドポイントURL (Gemini 1.5 Flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # 役割ごとのシステムプロンプト
    if role == "A":
        sys_msg = "あなたは肯定的なドリーマーです。制限を無視して理想的なアイデアを出してください。"
    elif role == "B":
        sys_msg = "あなたは批判的なリアリストです。現実的なリスクや欠陥を指摘してください。"
    else:
        sys_msg = "あなたは調整役です。AとBの意見を統合し、最適な結論を出してください。"

    # リクエストの中身（JSON）
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "systemInstruction": {
            "parts": [{"text": sys_msg}]
        }
    }
    
    headers = {'Content-Type': 'application/json'}

    try:
        # 直接POSTリクエストを送信
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 結果の解析
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            return f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"通信エラー: {str(e)}"

# --- 並列処理関数 ---
def run_parallel_thinking(prompt):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_a = executor.submit(call_ai_direct, prompt, "A")
        future_b = executor.submit(call_ai_direct, prompt, "B")
        return future_a.result(), future_b.result()

# --- サイドバー ---
with st.sidebar:
    st.title("⚛️ Sci-Core")
    st.caption("Direct-Link Protocol v6.0")
    if st.button("New Chat", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "thoughts" in message:
            with st.expander("✨ Thoughts"):
                st.markdown(message["thoughts"])

# --- 入力エリア ---
prompt = st.chat_input("質問を入力...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        status_box = st.status("Thinking...", expanded=True)
        
        status_box.write("⚡ Dreamer & Critic are debating...")
        res_a, res_b = run_parallel_thinking(prompt)
        
        status_box.write("👨‍⚖️ Judge is synthesizing...")
        judge_input = f"質問:{prompt}\n案A:{res_a}\n案B:{res_b}\n統合して結論を出せ。"
        final_answer = call_ai_direct(judge_input, "C")
        
        status_box.update(label="Complete", state="complete", expanded=False)
        
        st.markdown(final_answer)
        
        thoughts_log = f"**🚀 Agent A:**\n{res_a}\n\n---\n**🛡️ Agent B:**\n{res_b}"
        with st.expander("✨ Thoughts"):
            st.markdown(thoughts_log)
            
        st.session_state.messages.append({
            "role": "assistant", 
            "content": final_answer, 
            "thoughts": thoughts_log
        })
