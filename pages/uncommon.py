import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from streamlit_extras.metric_cards import style_metric_cards


st.title("Page anomaly logs/ raw logs")
default_start_date = datetime.now() - timedelta(days=7)
default_end_date = datetime.now()
default_start_time = datetime.now().replace(hour=0, minute=0)
default_end_time = datetime.now().replace(hour=23, minute=59)


start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 2, 25)

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
collection_anomaly_logs = db["anomaly_logs"]



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

arr = []

cursor_anomaly_logs = collection_anomaly_logs.find(query)
for document in cursor_anomaly_logs:
    arr.append(document)
    
print(arr)

data = pd.DataFrame(arr, columns=["timestamp", "message"])
st.write(
    data.style.set_table_styles([{
        'selector': 'table',
        'props': [('width', '1700px')]
    }])
)   