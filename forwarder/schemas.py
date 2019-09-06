import json


def load_event_data(json_msg):
    event_key = b'event'
    if event_key not in json_msg:
        event_key = 'event'
    event_json = json_msg.get(event_key, '{}')
    return json.loads(event_json)


def event_data_to_json(event_data):
    return {'event': json.dumps(event_data)}
