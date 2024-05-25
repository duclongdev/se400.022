import streamlit as st
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from common.db_connection import connect_to_db
from common.checkpassword import check_password
from common.insight_query import calc_user_device_percent, total_user_activity, req_datetime_timeseries, top_api_used, req_insight, log_patttern_recognition

if not check_password():
    st.stop()

# Init MongoDB connection
try:
    db = connect_to_db(True)
except Exception as e:
    st.title("Failed connect with db")
    sys.exit()

default_start_date = datetime(2024, 2, 1)
default_start_time = datetime(2024, 2, 1).replace(hour=0, minute=0)
default_end_date = datetime(2024, 2, 1)
default_end_time = datetime(2024, 2, 1).replace(hour=23, minute=59)
st.title("🟢 Dashboard")


st.write("### Input Date")
col1, col2 = st.columns(2)
start_date = col1.date_input('Start Date', value=default_start_date)
start_time = col2.time_input('Start Time', value=default_start_time)
end_date   = col1.date_input('End Date', value=default_end_date)
loan_term  = col2.time_input('End Time', value=default_end_time) 

start_datetime = datetime.combine(start_date, start_time) - timedelta(hours=7)
end_datetime = datetime.combine(end_date, loan_term) - timedelta(hours=7)

print(start_datetime)
# Tỉ lệ người dùng trên các loại thiết bị
col1, col2, col3 = st.columns([5, 5, 4], gap="medium")
labels, sizes = calc_user_device_percent(db, start_datetime, end_datetime)
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%')
# ax.set_title('Tỉ lệ người dùng trên các loại thiết bị')
plt.axis('equal')  # Tỷ lệ khung hình đảm bảo biểu đồ được vẽ như một vòng tròn.
plt.tight_layout()
col1.write("#### Tỉ lệ người dùng trên các loại thiết bị")
col1.pyplot(fig)

total_users = total_user_activity(db,start_datetime, end_datetime)
col2.write("#### Số người hoạt động trong khoảng thời gian này")
col2.write(f"# {total_users}")


data = top_api_used(db, start_datetime, end_datetime)

col3.write("#### Top 10 các API sử dụng nhiều nhất")
col3.write(
    data.style.set_table_styles([{
        'selector': 'table',
        'props': [('width', '100%')]
    }])
)


col1, col2 = st.columns([6, 4], gap="medium")
data = req_datetime_timeseries(db, start_datetime, end_datetime)
col1.write("#### Time series")
fig, ax = plt.subplots()
ax.plot(data['Adjusted Timestamp'], data['Number of Requests'])
ax.set_xlabel('Date')
ax.set_ylabel('Number of Requests')
ax.set_title('Time Series Plot')
ax.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
col1.pyplot(fig)


# Request insight
total_requests, requests_per_second = req_insight(db ,start_datetime, end_datetime)
col2.write("#### Total requests")
col2.write(f"# {total_requests}")
col2.write("#### Requests per second")
col2.write(f"# {requests_per_second}")


# Pattern recognition
st.write("#### Pattern recognition")
data1 = log_patttern_recognition(db, start_datetime, end_datetime)
df = pd.DataFrame(data1)
html = df.to_html(escape=False)
st.write(html, unsafe_allow_html=True)
st.write('<style type="text/css">.ansi33 { color: #ff0000; }</style', unsafe_allow_html=True)
