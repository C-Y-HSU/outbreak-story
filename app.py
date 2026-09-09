import streamlit as st

# 1. 設定網頁的標題
st.title("🏥 群聚事件管理系統")

# 2. 顯示一句歡迎語
st.write("歡迎使用！這是我們系統的第一個版本，準備開始記錄個案囉！")

# 3. 測試按鈕
if st.button("點擊測試按鈕"):
    st.success("太棒了！你的第一個互動按鈕成功運作了！")
