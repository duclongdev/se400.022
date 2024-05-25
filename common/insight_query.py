from pymongo import MongoClient
from datetime import datetime, timedelta
from common.logmine import pattern_recognition
import pandas as pd


def calc_user_device_percent(client, start_date, end_date):
  # Get collection
  collection_used_devices = client["used_devices"]

  # Query pipeline
  pipeline = [
    {'$match': {
          'timestamp': {'$gte': start_date, '$lte': end_date},
          'user_id': {'$ne': ''}}},
    {"$group": {"_id": "$device_type", "count": {"$sum": 1}}},
    {"$project": {"device_type": "$_id", "count": 1, "_id": 0}},
    {"$sort": {"count": -1}}
  ]
  results_used_devices = list(collection_used_devices.aggregate(pipeline))
  labels = [result["device_type"] for result in results_used_devices]
  sizes = [result["count"] for result in results_used_devices]

  return [labels, sizes]

def total_user_activity(client, start_date, end_date):
  # Init MongoDB connection

  # Get collection
  collection_used_devices = client["structure_logs"]

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
    # Calculate the interval duration in seconds
    total_seconds = (end_datetime - start_datetime).total_seconds()
    interval_duration = total_seconds / 12

    # Define the collection
    raw_logs_collection = client["raw_logs"]

    # Define the aggregation pipeline
    pipeline = [
        {"$match": {
            "timestamp": {"$gte": start_datetime, "$lte": end_datetime}
        }},
        {"$bucket": {
            "groupBy": {"$subtract": [
                {"$toLong": "$timestamp"},
                {"$mod": [{"$toLong": "$timestamp"}, interval_duration * 1000]}
            ]},
            "boundaries": [
                start_datetime.timestamp() * 1000 + i * interval_duration * 1000
                for i in range(13)
            ],
            "default": "Other",
            "output": {
                "count": {"$sum": 1},
                "timestamp": {"$first": "$timestamp"}
            }
        }},
        {"$project": {
            "_id": 0,
            "Timestamp": {
                "$dateToString": {
                    "format": "%Y-%m-%d %H:%M:%S",
                    "date": "$timestamp"
                }
            },
            "Number of Requests": "$count"
        }},
        {"$sort": {"Timestamp": 1}}
    ]

    # Execute the aggregation pipeline
    result = list(raw_logs_collection.aggregate(pipeline))

    # Convert the result to a DataFrame
    if result:
        data = pd.DataFrame(result)
        data["Timestamp"] = pd.to_datetime(data["Timestamp"])
        data["Adjusted Timestamp"] = data["Timestamp"] + timedelta(hours=7)
        data["Timestamp"] = data["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        data = pd.DataFrame(columns=["Timestamp", "Number of Requests"])

    # Fill in missing intervals
    if len(data) < 12:
        time_ranges = [
            start_datetime + timedelta(seconds=i * interval_duration)
            for i in range(13)
        ]
        filled_data = pd.DataFrame({
            "Timestamp": [
                (start_datetime + timedelta(seconds=i * interval_duration)).strftime("%Y-%m-%d %H:%M:%S")
                for i in range(12)
            ],
            "Adjusted Timestamp": [
                (start_datetime + timedelta(seconds=i * interval_duration) + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
                for i in range(12)
            ],
            "Number of Requests": 0
        })
        for i, row in data.iterrows():
            idx = min(range(12), key=lambda j: abs(datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S") - time_ranges[j]))
            filled_data.at[idx, "Number of Requests"] = row["Number of Requests"] 
            
        data = filled_data[filled_data['Number of Requests'] != 0]
    return data

def top_api_used(client, start_datetime, end_datetime):
    query = {
        "timestamp": {
            "$gte": start_datetime,
            "$lte": end_datetime
        },
        "api_name" : {
            '$ne' : ''
        }
    }

    # Reference the collection
    structure_logs_collection = client["structure_logs"]

    # Define the aggregation pipeline
    pipeline = [
        {"$match": query},
        {"$match": {"api_name": {"$exists": True}}},
        {"$group": {"_id": "$api_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    # Execute the aggregation pipeline
    result = structure_logs_collection.aggregate(pipeline)

    # Convert the result to a list of tuples and then to a DataFrame
    sorted_api_counts = [(doc["_id"], doc["count"]) for doc in result]
    data = pd.DataFrame(sorted_api_counts, columns=["API name", "Num Of call"])

    return data

def req_insight(client, start_datetime, end_datetime):
    query = {
        "timestamp": {
            "$gte": start_datetime,
            "$lte": end_datetime
        }
    }

    # Reference the collection
    raw_logs_collection = client["raw_logs"]

    # Define the aggregation pipeline
    pipeline = [
        {"$match": query},
        {"$sort": {"timestamp": 1}},
        {"$group": {
            "_id": None,
            "first_timestamp": {"$first": "$timestamp"},
            "last_timestamp": {"$last": "$timestamp"},
            "total_requests": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "total_requests": 1,
            "time_diff_seconds": {
                "$divide": [
                    {"$subtract": ["$last_timestamp", "$first_timestamp"]},
                    1000
                ]
            }
        }},
        {"$project": {
            "total_requests": 1,
            "requests_per_second": {
                "$cond": {
                    "if": {"$eq": ["$time_diff_seconds", 0]},
                    "then": 0,
                    "else": {"$divide": ["$total_requests", "$time_diff_seconds"]}
                }
            }
        }}
    ]

    # Execute the aggregation pipeline
    result = list(raw_logs_collection.aggregate(pipeline))

    if not result:
        return [0, 0.0]

    total_requests = result[0]["total_requests"]
    requests_per_second = round(result[0]["requests_per_second"], 5)

    return [total_requests, requests_per_second]

def process_aggregation_results(results):
    message_counts = {}
    for doc in results:
        message = doc["_id"]
        count = doc["count"]
        message_counts[message] = count

    sorted_messages = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)
    total_messages = sum(count for _, count in sorted_messages)
    ratios = [{"message": message, "count": count, "ratio": count / total_messages} for message, count in sorted_messages]

    return ratios

def calculate_message_ratios(client, start_datetime, end_datetime):
    # Part 1: Execute MongoDB aggregation pipeline
    pipeline_part1 = [
        {"$match": {"timestamp": {"$gte": start_datetime, "$lte": end_datetime}}},
        {"$group": {"_id": "$message", "count": {"$sum": 1}}}
    ]
    results_part1 = list(client["raw_logs"].aggregate(pipeline_part1))

    # Part 2: Process aggregation results using Python
    ratios = process_aggregation_results(results_part1)

    return ratios

def log_patttern_recognition(client, start_datetime, end_datetime):
  pipeline = [
    {
      '$match': {
          'timestamp': {
            '$gte': start_datetime,
            '$lte': end_datetime
          },
      }
    },
    {
      '$project': {
          '_id': 0,
          'message': 1
      }
    },
  ]

  raw_logs_data = list(client['raw_logs'].aggregate(pipeline))
  log_messsages = [log['message'] for log in raw_logs_data]

  # Logmine machine
  result = pattern_recognition(log_messsages)
  return result