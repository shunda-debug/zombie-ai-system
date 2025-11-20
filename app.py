import streamlit as st
import re
import unicodedata
from google import genai

# --- ページ設定 ---
st.set_page_config(page_title="Zombie AI Enterprise", page_icon="🧟")

st.title("🧟 Zombie AI System")
st.caption("Ultimate Reliability & Cost Efficiency Architecture")

# --- サイドバーでAPIキー入力 ---
# これにより、コード内にキーを書かなくて済むので、GitHubに上げても安全です
with st.sidebar:
    st.header("🔐 設定")
    api_key = st.text_input("Gemini APIキーを入力", type="password")
    st.markdown("[APIキーの取得はこちら](https://aistudio.google.com/app/apikey)")
    st.info("キーはこのタブでのみ使用されます。保存はされません。")

# --- ロジック関数 ---
def get_integer(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^0-9.]', '', text)
    if '.' in text: text = text.split('.')[0]
    return text

def call_ai(client, model, prompt):
    try:
        res = client.models.generate_content(model=model, contents=prompt)
        return res.text.strip()
    except:
        return None

# --- メイン処理 ---
if not api_key:
    st.warning("👈 左のサイドバーにGemini APIキーを入れてシステムを稼働させてください。")
else:
    client = genai.Client(api_key=api_key)
    
    # チャット履歴の初期化（会話を続ける場合に必要）
    if "messages" not in st.session_state:
        st.session_state.messages = []

    question = st.chat_input("質問を入力（例: 12345+67890は？）")
    
    if question:
        # ユーザーの質問を表示
        with st.chat_message("user"):
            st.write(question)
            
        # AIの処理開始
        with st.chat_message("assistant"):
            status = st.empty()
            status.info("⚡ Tier 1: Flashモデル(x2)でコストを抑えつつ高速照合中...")
            
            col1, col2 = st.columns(2)
            
            # Flash実行
            res_a = call_ai(client, "gemini-2.0-flash", f"{question} (簡潔に)")
            res_c = call_ai(client, "gemini-2.0-flash", f"{question} (簡潔に)")
            
            with col1:
                st.markdown("**Flash A**")
                st.write(res_a if res_a else "Error")
            with col2:
                st.markdown("**Flash C**")
                st.write(res_c if res_c else "Error")
            
            # 判定ロジック
            match = False
            final_answer = ""
            
            if res_a and res_c:
                num_a = get_integer(res_a)
                num_c = get_integer(res_c)
                # 数字が含まれていて一致するか、完全に文字列が一致するか
                if (num_a and num_c and num_a == num_c) or (res_a == res_c):
                    match = True
                    final_answer = res_a
            
            # 結果表示
            if match:
                status.success("✅ 【Cost Saved】意見完全一致！Proモデルを節約しました。")
                st.balloons()
                st.markdown(f"### 🏆 結論: {final_answer}")
            else:
                status.warning("🚨 【Mismatch】意見不一致。最高性能Proモデル(Tier 2)を起動します...")
                res_pro = call_ai(client, "gemini-2.0-pro-exp-02-05", f"{question} (専門家として厳密に)")
                
                if res_pro:
                    status.error("🚑 Proモデルが解決しました。")
                    st.divider()
                    st.markdown(f"### 🏆 最終結論 (Pro):")
                    st.write(res_pro)
                else:
                    st.error("💀 システムエラー（API制限など）")
