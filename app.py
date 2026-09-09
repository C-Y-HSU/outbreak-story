from datetime import datetime
import os
import pandas as pd
import streamlit as st

st.title("🏥 群聚事件管理系統 - 個案核心日誌")
st.write(
    "以「確診者」為單位，手動輸入基本資料與群聚事件歷程，並依指定順序由左至右排列。"
)

# 定義儲存資料的檔案名稱
DATA_FILE = "outbreak_logs.csv"

# 定義你要求的標準欄位順序
DESIRED_COLS = [
    "發生日期",
    "姓名",
    "性別",
    "生日",
    "身份證字號",
    "確診管道",
    "後續處理",
    "記錄時間",
]


# 載入現有資料，並強制規範由左至右的排列順序
def load_data():
  if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    # 按照 DESIRED_COLS 的順序重新排列欄位（避免舊 CSV 順序錯亂）
    existing_cols = [col for col in DESIRED_COLS if col in df.columns]
    other_cols = [col for col in df.columns if col not in DESIRED_COLS]
    return df[existing_cols + other_cols]
  else:
    return pd.DataFrame(columns=DESIRED_COLS)


df_logs = load_data()

# 建立個案與日誌輸入表單
with st.form("case_form"):
  st.subheader("📝 新增確診者資料與日誌")

  # 1. 發生日期
  case_date = st.date_input("1. 發生日期")

  col1, col2 = st.columns(2)
  with col1:
    # 2. 姓名
    name = st.text_input("2. 姓名")
    # 3. 性別
    gender = st.selectbox("3. 性別", ["男", "女", "其他"])

  with col2:
    # 4. 生日（手動輸入文字框）
    birthday = st.text_input(
        "4. 生日（可直接手動輸入，例如：1991-03-08 或 民國80年3月8日）"
    )
    # 5. 身份證字號
    id_number = st.text_input("5. 身份證字號（例如：A123456789）")

  # 6. 確診管道
  diagnosis_method = st.text_input(
      "6. 確診管道（例如：快篩陽性、發燒就醫、PCR）"
  )

  # 7. 後續處理
  follow_up_action = st.text_area(
      "7. 後續處理（例如：安排單人隔離、通報疾管科、給予症狀治療）"
  )

  submitted = st.form_submit_button("送出並記錄個案日誌")

  if submitted:
    if not name or not id_number:
      st.warning("⚠️ 請務必填寫「姓名」與「身份證字號」！")
    else:
      now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      # 包裝新資料
      new_data = pd.DataFrame([{
          "發生日期": str(case_date),
          "姓名": name,
          "性別": gender,
          "生日": birthday,
          "身份證字號": id_number.upper(),
          "確診管道": diagnosis_method,
          "後續處理": follow_up_action,
          "記錄時間": now_time,
      }])

      # 串接新舊資料
      df_logs = pd.concat([df_logs, new_data], ignore_index=True)

      # 存檔前再次確保欄位順序整齊
      existing_cols = [col for col in DESIRED_COLS if col in df_logs.columns]
      other_cols = [col for col in df_logs.columns if col not in DESIRED_COLS]
      df_logs = df_logs[existing_cols + other_cols]

      df_logs.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

      st.success(f"🎉 成功記錄確診者【{name}】的個案日誌！")

# 顯示目前的總日誌表格
st.markdown("---")
st.subheader("📋 目前累積的確診個案總日誌")

if not df_logs.empty:
  st.dataframe(df_logs, use_container_width=True)
else:
  st.info("print目前尚無確診個案紀錄，請透過上方表單新增第一筆資料！")
