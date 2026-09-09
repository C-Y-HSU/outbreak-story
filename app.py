from datetime import datetime
import os
import pandas as pd
import streamlit as st

st.title("🏥 群聚事件管理系統 - 個案核心日誌")
st.write("以「確診者」為單位，集中管理個人基本資料與群聚事件歷程。")

# 定義儲存資料的檔案名稱
DATA_FILE = "outbreak_logs.csv"


# 載入現有資料的函數
def load_data():
  if os.path.exists(DATA_FILE):
    return pd.read_csv(DATA_FILE)
  else:
    return pd.DataFrame(columns=[
        "姓名",
        "性別",
        "生日(西元)",
        "生日(民國)",
        "身份證字號",
        "發生日期",
        "確診管道",
        "後續處理",
        "記錄時間",
    ])


df_logs = load_data()

# 建立個案與日誌輸入表單
with st.form("case_form"):
  st.subheader("📝 新增確診者基本資料與日誌")

  # 區塊一：確診者個人基本資料
  st.markdown("#### 【1. 確診者基本身分】")
  col1, col2 = st.columns(2)

  with col1:
    name = st.text_input("姓名")
    gender = st.selectbox("性別", ["男", "女", "其他"])

  with col2:
    birth_date = st.date_input(
        "生日（西元）",
        min_value=datetime(1900, 1, 1),
        max_value=datetime.today(),
    )
    id_number = st.text_input("身份證字號（例如：A123456789）")

  st.markdown("---")
  # 區塊二：群聚事件與處理歷程
  st.markdown("#### 【2. 事件與處理紀錄】")
  case_date = st.date_input("發生當下日期")
  diagnosis_method = st.text_input(
      "如何知道確診（例如：快篩陽性、發燒就醫、PCR）"
  )
  follow_up_action = st.text_area(
      "後續處理（例如：安排單人隔離、通報疾管科、給予症狀治療）"
  )

  submitted = st.form_submit_button("送出並記錄個案日誌")

  if submitted:
    if not name or not id_number:
      st.warning("⚠️ 請務必填寫「姓名」與「身份證字號」！")
    else:
      # 自動計算民國生日 (西元年 - 1911)
      roc_year = birth_date.year - 1911
      birth_roc = (
          f"民國 {roc_year} 年 {birth_date.month} 月 {birth_date.day} 日"
      )
      birth_western = str(birth_date)

      now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      # 包裝成新的一筆個案資料
      new_data = pd.DataFrame([{
          "姓名": name,
          "性別": gender,
          "生日(西元)": birth_western,
          "生日(民國)": birth_roc,
          "身份證字號": id_number.upper(),  # 自動轉大寫，避免格式不一
          "發生日期": str(case_date),
          "確診管道": diagnosis_method,
          "後續處理": follow_up_action,
          "記錄時間": now_time,
      }])

      # 串接並存檔
      df_logs = pd.concat([df_logs, new_data], ignore_index=True)
      df_logs.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

      st.success(f"🎉 成功記錄確診者【{name}】的個案日誌與基本資料！")

# 顯示目前的總日誌表格
st.markdown("---")
st.subheader("📋 目前累積的確診個案總日誌")

if not df_logs.empty:
  st.dataframe(df_logs, use_container_width=True)
else:
  st.info("目前尚無確診個案紀錄，請透過上方表單新增第一筆資料！")
