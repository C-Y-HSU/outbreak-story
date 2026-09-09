from datetime import datetime
import os
import pandas as pd
import streamlit as st

st.title("🏥 群聚事件管理系統 - 多事件隔離與日誌")
st.write(
    "支援多個群聚事件同時獨立處理，透過側邊欄切換或新增事件，避免資料互相混淆。"
)

# 定義儲存資料的檔案名稱
DATA_FILE = "outbreak_logs.csv"

# 定義標準欄位順序（新增「事件名稱」在最左側）
DESIRED_COLS = [
    "事件名稱",
    "發生日期",
    "姓名",
    "性別",
    "生日",
    "身份證字號",
    "確診管道",
    "後續處理",
    "記錄時間",
]


# 載入現有資料，並強制規範欄位順序
def load_data():
  if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    existing_cols = [col for col in DESIRED_COLS if col in df.columns]
    other_cols = [col for col in df.columns if col not in DESIRED_COLS]
    return df[existing_cols + other_cols]
  else:
    return pd.DataFrame(columns=DESIRED_COLS)


df_logs = load_data()

# ==========================================
# 側邊欄：事件隔離與切換管理
# ==========================================
st.sidebar.header("📁 事件切換與管理")

# 取得目前所有已存在的事件名稱清單
existing_events = (
    df_logs["事件名稱"].dropna().unique().tolist()
    if not df_logs.empty and "事件名稱" in df_logs.columns
    else []
)

event_mode = st.sidebar.radio("請選擇操作模式", ["選擇現有事件", "新增並切換新事件"])

selected_event = ""
if event_mode == "選擇現有事件":
  if existing_events:
    selected_event = st.sidebar.selectbox("選擇要處理的事件", existing_events)
  else:
    st.sidebar.info("目前尚無任何事件紀錄，請先切換至「新增並切換新事件」。")
    selected_event = st.sidebar.text_input("輸入新事件名稱", "預設群聚事件")
else:
  selected_event = st.sidebar.text_input("輸入新事件名稱（例如：A機構群聚）", "")

if not selected_event:
  selected_event = "未命名群聚事件"

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📌 目前正在處理的事件：**\n### `{selected_event}`")

# 篩選出屬於「當前選定事件」的資料
if not df_logs.empty and "事件名稱" in df_logs.columns:
  df_current_event = df_logs[df_logs["事件名稱"] == selected_event]
else:
  df_current_event = pd.DataFrame(columns=DESIRED_COLS)


# ==========================================
# 主畫面：新增該事件的確診者資料
# ==========================================
with st.form("case_form"):
  st.subheader(f"📝 新增確診者資料（目前事件：{selected_event}）")

  # 1. 發生日期
  case_date = st.date_input("1. 發生日期")

  col1, col2 = st.columns(2)
  with col1:
    # 2. 姓名
    name = st.text_input("2. 姓名")
    # 3. 性別
    gender = st.selectbox("3. 性別", ["男", "女", "其他"])

  with col2:
    # 4. 生日
    birthday = st.text_input(
        "4. 生日（例如：1991-03-08 或 民國80年3月8日）"
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

      # 包裝新資料（包含當前事件名稱）
      new_data = pd.DataFrame([{
          "事件名稱": selected_event,
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

      # 確保欄位順序整齊
      existing_cols = [col for col in DESIRED_COLS if col in df_logs.columns]
      other_cols = [col for col in df_logs.columns if col not in DESIRED_COLS]
      df_logs = df_logs[existing_cols + other_cols]

      # 存檔
      df_logs.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

      st.success(f"🎉 成功將確診者【{name}】記錄至事件【{selected_event}】！")
      st.rerun()  # 重新整理畫面讓表格立即更新


# ==========================================
# 顯示目前事件的總日誌表格
# ==========================================
st.markdown("---")
st.subheader(f"📋 【{selected_event}】目前的確診個案總日誌")

if not df_current_event.empty:
  st.dataframe(df_current_event, use_container_width=True)
else:
  st.info(f"事件【{selected_event}】目前尚無個案紀錄，請透過上方表單新增！")

# 額外提供一個收納選單，讓需要時可以檢視所有事件的大合併總表
with st.expander("🔍 管理員視角：檢視所有事件的總合併日誌"):
  st.dataframe(df_logs, use_container_width=True)
