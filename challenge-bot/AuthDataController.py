import json
import os

FILENAME = os.path.join('./data/credentials.json')

def save_credentials(response):
    json_response = json.loads(response)

    if not os.path.exists('./data'):
        os.makedirs('./data')
    # and keyword has short circuit behavior -> if the first condition isn't met the second one is not evaluated 
    if os.path.exists(FILENAME) and os.path.getsize(FILENAME) != 0:
        with open(FILENAME, 'r') as f:
            data = json.load(f)
            for i in range(len(data)):
                if data[i]["athlete"]["id"] == json_response["athlete"]["id"]:
                    data[i] = json_response
                    break
            else:
                data.append(json_response)     
    else:
        data = [json_response]

    with open(FILENAME, 'w') as f:
        json.dump(data, f, default=serialize, indent=4)

def load_credentials():
    if os.path.exists(FILENAME) and os.path.getsize(FILENAME) != 0:
        with open(FILENAME, 'r') as f:
            credentials = json.load(f)
        return credentials
    return None

def serialize(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    elif isinstance(obj, dict):
        return {str(k): serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize(i) for i in obj]
    else:
        return obj
