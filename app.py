from datetime import datetime
import os
import pandas as pd
import streamlit as st

st.title("🏥 群聚事件管理系統 - 指標個案追蹤與隔離")
st.write(
    "以群聚事件為單位，管理個案日誌，並可指定與醒目展示該事件的「指標個案」。"
)

# 定義儲存資料的檔案名稱
DATA_FILE = "outbreak_logs.csv"

# 定義標準欄位順序
DESIRED_COLS = [
    "事件名稱",
    "指標個案",
    "發生日期",
    "姓名",
    "性別",
    "生日",
    "身份證字號",
    "確診管道",
    "後續處理",
    "記錄時間",
]


# 載入現有資料，並強化欄位與型態檢查
def load_data():
  if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)

    if "指標個案" not in df.columns:
      df["指標個案"] = ""
    if "事件名稱" not in df.columns:
      df["事件名稱"] = "未命名群聚事件"

    df["指標個案"] = df["指標個案"].fillna("").astype(str)
    df["事件名稱"] = df["事件名稱"].fillna("未命名群聚事件").astype(str)

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
    selected_event = st.sidebar.text_input("輸入新事件名稱", "預設群聚事件")
else:
  selected_event = st.sidebar.text_input("輸入新事件名稱（例如：A機構群聚）", "")

if not selected_event:
  selected_event = "未命名群聚事件"

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📌 目前正在處理的事件：**\n### `{selected_event}`")

# 篩選出屬於「當前選定事件」的資料，並將「指標個案」自動排序置頂
if not df_logs.empty and "事件名稱" in df_logs.columns:
  df_current_event = df_logs[df_logs["事件名稱"] == selected_event].copy()

  if not df_current_event.empty and "指標個案" in df_current_event.columns:
    # 建立暫時的排序依據：是指標個案的排在最前面 (True 轉數值會排在前面)
    df_current_event["_temp_sort"] = df_current_event[
        "指標個案"
    ].str.contains("指標個案", na=False)
    df_current_event = df_current_event.sort_values(
        by="_temp_sort", ascending=False
    ).drop(columns=["_temp_sort"])
else:
  df_current_event = pd.DataFrame(columns=DESIRED_COLS)


# ==========================================
# 醒目功能：顯示當前事件的「指標個案英雄卡片」
# ==========================================
st.markdown("---")
if not df_current_event.empty and "指標個案" in df_current_event.columns:
  index_cases = df_current_event[
      df_current_event["指標個案"].str.contains("指標個案", na=False)
  ]

  if not index_cases.empty:
    ic = index_cases.iloc[0]
    st.success(
        f"### 🌟 【{selected_event}】之官方認定指標個案\n"
        f"- **姓名**：{ic['姓名']} （{ic['性別']}）\n"
        f"- **身分證字號**：{ic['身份證字號']}\n"
        f"- **發生日期**：{ic['發生日期']} | **確診管道**：{ic['確診管道']}\n"
        f"- **後續處理**：{ic['後續處理']}"
    )
  else:
    st.info(
        f"💡 提示：目前事件【{selected_event}】尚未指定指標個案，請於下方清單中選取。"
    )


# ==========================================
# 主畫面 1：新增該事件的確診者資料
# ==========================================
with st.expander("➕ 點此展開表單：新增確診者資料"):
  with st.form("case_form"):
    case_date = st.date_input("1. 發生日期")

    col1, col2 = st.columns(2)
    with col1:
      name = st.text_input("2. 姓名")
      gender = st.selectbox("3. 性別", ["男", "女", "其他"])

    with col2:
      birthday = st.text_input("4. 生日（例如：1991-03-08 或 民國80年3月8日）")
      id_number = st.text_input("5. 身份證字號（例如：A123456789）")

    diagnosis_method = st.text_input(
        "6. 確診管道（例如：快篩陽性、發燒就醫、PCR）"
    )
    follow_up_action = st.text_area(
        "7. 後續處理（例如：安排單人隔離、通報疾管科）"
    )

    submitted = st.form_submit_button("送出並記錄個案日誌")

    if submitted:
      if not name or not id_number:
        st.warning("⚠️ 請務必填寫「姓名」與「身份證字號」！")
      else:
        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_data = pd.DataFrame([{
            "事件名稱": selected_event,
            "指標個案": "",
            "發生日期": str(case_date),
            "姓名": name,
            "性別": gender,
            "生日": birthday,
            "身份證字號": id_number.upper(),
            "確診管道": diagnosis_method,
            "後續處理": follow_up_action,
            "記錄時間": now_time,
        }])

        df_logs = pd.concat([df_logs, new_data], ignore_index=True)

        existing_cols = [col for col in DESIRED_COLS if col in df_logs.columns]
        other_cols = [col for col in df_logs.columns if col not in DESIRED_COLS]
        df_logs = df_logs[existing_cols + other_cols]

        df_logs.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        st.success(f"🎉 成功將確診者【{name}】記錄至事件【{selected_event}】！")
        st.rerun()


# ==========================================
# 主畫面 2：目前事件的總日誌表格與「指定指標個案」功能
# ==========================================
st.markdown("---")
st.subheader(f"📋 【{selected_event}】目前的確診個案總日誌")

if not df_current_event.empty:
  # 此處顯示的表格，其指標個案已經自動排在最上方
  st.dataframe(df_current_event, use_container_width=True)

  st.markdown("#### ⭐ 設定此事件的指標個案")
  case_options = {
      f"{row['姓名']} ({row['身份證字號']})": idx
      for idx, row in df_current_event.iterrows()
  }

  selected_case_label = st.selectbox(
      "選擇要設為指標個案的確診者", list(case_options.keys())
  )

  if st.button("🌟 確認將此人設為指標個案"):
    target_idx = case_options[selected_case_label]

    df_logs["指標個案"] = df_logs["指標個案"].astype(str)
    df_logs.loc[df_logs["事件名稱"] == selected_event, "指標個案"] = ""
    df_logs.loc[target_idx, "指標個案"] = "⭐ 指標個案"

    df_logs.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    st.success(f"✨ 已成功指定【{selected_case_label}】為本群聚事件的指標個案！")
    st.rerun()

else:
  st.info(f"事件【{selected_event}】目前尚無個案紀錄，請先展開上方表單新增個案！")

# 管理員總表
with st.expander("🔍 管理員視角：檢視所有事件的總合併日誌"):
  st.dataframe(df_logs, use_container_width=True)
