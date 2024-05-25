from .logmine_pkg import log_mine
import io
from datetime import datetime
from pymongo import MongoClient
from ansi2html import Ansi2HTMLConverter

buffer = io.StringIO()

lm = log_mine.LogMine(
  { 'single_core': True },
  {
    'max_dist': 0.6,
    'delimeters': '\s+',
    'min_members': 1,
    'k1': 1,
    'k2': 1,
    'variables': [
      '<time>:/\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\]',
      '<processed_time>:/\[(\d+)ms\]',
      '<elapsed_time>:/\+(\d+)?ms'
    ]
  },
  {
    'sorted': 'desc',
    'highlight_patterns': True,
    'highlight_variables': True,
    'mask_variables': True,
    'number_align': True
  }
) # pass the usual parameters
lm.output.set_output_file(file=buffer)

conv = Ansi2HTMLConverter()
def pattern_recognition(input):
  total_lines = len(input)

  result = lm.run(files=None, data=input)

  if result is None:
    return {'Pattern': [], 'Count': [], 'Ratio': []}

  # Calculate the percentage of the pattern recognition
  for item in result:
    item['Pattern'] = conv.convert(item['Pattern'], False)
    count = item['Count']
    percent = (count / total_lines) * 100
    item['Ratio'] = str(round(percent, 2))

  # Convert ansi2html
  return result
