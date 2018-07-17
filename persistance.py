import datetime
import jsonpickle
import orders

def save_orders(orders):
    filename = get_filename()
    with open(filename, 'w') as fp:
        json = jsonpickle.encode(orders)
        fp.write(json)

def load_orders():
    filename = get_filename()
    try:
        with open(filename, 'r') as fp:
            json = fp.read()
            return jsonpickle.decode(json)
    except:
        return orders.Orders()

def get_filename():
    return str(datetime.date.today()) + '-orders.bak'