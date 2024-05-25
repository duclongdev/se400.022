import streamlit as st
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from common.db_connection import connect_to_db
from common.checkpassword import check_password


if not check_password():
    st.stop()

# Init MongoDB connection
try:
    db = connect_to_db(True)
except Exception as e:
    st.title("Failed connect with db")
    sys.exit()

st.title("Anomaly logs page")
default_start_date = datetime(2024, 2, 1)
default_start_time = datetime(2024, 2, 1).replace(hour=0, minute=0)
default_end_date = datetime(2024, 2, 1)
default_end_time = datetime(2024, 2, 1).replace(hour=23, minute=59)


collection_anomaly_logs = db["anomaly_logs"]

st.write("### Input Date")
col1, col2 = st.columns(2)
col1, col2 = st.columns(2)
start_date = col1.date_input('Start Date', value=default_start_date)
start_time = col2.time_input('Start Time', value=default_start_time)
end_date   = col1.date_input('End Date', value=default_end_date)
loan_term  = col2.time_input('End Time', value=default_end_time)

start_datetime = datetime.combine(start_date, start_time) - timedelta(hours=7)
end_datetime = datetime.combine(end_date, loan_term) - timedelta(hours=7)

query = {
    "timestamp": {
        "$gte": start_datetime,
        "$lte": end_datetime
    }
}

arr = []

cursor_anomaly_logs = collection_anomaly_logs.find(query)
for document in cursor_anomaly_logs:
    arr.append(document)

data = pd.DataFrame(arr, columns=["timestamp", "message"])
data["timestamp"] = pd.to_datetime(data["timestamp"])

# Add 7 hours to the "timestamp" column
data["timestamp"] = data["timestamp"] + timedelta(hours=7)
st.table(data)