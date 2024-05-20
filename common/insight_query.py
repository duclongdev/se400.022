from pymongo import MongoClient
from datetime import datetime, timedelta
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

# def req_datetime_timeseries(client, start_datetime, end_datetime):
#     interval = (end_datetime - start_datetime) / 12
#     segment_start = start_datetime + 1 * interval
#     segment_end = segment_start + interval
#     query = {
#         "timestamp": {
#             "$gte": segment_start,
#             "$lte": segment_end
#         }
#     }

#     # Reference the collection
#     raw_logs_collection = client["raw_logs"]

#     # Define the aggregation pipeline
#     pipeline = [
#         {"$match": query},
#         {"$group": {
#             "_id": {
#                 "$dateToString": {
#                     "format": "%Y-%m-%d",
#                     "date": "$timestamp"
#                 }
#             },
#             "count": {"$sum": 1}
#         }},
#         {"$sort": {"_id": 1}},
#         {"$project": {
#             "Timestamp": "$_id",
#             "Number of Requests": "$count"
#         }}
#     ]

#     # Execute the aggregation pipeline
#     result = raw_logs_collection.aggregate(pipeline)

#     # Convert the result to a DataFrame
#     data = pd.DataFrame(list(result))
    
#     return data

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
            "Number of Requests": 0
        })
        for i, row in data.iterrows():
            idx = min(range(12), key=lambda j: abs(datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S") - time_ranges[j]))
            filled_data.at[idx, "Number of Requests"] = row["Number of Requests"]

        data = filled_data

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
  
# def calculate_message_ratios(client, start_datetime, end_datetime):
#     # Reference the collection
#     collection_raw_logs = client["raw_logs"]
    
#     # Define the query to filter data by timestamp
#     query = {
#         "timestamp": {
#             "$gte": start_datetime,
#             "$lte": end_datetime
#         }
#     }
    
#     # Define the aggregation pipeline
#     pipeline = [
#         {"$match": query},
#         {"$group": {
#             "_id": "$message",
#             "count": {"$sum": 1}
#         }},
#         {"$sort": {"count": -1}},
#         {"$group": {
#             "_id": None,
#             "total_messages": {"$sum": "$count"},
#             "messages": {"$push": {"message": "$_id", "count": "$count"}}
#         }},
#         {"$unwind": "$messages"},
#         {"$project": {
#             "_id": 0,
#             "message": "$messages.message",
#             "count": "$messages.count",
#             "ratio": {"$divide": ["$messages.count", "$total_messages"]}
#         }},
#         {"$sort": {"count": -1}}
#     ]
    
#     # Execute the aggregation pipeline with allowDiskUse=True
#     result = list(collection_raw_logs.aggregate(pipeline, allowDiskUse=True))
    
#     # Return the result
#     return result
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