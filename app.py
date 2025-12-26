st.warning(f"現在のモデル: {MODEL_NAME}")
import streamlit as st
import requests
import concurrent.futures

# -----------------------------
# 基本設定
# -----------------------------
st.set_page_config(
    page_title="Sci-Core AI — Disney Protocol Edition",
    page_icon="✨",
    layout="centered",
)

BG = "#0E1117"
FG = "#E0E0E0"

st.markdown(
    f"""
    <style>
        body {{ background-color:{BG}; color:{FG}; }}
        .stMarkdown, .stTextInput, .stChatMessage, .stExpander {{ color:{FG}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# API設定
# -----------------------------
API_KEY = st.secrets["GEMINI_API_KEY"]

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
MODEL_NAME = "gemini-1.5-flash"   # ← 安定稼働版

HEADERS = {"Content-Type": "application/json"}


def call_gemini(prompt: str):
    """
    Google Gemini REST API (generateContent)
    requestsのみ使用
    """
    url = f"{BASE_URL}/models/{MODEL_NAME}:generateContent?key={API_KEY}"

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
        res = requests.post(url, headers=HEADERS, json=payload)

        # ---- エラーは Raw で返す（デバッグ目的・仕様要件）----
        if res.status_code >= 400:
            return f"[ERROR] Status Code: {res.status_code} Raw Error: {res.text}"

        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"[EXCEPTION] {str(e)}"


# -----------------------------
# セッションログ
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# -----------------------------
# Disney Strategy — 各エージェント定義
# -----------------------------
def prompt_dreamer(user_input):
    return f"""
あなたは「The Dreamer（理想的・革新的・制約無視）」の役割です。

ユーザーの課題:
{user_input}

制約（予算・技術・常識）を一切考慮せず、
ワクワクする未来的で革新的な解決案を3つ提案してください。
"""


def prompt_realist(user_input):
    return f"""
あなたは「The Realist / Critic（現実的・批判的）」の役割です。

ユーザーの課題:
{user_input}

以下の観点から徹底的に問題点・欠陥・リスクを指摘してください。

・コスト
・実現性
・スケジュール
・安全性
・運用上の負担

厳しく遠慮なく評価してください。
"""


def prompt_judge(user_input, out_a, out_b):
    return f"""
あなたは「The Judge（統合・調停者）」です。

ユーザーの課題:
{user_input}

--- Agent A（理想案） ---
{out_a}

--- Agent B（現実的批判） ---
{out_b}

役割:
Aの良い点を活かし、
Bの懸念点を解決する
「第3の解決策（アウフヘーベン）」を提示してください。

条件:
・現実的に実行可能
・しかし革新性を失わない
・手順ベースで具体的
"""


# -----------------------------
# UI
# -----------------------------
st.title("✨ 最終結論（Agent C）")

user_input = st.chat_input("質問・相談を入力してください…")

if user_input:

    # 並列処理（A & B を同時実行）
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_a = executor.submit(call_gemini, prompt_dreamer(user_input))
        future_b = executor.submit(call_gemini, prompt_realist(user_input))

        out_a = future_a.result()
        out_b = future_b.result()

    # Agent C（統合）
    out_c = call_gemini(prompt_judge(user_input, out_a, out_b))

    # セッションに保存
    st.session_state.history.append(
        {
            "user": user_input,
            "A": out_a,
            "B": out_b,
            "C": out_c,
        }
    )

# -----------------------------
# 表示（最新のみ メイン＝C）
# -----------------------------
if st.session_state.history:
    last = st.session_state.history[-1]

    st.markdown(last["C"])

    with st.expander("✨ 思考プロセスを表示 (Thoughts)"):
        st.subheader("🟦 Agent A — Dreamer")
        st.markdown(last["A"])

        st.subheader("🟥 Agent B — Realist / Critic")
        st.markdown(last["B"])
