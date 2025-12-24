import streamlit as st
import requests
import concurrent.futures

# -------------------------------
#  基本設定 / UIテーマ
# -------------------------------
st.set_page_config(
    page_title="Sci-Core AI — Disney Protocol Edition",
    layout="centered"
)

# Dark Minimal Styling
st.markdown(
    """
    <style>
    body { background-color: #0E1117 !important; }
    .stMarkdown, .stChatMessage, .stTextInput, .stTextArea,
    .stButton, .stExpander {
        color: #E0E0E0 !important;
    }
    .main { background-color: #0E1117 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧠 Sci-Core AI — Disney Protocol Edition")

# -------------------------------
#  セッション管理
# -------------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# -------------------------------
#  Gemini REST API 呼び出し
#  （google-generativeai は使用しない）
# -------------------------------
MODEL_NAME = "gemini-1.5-flash-latest"  # ← 修正版モデル名

def call_gemini_api(prompt: str):
    api_key = st.secrets["GEMINI_API_KEY"]

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL_NAME}:generateContent?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        res = requests.post(url, json=payload, timeout=60)

        # ❗ 要件どおり：エラー時は Raw Response をそのまま返す
        if not res.ok:
            return (
                f"[ERROR]\n"
                f"Status Code: {res.status_code}\n"
                f"Raw Error:\n{res.text}"
            )

        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"[EXCEPTION]\n{str(e)}"


# -------------------------------
#  Disney Strategy — Prompt Templates
# -------------------------------
def build_prompt_dreamer(user_input):
    return f"""
You are Agent A — The Dreamer.
Generate bold, innovative, optimistic ideas.
Ignore constraints such as cost, time, and feasibility.

User Question:
{user_input}

Output Style:
- visionary
- creative
- inspiring
- no limitations
"""

def build_prompt_critic(user_input):
    return f"""
You are Agent B — The Realist / Critic.
Analyze risks, constraints, feasibility, costs, and failures.
Be strict, logical, and critical.

User Question:
{user_input}

Output Style:
- risk assessment
- weaknesses
- constraints
- potential failures
"""

def build_prompt_judge(user_input, a_out, b_out):
    return f"""
You are Agent C — The Judge / Synthesizer.

Your task:
Create a **third solution** which:
- preserves the innovative strengths of Agent A
- resolves the realistic concerns of Agent B
- is practical, balanced, and elegant

Context:

[Agent A — Dreamer Output]
{a_out}

[Agent B — Realist Output]
{b_out}

User Question:
{user_input}

Output Style:
- clear
- structured
- actionable
- balanced innovation
"""


# -------------------------------
#  UI — 履歴表示（既定は Agent C のみ）
# -------------------------------
for turn in st.session_state.history:
    st.markdown("### ✨ 最終結論（Agent C）")
    st.markdown(turn["agent_c"])

    with st.expander("✨ 思考プロセスを表示 (Thoughts)"):
        st.markdown("#### 🟦 Agent A — Dreamer")
        st.markdown(turn["agent_a"])

        st.markdown("#### 🟥 Agent B — Realist / Critic")
        st.markdown(turn["agent_b"])

    st.divider()


# -------------------------------
#  入力フォーム（画面下固定）
# -------------------------------
user_input = st.chat_input("質問・テーマを入力してください...")

if user_input:

    # Phase 1 — 並列思考（A & B を concurrent.futures で同時実行）
    prompt_a = build_prompt_dreamer(user_input)
    prompt_b = build_prompt_critic(user_input)

    with st.spinner("Processing — Running parallel reasoning..."):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(call_gemini_api, prompt_a)
            future_b = executor.submit(call_gemini_api, prompt_b)

            agent_a_out = future_a.result()
            agent_b_out = future_b.result()

    # Phase 2 — 統合（Agent C）
    prompt_c = build_prompt_judge(user_input, agent_a_out, agent_b_out)
    agent_c_out = call_gemini_api(prompt_c)

    # セッション履歴へ保存
    st.session_state.history.append(
        {
            "user": user_input,
            "agent_a": agent_a_out,
            "agent_b": agent_b_out,
            "agent_c": agent_c_out,
        }
    )

    # 直近の結果を即時表示
    st.markdown("### ✨ 最終結論（Agent C）")
    st.markdown(agent_c_out)

    with st.expander("✨ 思考プロセスを表示 (Thoughts)"):
        st.markdown("#### 🟦 Agent A — Dreamer")
        st.markdown(agent_a_out)

        st.markdown("#### 🟥 Agent B — Realist / Critic")
        st.markdown(agent_b_out)

    st.divider()

