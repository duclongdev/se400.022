from logmine_pkg import log_mine
import io
from datetime import datetime
from pymongo import MongoClient
buffer = io.StringIO()

lm = log_mine.LogMine(
  { 'single_core': True },
  {
    'max_dist': 0.6,
    'delimeters': '\s+',
    'min_members': 2,
    'k1': 1,
    'k2': 1,
    'variables': [
      '<time>:/\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\]',
      '<processed_time>:/\[(\d+)ms\]',
      '<elapsed_time>:/\+(\d+)?ms']
  },
  {
    'sorted': 'desc',
    'highlight_patterns': False,
    'highlight_variables': False,
    'mask_variables': True,
    'number_align': True
  }
) # pass the usual parameters
lm.output.set_output_file(file=buffer)

# Connect to MongoDB & Read the logs
client = MongoClient('localhost', 27017)
raw_logs_collection = client['logs']['raw_logs']
query = {
  "timestamp": {
    "$gte": datetime.strptime('2024-01-31T17:00:00.000Z', "%Y-%m-%dT%H:%M:%S.%fZ"),
    "$lte": datetime.strptime('2024-01-31T20:00:00.000Z', "%Y-%m-%dT%H:%M:%S.%fZ")
  }
}

arr = []
cursor_anomaly_logs = raw_logs_collection.find(query)
for document in cursor_anomaly_logs:
  arr.append(document['message'])

# a = lm.run(files=None, data=arr)
# print(buffer.getvalue())
# print(a)

def pattern_recognition(input):
  total_lines = len(input)

  result = lm.run(files=None, data=input)

  # Calculate the percentage of the pattern recognition
  for item in result:
    count = item['count']
    percent = (count / total_lines) * 100
    item['percent'] = percent

  # Convert ansi2html
  return result


