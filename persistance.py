import json
import datetime

def save_orders_dict(dict):
    filename = get_filename()
    with open(filename, 'w') as fp:
        json.dump(dict, fp)

def load_orders_dict():
    filename = get_filename()
    try:
        with open(filename, 'r') as fp:
            return json.load(fp)
    except:
        return {}

def get_filename():
    return str(datetime.date.today()) + '-orders.bak'