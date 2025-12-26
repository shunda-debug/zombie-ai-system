import streamlit as st
from google import generativeai as genai
import os

# =============================
# 🔑 Gemini API KEY の設定
# =============================
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ GEMINI_API_KEY が設定されていません（環境変数に追加してください）")
    st.stop()

genai.configure(api_key=API_KEY)

# =============================
# 🧠 使用するモデル名
# =============================
MODEL_NAME = "gemini-1.5-flash"

st.title("🧟‍♂️ Zombie-AI System（テスト版）")
st.warning(f"現在のモデル: {MODEL_NAME}")

# =============================
# ✉️ 入力フォーム
# =============================
user_input = st.text_input("質問 or 指示を入力してください")

if st.button("送信"):
    if not user_input:
        st.warning("入力が空です")
    else:
        try:
            model = genai.GenerativeModel(MODEL_NAME)

            response = model.generate_content(user_input)

            st.subheader("🧠 AIの応答")
            st.write(response.text)

        except Exception as e:
            st.error("⚠️ API 実行中にエラーが発生しました")
            st.code(str(e))
st.divider()
st.subheader("🧾 利用可能なモデル一覧（デバッグ用）")

if st.button("モデルを一覧表示する"):
    try:
        models = genai.list_models()
        for m in models:
            st.write(m.name)
    except Exception as e:
        st.error("モデル一覧の取得に失敗しました")
        st.code(str(e))
