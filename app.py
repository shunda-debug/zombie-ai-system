import streamlit as st
from google import genai
import concurrent.futures

# --- 1. ページ設定 ---
st.set_page_config(page_title="Sci-Core", page_icon="⚛️", layout="wide")

# --- 2. デザイン (Disney Protocol / Dark Minimal) ---
st.markdown("""
<style>
    /* 全体のフォントと背景 */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* 入力エリア */
    .stChatInputContainer {
        background-color: #0E1117;
        border-top: 1px solid #333;
    }
    
    /* ユーザーの吹き出し */
    .stChatMessage[data-testid="user"] {
        background-color: #262730;
        border: none;
    }
    
    /* AIの吹き出し */
    .stChatMessage[data-testid="assistant"] {
        background-color: transparent;
        border: none;
    }
    
    /* Expanderのスタイル */
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

# --- APIキー設定 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 エラー: SecretsにAPIキーが設定されていません。")
    st.stop()

# クライアント初期化
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"クライアント初期化エラー: {e}")
    st.stop()

# --- 履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AI脳みそ (デバッグモード搭載) ---
def call_ai(prompt, role):
    try:
        # 役割ごとのシステム命令
        if role == "A": # Dreamer
            sys = """
            あなたは「肯定的なドリーマー（Dreamer）」です。
            ユーザーの問いに対し、制限を無視して、
            最も理想的で、ワクワクする革新的なアイデアを提案してください。
            批判は一切せず、可能性を広げることだけに集中してください。
            """
        elif role == "B": # Realist
            sys = """
            あなたは「批判的なリアリスト（Critic）」です。
            ユーザーの問いに対し、現実的な視点（予算、時間、技術、リスク）から
            懸念点や欠陥を厳しく指摘してください。
            甘い考えを捨て、障害を列挙してください。
            """
        else: # C: Judge
            sys = """
            あなたは「統合する調整者（Judge）」です。
            A（理想）とB（現実）の議論を踏まえ、
            「第3の解決策（アウフヘーベン）」を導き出してください。
            回答は、AやBの議論には触れず、あなたが出した「最終結論」のみを
            論理的かつ洗練された文章で出力してください。
            """
        
        # API呼び出し (gemini-1.5-flash)
        res = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt,
            config={"system_instruction": sys}
        )
        return res.text.strip()
        
    except Exception as e:
        # 【重要】エラーの正体をそのまま返す
        return f"🚨 DEBUG_ERROR: {str(e)}"

# --- 並列処理関数 ---
def run_parallel_thinking(prompt):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_a = executor.submit(call_ai, prompt, "A")
        future_b = executor.submit(call_ai, prompt, "B")
        return future_a.result(), future_b.result()

# --- サイドバー ---
with st.sidebar:
    st.title("⚛️ Sci-Core")
    st.caption("Disney Protocol v5.1")
    
    st.markdown("---")
    if st.button("New Chat", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
# 履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
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
        status_box = st.status("Thinking...", expanded=True)
        
        # 1. AとBが並列で議論
        status_box.write("⚡ Dreamer & Critic are debating...")
        res_a, res_b = run_parallel_thinking(prompt)
        
        # 2. Cが統合
        status_box.write("👨‍⚖️ Judge is synthesizing...")
        
        # もしAかBでエラーが出ていたら、Judgeにはエラー文ごと渡して無理やり処理させるか、停止する
        if "DEBUG_ERROR" in res_a or "DEBUG_ERROR" in res_b:
             final_answer = "⚠️ エラーが発生しました。下のThoughtsを開いて詳細を確認してください。"
        else:
            judge_input = f"質問:{prompt}\n案A:{res_a}\n案B:{res_b}\n統合して結論を出せ。"
            final_answer = call_ai(judge_input, "C")
        
        # 完了
        status_box.update(label="Complete", state="complete", expanded=False)
        
        # 結果表示
        st.markdown(final_answer)
        
        # 思考ログ
        thoughts_log = f"**🚀 Agent A:**\n{res_a}\n\n---\n**🛡️ Agent B:**\n{res_b}"
        
        with st.expander("✨ Thoughts (Process A vs B)"):
            st.markdown(thoughts_log)
            
        # 履歴保存
        st.session_state.messages.append({
            "role": "assistant", 
            "content": final_answer, 
            "thoughts": thoughts_log
        })
