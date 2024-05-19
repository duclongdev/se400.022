from pymongo import MongoClient
from datetime import datetime
import pandas as pd

# Constant
DATABASE_NAME = "my_app"

def calc_user_device_percent(db_client):
  # Get collection
  collection_used_devices = db_client["used_devices"]

  # Query pipeline
  pipeline = [
    {"$group": {"_id": "$device_type", "count": {"$sum": 1}}},
    {"$project": {"device_type": "$_id", "count": 1, "_id": 0}},
    {"$sort": {"count": -1}}
  ]
  results_used_devices = list(collection_used_devices.aggregate(pipeline))
  labels = [result["device_type"] for result in results_used_devices]
  sizes = [result["count"] for result in results_used_devices]

  return [labels, sizes]

def total_user_activity(start_date, end_date):
  # Init MongoDB connection
  client = MongoClient('localhost', 27017)

  # Get collection
  collection_used_devices = client["logs"]["structure_logs"]

  # Create start and end date
  # start_date = datetime(2024, 1, 30, 18, 0, 0)
  # end_date = datetime(2024, 3, 1, 10, 0, 0)

  # Query pipeline
  pipeline = [
    {
      '$match': {
          'timestamp': {'$gte': start_date, '$lte': end_date},
          'user_id': {'$ne': ''}
      }
    },
    {
      '$group': {
          '_id': '$user_id'
      }
    },
    {
      '$count': 'distinct_user_count'
    }
  ]


  results_used_devices = list(collection_used_devices.aggregate(pipeline))
  return results_used_devices[0]["distinct_user_count"] if results_used_devices else 0

def req_datetime_timeseries(client, start_datetime, end_datetime):
  query = {
    "timestamp": {
        "$gte": start_datetime,
        "$lte": end_datetime
    }
  }

  timestamps = []
  raw_logs_collection = client[DATABASE_NAME]["raw_logs"]
  cursor_raw_logs   = raw_logs_collection.find(query)
  for document in cursor_raw_logs:
      timestamp = document["timestamp"]
      timestamps.append(timestamp)


  # date_range = pd.date_range(start=start_date, end=end_date)
  data = pd.DataFrame({
      'Timestamp': timestamps
  })

  # Nhóm theo ngày và đếm số lần request trong mỗi ngày
  data = data.groupby(pd.Grouper(key='Timestamp', freq='D')).size().reset_index(name='Number of Requests')
  return data

def top_api_used(client, start_datetime, end_datetime):
  api_counts = {}
  query = {
    "timestamp": {
        "$gte": start_datetime,
        "$lte": end_datetime
    }
  }

  # Lặp qua kết quả cursor và đếm số lần gọi của mỗi API
  structure_logs_collection = client[DATABASE_NAME]["structure_logs"]

  cursor_structures = structure_logs_collection.find(query)

  for document in cursor_structures:
      api_name = document["api_name"]
      if api_name in api_counts:
          api_counts[api_name] += 1
      else:
          api_counts[api_name] = 1

  # Sắp xếp dictionary theo số lần gọi giảm dần
  sorted_api_counts = sorted(api_counts.items(), key=lambda x: x[1], reverse=True)

  data = pd.DataFrame(sorted_api_counts, columns=["API name", "Num Of call"])
  return data

def req_insight(data_raw_logs):
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
  return [total_requests, round(requests_per_second, 5)]
# print(total_user_activity(1, 2))