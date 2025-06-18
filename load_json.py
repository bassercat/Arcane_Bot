import json
import os

json_data={}


def load_json(ENV):

  global json_data

  json_path = os.path.abspath(
      os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
  )
  with open(json_path, 'r') as f:
    json_data1 = json.load(f)

  if ENV == 'local':
    pass
  elif ENV == 'colab':
    json_data1['MAIN'] = json_data1['MAIN_2']
    json_data1['CHANNEL_IDS'] = json_data1['CHANNEL_IDS_2']
  else:
    print("load_json error")
    return

  json_data.clear()
  json_data.update(json_data1)
