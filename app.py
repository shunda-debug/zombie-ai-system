import streamlit as st
import google.generativeai as genai

# ==============================
#  設定
# ==============================

API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"

model = genai.GenerativeModel(MODEL_NAME)

st.title("🧠 マルチエージェント AI システム")

st.warning(f"現在のモデル: {MODEL_NAME}")

# ==============================
#  プロンプト入力
# ==============================

user_input = st.text_area(
    "質問 / 課題を入力してください",
    height=150
)

run_button = st.button("🚀 実行")


# ==============================
#  エージェント関数
# ==============================

def run_agent(role_name, system_prompt, content):
    st.subheader(role_name)

    prompt = f"""
あなたは {role_name} です。

ルール:
- 箇条書きで論理的に
- 無駄な装飾はしない
- 日本語で書く

役割説明:
{system_prompt}

ユーザー入力:
{content}
"""

    try:
        response = model.generate_content(prompt)
        output = response.text

    except Exception as e:
        output = f"[ERROR] {str(e)}"

    st.write(output)

    return output


# ==============================
#  ボタン押下時の実行処理
# ==============================

if run_button and user_input.strip():

    st.divider()
    st.header("Agent A — Dreamer（発想担当）")

    agent_a = run_agent(
        "Agent A — Dreamer",
        "自由発想で大胆なアイデアを出す役割。制約を考えすぎない。",
        user_input
    )

    st.divider()
    st.header("Agent B — Realist / Critic（批判担当）")

    agent_b = run_agent(
        "Agent B — Realist / Critic",
        "現実的な観点から弱点・リスク・欠点を洗い出す役割。",
        f"Agent A の案:\n{agent_a}"
    )

    st.divider()
    st.header("Agent C — Synthesizer（統合担当）")

    final_answer = run_agent(
        "Agent C — Synthesizer",
        """
Agent A と Agent B の内容を整理し
- 良い点を採用
- 問題点を修正
- 実行可能な結論をまとめる役割
""",
        f"Agent A:\n{agent_a}\n\nAgent B:\n{agent_b}"
    )

    st.success("🎉 処理完了！")
