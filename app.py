import streamlit as st
import google.generativeai as genai
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
    .katex { color: #A8C7FA !important; }
</style>
""", unsafe_allow_html=True)

# --- APIキー設定 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("🚨 エラー: Secrets設定を確認してください")
    st.stop()

# --- 履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI脳みそ (Gemini Pro版) ---
def call_ai(prompt, role):
    # 役割定義
    if role == "A":
        sys_prompt = "あなたは肯定的なドリーマーです。制限を無視して理想的なアイデアを出してください。"
    elif role == "B":
        sys_prompt = "あなたは批判的なリアリストです。現実的なリスクや欠陥を指摘してください。"
    else:
        sys_prompt = "あなたは調整役です。AとBの意見を統合し、最適な結論を出してください。"

    # Gemini Proは system_instruction をサポートしていない場合があるので、プロンプトに混ぜる
    full_prompt = f"{sys_prompt}\n\n【ユーザーの入力】\n{prompt}"

    try:
        # 【ここが変更点】絶対に動く "gemini-pro" を指定
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- 並列処理関数 ---
def run_parallel_thinking(prompt):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_a = executor.submit(call_ai, prompt, "A")
        future_b = executor.submit(call_ai, prompt, "B")
        return future_a.result(), future_b.result()

# --- サイドバー ---
with st.sidebar:
    st.title("⚛️ Sci-Core")
    st.caption("Disney Protocol (Pro ver.)")
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
        final_answer = call_ai(judge_input, "C")
        
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
