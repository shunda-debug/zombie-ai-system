import streamlit as st
import requests
import json
import concurrent.futures

st.set_page_config(page_title="Sci-Core", page_icon="⚛️", layout="wide")

# デザイン
st.markdown("""<style>.stApp { background-color: #0E1117; color: #E0E0E0; } .stChatInputContainer { background-color: #0E1117; } .stChatMessage[data-testid="user"] { background-color: #262730; } .stChatMessage[data-testid="assistant"] { background-color: transparent; } header {visibility: hidden;}</style>""", unsafe_allow_html=True)

# APIキー
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Key Error")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 【核心】ライブラリを使わず、直接URLを叩く関数 ---
def call_api_direct(prompt, role):
    # Googleの住所（エンドポイント）
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # 役割定義
    sys_msg = "あなたは優秀なAIです。"
    if role == "A": sys_msg = "あなたは肯定的なドリーマーです。"
    elif role == "B": sys_msg = "あなたは批判的なリアリストです。"
    elif role == "C": sys_msg = "あなたは統合する調整役です。"

    # 手紙の中身（JSON）
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": sys_msg}]}
    }

    try:
        # 送信！
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"通信エラー: {e}"

# 並列処理
def run_parallel(prompt):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        fa = executor.submit(call_api_direct, prompt, "A")
        fb = executor.submit(call_api_direct, prompt, "B")
        return fa.result(), fb.result()

# UI
with st.sidebar:
    st.title("⚛️ Sci-Core")
    st.caption("v6.0 Direct-REST")
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sub" in msg:
            with st.expander("Thoughts"): st.markdown(msg["sub"])

prompt = st.chat_input("質問を入力...")

if prompt:
    with st.chat_message("user"): st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        stat = st.status("Thinking...", expanded=True)
        stat.write("⚡ Discussing...")
        res_a, res_b = run_parallel(prompt)
        
        stat.write("👨‍⚖️ Synthesizing...")
        final = call_api_direct(f"質問:{prompt}\nA:{res_a}\nB:{res_b}\n統合せよ", "C")
        
        stat.update(label="Complete", state="complete", expanded=False)
        st.markdown(final)
        
        sub_log = f"**A:**\n{res_a}\n\n**B:**\n{res_b}"
        with st.expander("Thoughts"): st.markdown(sub_log)
        
        st.session_state.messages.append({"role": "assistant", "content": final, "sub": sub_log})
