import streamlit as st
import google.generativeai as genai

# ==============================
# 設定
# ==============================

API_KEY = st.secrets.get("GOOGLE_API_KEY", None)

MODEL_NAME = "gemini-1.5-flash"

st.warning(f"現在のモデル: {MODEL_NAME}")

if not API_KEY:
    st.error("❌ APIキーが設定されていません（Streamlit Secrets に GOOGLE_API_KEY を追加してください）")
    st.stop()

genai.configure(api_key=API_KEY)


# ==============================
# Gemini 呼び出し関数
# ==============================

def call_gemini(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        # safety / empty response 対策
        if not hasattr(response, "text") or response.text is None:
            return "⚠ モデルからテキスト応答を取得できませんでした。"

        return response.text

    except Exception as e:
        return f"⚠ エラーが発生しました: {e}"


# ==============================
# UI
# ==============================

st.title("🧠 Zombie AI System - Gemini Debug 版")

user_input = st.text_area(
    "入力テキスト",
    placeholder="ここに質問やプロンプトを入力してください"
)

if st.button("送信"):
    if not user_input.strip():
        st.warning("⚠ 入力してください")
    else:
        with st.spinner("Gemini に送信中..."):
            output = call_gemini(user_input)

        st.subheader("📌 出力")
        st.write(output)
