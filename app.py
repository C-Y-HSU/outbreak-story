from datetime import datetime
import os
import pandas as pd
import streamlit as st

st.title("🏥 群聚事件管理系統 - 核心日誌與累積")
st.write("透過自動化日誌累積，讓每次輸入的資料都妥善保存，不再遺失！")

# 定義儲存資料的檔案名稱
DATA_FILE = "outbreak_logs.csv"


# 載入現有資料的函數
def load_data():
  if os.path.exists(DATA_FILE):
    # 如果檔案存在，把它讀進來
    return pd.read_csv(DATA_FILE)
  else:
    # 如果檔案還不存在，建立一個全新的空白表格架構
    return pd.DataFrame(columns=["發生日期", "確診管道", "後續處理", "記錄時間"])


# 讀取目前的日誌資料
df_logs = load_data()

# 建立輸入表單
with st.form("log_form"):
  st.subheader("📝 新增確診者日誌")

  case_date = st.date_input("1. 發生當下日期")
  diagnosis_method = st.text_input(
      "2. 如何知道確診（例如：快篩陽性、發燒就醫）"
  )
  follow_up_action = st.text_area("3. 後續處理（例如：安排隔離、通報等）")

  submitted = st.form_submit_button("送出並記錄日誌")

  if submitted:
    if not diagnosis_method:
      st.warning("請至少填寫「如何知道確診」欄位！")
    else:
      # 取得當下系統時間
      now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      # 包裝成新的一筆資料
      new_data = pd.DataFrame(
          [{
              "發生日期": str(case_date),
              "確診管道": diagnosis_method,
              "後續處理": follow_up_action,
              "記錄時間": now_time,
          }]
      )

      # 把新資料串接到原本的資料後面
      df_logs = pd.concat([df_logs, new_data], ignore_index=True)

      # 存回 CSV 檔案中
      df_logs.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

      st.success("🎉 成功記錄此筆個案，並已自動存入日誌庫中！")

# 顯示「自動販賣機」累積的總日誌清單
st.markdown("---")
st.subheader("📋 目前累積的事件總日誌（自動販賣機清單）")

if not df_logs.empty:
  # 顯示漂亮的互動表格
  st.dataframe(df_logs, use_container_width=True)
else:
  st.info("目前尚無個案紀錄，請透過上方表單新增第一筆資料！")
