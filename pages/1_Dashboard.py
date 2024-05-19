import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from common.db_connection import connect_to_db
from common.insight_query import calc_user_device_percent, total_user_activity, req_datetime_timeseries, top_api_used, req_insight

st.sidebar.write("### Navigation")

# Init MongoDB connection
client = connect_to_db()
# Get the database
db = client["my_app"]

# Access your collection_raw_logs
collection_structure_logs = db["structure_logs"]
collection_raw_logs     = db["raw_logs"]


default_start_date = datetime.now() - timedelta(days=7)
default_end_date = datetime.now()
default_start_time = datetime.now().replace(hour=0, minute=0)
default_end_time = datetime.now().replace(hour=23, minute=59)
st.title("🟢 Dashboard")


default_start_date = datetime.now() - timedelta(days=30)
default_end_date = datetime.now()
default_start_time = datetime.now().replace(hour=0, minute=0)
default_end_time = datetime.now().replace(hour=23, minute=59)


st.write("### Input Date")
col1, col2 = st.columns(2)
start_date = col1.date_input('Start Date', value=default_start_date)
start_time = col2.time_input('Start Time', value=default_start_time)
end_date   = col1.date_input('End Date', value=default_end_date)
loan_term  = col2.time_input('End Time', value=default_end_time)

start_datetime = datetime.combine(start_date, start_time)
end_datetime = datetime.combine(end_date, loan_term)
query = {
    "timestamp": {
        "$gte": start_datetime,
        "$lte": end_datetime
    }
}
cursor_structures = collection_structure_logs.find(query)
cursor_raw_logs   = collection_raw_logs.find(query)


collection_names = db.list_collection_names()


data_raw_logs = []

for document in cursor_raw_logs:
    timestamp = document["timestamp"]
    data_raw_logs.append({"timestamp": timestamp})

# Tỉ lệ người dùng trên các loại thiết bị
col1, col2, col3 = st.columns([5, 5, 4], gap="medium")
labels, sizes = calc_user_device_percent(db)
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%')
# ax.set_title('Tỉ lệ người dùng trên các loại thiết bị')
plt.axis('equal')  # Tỷ lệ khung hình đảm bảo biểu đồ được vẽ như một vòng tròn.
plt.tight_layout()
col1.write("#### Tỉ lệ người dùng trên các loại thiết bị")
col1.pyplot(fig)

total_users = total_user_activity(start_datetime, end_datetime)
col2.write("#### Số người hoạt động trong khoảng thời gian này")
col2.write(f"# {total_users}")


data = top_api_used(client, start_datetime, end_datetime)
col3.write("#### Top 10 các API sử dụng nhiều nhất")
col3.write(
    data.style.set_table_styles([{
        'selector': 'table',
        'props': [('width', '100%')]
    }])
)


col1, col2 = st.columns([6, 4], gap="medium")
data = req_datetime_timeseries(client, start_datetime, end_datetime)

# Hiển thị biểu đồ time series
col1.write("#### Time series")
fig, ax = plt.subplots()
ax.plot(data['Timestamp'], data['Number of Requests'])
ax.set_xlabel('Date')
ax.set_ylabel('Number of Requests')
ax.set_title('Time Series Plot')
plt.xticks(rotation=45)
plt.tight_layout()
col1.pyplot(fig)


# Request insight
total_requests, requests_per_second = req_insight(data_raw_logs)
col2.write("#### Total requests")
col2.write(f"# {total_requests}")
col2.write("#### Requests per second")
col2.write(f"# {requests_per_second}")


# Pattern recognition
st.write("#### Pattern recognition")
cursor_raw_logs   = collection_raw_logs.find(query)
message_counts = {}
total_messages = 0
for document in cursor_raw_logs:
    message = document["message"]
    if message in message_counts:
        message_counts[message] += 1
    else:
        message_counts[message] = 1
    total_messages += 1

message_ratios = {message: count / total_messages for message, count in message_counts.items()}

# Sắp xếp message_counts theo số lần xuất hiện giảm dần
sorted_message_counts = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)

# Chuyển đổi dữ liệu thành DataFrame
data = pd.DataFrame(sorted_message_counts, columns=["Message", "Count"])

# Thêm cột Ratio vào DataFrame
data["Ratio"] = data["Message"].apply(lambda x: message_ratios[x])

# Hiển thị top 10 messages
top_10_data = data.head(10)
st.write(
    top_10_data.style.set_table_styles([{
        'selector': 'table',
        'props': [('width', '200px')]
    }])
)