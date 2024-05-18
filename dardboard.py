import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from streamlit_extras.metric_cards import style_metric_cards


uri = "mongodb+srv://ngduclong173:lRTTd7JxwBgEVO0W@cluster0.tva8uce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client["my_app"]

# Access your collection_raw_logs
collection_structure_logs = db["structure_logs"] 
collection_raw_logs     = db["raw_logs"]
collection_used_devices = db["used_devices"]

pipeline = [
    {"$group": {"_id": "$device_type", "count": {"$sum": 1}}},
    {"$project": {"device_type": "$_id", "count": 1, "_id": 0}},
    {"$sort": {"count": -1}}
]
results_used_devices = list(collection_used_devices.aggregate(pipeline))
total_users = sum(result["count"] for result in results_used_devices)



default_start_date = datetime.now() - timedelta(days=7)
default_end_date = datetime.now()
default_start_time = datetime.now().replace(hour=0, minute=0)
default_end_time = datetime.now().replace(hour=23, minute=59)
st.title("Dash board")


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
    


# Sắp xếp timestamps
data_raw_logs.sort(key=lambda x: x["timestamp"])

# Tính khoảng thời gian giữa timestamp đầu tiên và timestamp cuối cùng
time_diff = data_raw_logs[len(data_raw_logs) - 1]["timestamp"] - data_raw_logs[0]["timestamp"]

# Số request
total_requests = len(data_raw_logs)

# Số giây trong khoảng thời gian
total_seconds = time_diff.total_seconds()

# Tính số request mỗi giây
requests_per_second = total_requests / total_seconds

col1, col2, col3 = st.columns([2,2,1])
col1.metric(label="Trung bình mỗi giây có ", value=f"{requests_per_second} request")
style_metric_cards()
col2.metric(label="Tổng request", value=f"{total_requests} request")
style_metric_cards()

col1, col2 = st.columns(2)
col1.write("### Top 10 các API được sử dụng")
api_counts = {}

# Lặp qua kết quả cursor và đếm số lần gọi của mỗi API
for document in cursor_structures:
    api_name = document["api_name"]
    if api_name in api_counts:
        api_counts[api_name] += 1
    else:
        api_counts[api_name] = 1

# Sắp xếp dictionary theo số lần gọi giảm dần
sorted_api_counts = sorted(api_counts.items(), key=lambda x: x[1], reverse=True)

data = pd.DataFrame(sorted_api_counts, columns=["API name", "Num Of call"])
col1.write(
    data.style.set_table_styles([{
        'selector': 'table',
        'props': [('width', '200px')]
    }])
)   

col2.write("### Các pattern")
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
col2.write(
    top_10_data.style.set_table_styles([{
        'selector': 'table',
        'props': [('width', '200px')]
    }])
)   
st.write("### Tỉ lệ người dùng trên các loại thiết bị") 
labels = [result["device_type"] for result in results_used_devices]
sizes = [result["count"] for result in results_used_devices]


col1, col2 = st.columns(2)
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%')
ax.set_title('Tỉ lệ người dùng trên các loại thiết bị')
plt.axis('equal')  # Tỷ lệ khung hình đảm bảo biểu đồ được vẽ như một vòng tròn.
plt.tight_layout()
col1.pyplot(fig)  

timestamps = []
cursor_raw_logs   = collection_raw_logs.find(query)
for document in cursor_raw_logs:
    timestamp = document["timestamp"] 
    timestamps.append(timestamp)


# date_range = pd.date_range(start=start_date, end=end_date)
data = pd.DataFrame({
    'Timestamp': timestamps
})

# Nhóm theo ngày và đếm số lần request trong mỗi ngày
data = data.groupby(pd.Grouper(key='Timestamp', freq='D')).size().reset_index(name='Number of Requests')

# Hiển thị biểu đồ time series
st.write("### Time series")
fig, ax = plt.subplots()
ax.plot(data['Timestamp'], data['Number of Requests'])
ax.set_xlabel('Date')
ax.set_ylabel('Number of Requests')
ax.set_title('Time Series Plot')
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)