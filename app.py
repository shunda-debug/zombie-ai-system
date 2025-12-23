import streamlit as st
import google.generativeai as genai
import concurrent.futures

# --- 1. ページ設定 ---
st.set_page_config(page_title="Sci-Core", page_icon="⚛️", layout="wide")

# --- 2. デザイン (Disney Protocol / Dark Minimal) ---
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

# --- APIキー設定 (安定版) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key) # ここが変更点！
except:
    st.error("🚨 エラー: SecretsにAPIキーが設定されていません。")
    st.stop()

# --- 履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI脳みそ (安定版: google-generativeai) ---
def call_ai(prompt, role):
    try:
        # モデル定義 (gemini-1.5-flash)
        # 安定版ライブラリならこの名前で確実に動きます
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 役割ごとのシステム命令
        if role == "A": # Dreamer
            sys_prompt = "あなたは肯定的なドリーマーです。制限を無視して理想的なアイデアを出してください。"
        elif role == "B": # Realist
            sys_prompt = "あなたは批判的なリアリストです。現実的なリスクや欠陥を指摘してください。"
        else: # C: Judge
            sys_prompt = "あなたは調整役です。AとBの意見を統合し、最適な結論を出してください。"
        
        # 安定版での呼び出し方
        # system_instructionはモデル生成時に渡すのが一般的ですが、
        # 簡易化のためプロンプトに連結して渡します（これが一番エラーが出ない）
        full_prompt = f"{sys_prompt}\n\n【ユーザーの入力】\n{prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"🚨 ERROR: {str(e)}"

# --- 並列処理関数 ---
def run_parallel_thinking(prompt):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_a = executor.submit(call_ai, prompt, "A")
        future_b = executor.submit(call_ai, prompt, "B")
        return future_a.result(), future_b.result()

# --- サイドバー ---
with st.sidebar:
    st.title("⚛️ Sci-Core")
    st.caption("Disney Protocol v5.2 Stable")
    st.markdown("---")
    if st.button("New Chat", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "thoughts" in message:
            with st.expander("✨ Thoughts (Process A vs B)"):
                st.markdown(message["thoughts"])

# --- 入力エリア ---
prompt = st.chat_input("質問やアイデアを入力してください...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        status_box = st.status("Thinking...", expanded=True)
        
        # 1. AとB
        status_box.write("⚡ Dreamer & Critic are debating...")
        res_a, res_b = run_parallel_thinking(prompt)
        
        # 2. C
        status_box.write("👨‍⚖️ Judge is synthesizing...")
        judge_input = f"質問:{prompt}\n案A:{res_a}\n案B:{res_b}\n統合して結論を出せ。"
        final_answer = call_ai(judge_input, "C")
        
        status_box.update(label="Complete", state="complete", expanded=False)
        
        st.markdown(final_answer)
        
        thoughts_log = f"**🚀 Agent A:**\n{res_a}\n\n---\n**🛡️ Agent B:**\n{res_b}"
        with st.expander("✨ Thoughts (Process A vs B)"):
            st.markdown(thoughts_log)
            
        st.session_state.messages.append({
            "role": "assistant", 
            "content": final_answer, 
            "thoughts": thoughts_log
        })
