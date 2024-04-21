# producer.py
import pika
import json
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

# Declare queues
channel.queue_declare(queue='item_creation_queue')
channel.queue_declare(queue='order_queue')
channel.queue_declare(queue='item_creation_queue')
channel.queue_declare(queue='forward_to_inventory_manager')
channel.queue_declare(queue='order_to_stock') 
channel.queue_declare(queue='stock_to_order')
channel.queue_declare(queue='bill_data')

app = Flask(__name__)
socketio = SocketIO(app)



@app.route('/')
def index():
    return render_template('index.html')
@app.route('/create_item_page')
def create_item_page():
    return render_template('create_item.html')

@app.route('/place_order_page')
def place_order_page():
    return render_template('place_order.html')


@app.route('/create_item', methods=['POST'])
def create_item():
    ids = request.form.getlist('id[]')
    names = request.form.getlist('name[]')
    quantities = request.form.getlist('quantity[]')
    prices = request.form.getlist('price[]')

    items_data = []
    for id, name, quantity, price in zip(ids, names, quantities, prices):
        items_data.append({"id": id, "name": name, "quantity": int(quantity), "price": float(price)})
        item_data = {"id": id, "name": name, "quantity": int(quantity), "price": float(price)}
        channel.basic_publish(exchange='', routing_key='item_creation_queue', body=json.dumps(item_data))

    return "Item creation requests sent successfully."

@app.route('/place_order', methods=['POST'])
def place_order():
    item_ids = request.form.getlist('item_id[]')
    quantities = request.form.getlist('item_quantity[]')

    order_data = []
    for item_id, quantity in zip(item_ids, quantities):
        order_data.append({"id": item_id, "quantity": int(quantity)})
    order_data = json.loads(request.form['order_data'])
    channel.basic_publish(exchange='', routing_key='order_queue', body=json.dumps(order_data))
    return "Order placed successfully."

@socketio.on('connect')
def handle_connect():
    print('Client connected')

def callback(ch, method, properties, body):
    message_data = body.decode('utf-8')
    print("Received message from bill_data:", message_data)
    socketio.emit('bill_data_message', message_data)

channel.basic_consume(queue='bill_data', on_message_callback=callback, auto_ack=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

