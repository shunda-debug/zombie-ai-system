import streamlit as st
from google import genai
import concurrent.futures

# --- 1. ページ設定 (Minimalist Design) ---
st.set_page_config(page_title="Sci-Core", page_icon="⚛️", layout="wide")

# --- 2. デザイン (洗練されたミニマリズム) ---
st.markdown("""
<style>
    /* 全体のフォントと背景を調整 */
    .stApp {
        background-color: #0E1117; /* 深い黒 (Gemini Dark風) */
        color: #E0E0E0;
    }
    
    /* 入力エリアをシンプルに */
    .stChatInputContainer {
        background-color: #0E1117;
        border-top: 1px solid #333;
    }
    
    /* ユーザーの吹き出し (目立たないグレー) */
    .stChatMessage[data-testid="user"] {
        background-color: #262730;
        border: none;
    }
    
    /* AIの吹き出し (背景なし、文字のみ強調) */
    .stChatMessage[data-testid="assistant"] {
        background-color: transparent;
        border: none;
    }
    
    /* 思考プロセスのExpanderをスタイリッシュに */
    .streamlit-expanderHeader {
        background-color: #161B22;
        color: #888;
        font-size: 0.9em;
        border-radius: 5px;
    }
    
    /* ヘッダー隠し */
    header {visibility: hidden;}
    
    /* 数式カラー */
    .katex { color: #A8C7FA !important; }
</style>
""", unsafe_allow_html=True)

# --- APIキー ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Key Error")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI脳みそ (並列処理対応) ---
def call_ai(prompt, role):
    try:
        # 役割ごとのシステム命令 (Disney Strategy)
        if role == "A": # Dreamer
            sys = """
            あなたは「肯定的なドリーマー（Dreamer）」です。
            ユーザーの問いに対し、制限（予算、技術、時間）を無視して、
            最も理想的で、ワクワクする、革新的なアイデアを提案してください。
            批判は一切せず、可能性を広げることだけに集中してください。
            """
        elif role == "B": # Realist/Critic
            sys = """
            あなたは「批判的なリアリスト（Critic）」です。
            ユーザーの問いに対し、現実的な視点（予算、時間、物理法則、リスク）から
            懸念点や欠陥を厳しく指摘してください。
            甘い考えを捨て、最悪のケースや障害を列挙してください。
            """
        else: # C: Judge
            sys = """
            あなたは「統合する調整者（Judge）」です。
            あなたはユーザーの質問と、それに対する「A（理想案）」と「B（批判案）」を持っています。
            
            あなたの仕事は、Bの懸念をAのアイデアでどう乗り越えるか、
            あるいはAのアイデアをBの制約の中でどう実現するか、
            「第3の解決策（アウフヘーベン）」を導き出すことです。
            
            回答は、AやBの議論には触れず、**あなたが出した「最終結論」のみ**を、
            論理的かつ洗練された文章で出力してください。
            """
        
        res = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt,
            config={"system_instruction": sys}
        )
        return res.text.strip()
    except:
        return "Error"

# --- 並列処理関数 (時間を短縮する魔法) ---
def run_parallel_thinking(prompt):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # AとBを「ヨーイドン」で同時に走らせる
        future_a = executor.submit(call_ai, prompt, "A")
        future_b = executor.submit(call_ai, prompt, "B")
        
        # 両方が終わるのを待って結果を受け取る
        return future_a.result(), future_b.result()

# --- サイドバー ---
with st.sidebar:
    st.title("⚛️ Sci-Core")
    st.caption("Disney Protocol v5.0")
    
    st.markdown("---")
    if st.button("New Chat", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
# 履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # 思考プロセスがあれば表示 (Google AI Studio風)
        if "thoughts" in message:
            with st.expander("✨ Thoughts (Process A vs B)"):
                st.markdown(message["thoughts"])

# --- 入力エリア ---
prompt = st.chat_input("質問やアイデアを入力してください...")

if prompt:
    # ユーザー表示
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI処理
    with st.chat_message("assistant"):
        # ステータス表示（カッコよく）
        status_box = st.status("Thinking...", expanded=True)
        
        # 1. AとBが並列で議論 (パラレル処理)
        status_box.write("⚡ Dreamer & Critic are debating...")
        res_a, res_b = run_parallel_thinking(prompt)
        
        # 2. Cが統合 (ジャッジ)
        status_box.write("👨‍⚖️ Judge is synthesizing...")
        
        judge_input = f"""
        【ユーザーの質問】
        {prompt}
        
        【Aの意見（理想）】
        {res_a}
        
        【Bの意見（現実）】
        {res_b}
        
        これらを統合し、最適な回答を作成せよ。
        """
        final_answer = call_ai(judge_input, "C")
        
        # 完了
        status_box.update(label="Complete", state="complete", expanded=False)
        
        # 結果表示
        st.markdown(final_answer)
        
        # 思考ログの作成
        thoughts_log = f"""
        **🚀 Agent A (Dreamer):**
        {res_a}
        
        ---
        **🛡️ Agent B (Realist):**
        {res_b}
        """
        
        with st.expander("✨ Thoughts (Process A vs B)"):
            st.markdown(thoughts_log)
            
        # 履歴保存
        st.session_state.messages.append({
            "role": "assistant", 
            "content": final_answer, 
            "thoughts": thoughts_log
        })
