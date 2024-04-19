# producer.py
import pika
import json
import time


connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

# Declare queues
channel.queue_declare(queue='item_creation_queue')
channel.queue_declare(queue='order_queue')
channel.queue_declare(queue='item_creation_queue')
channel.queue_declare(queue='forward_to_inventory_manager')
channel.queue_declare(queue='order_to_stock') 
channel.queue_declare(queue='stock_to_order')

def send_item_creation_request(item_data):
    channel.basic_publish(exchange='', routing_key='item_creation_queue', body=json.dumps(item_data))
    print("Sent item creation request:", item_data)

def send_order(order_data):
    channel.basic_publish(exchange='', routing_key='order_queue', body=json.dumps(order_data))
    print("Sent order:", order_data)

# Example data
item_data = {"id": "1", "name": "Product A", "quantity": 10, "price": 20.0}
order_data = {"1": 5}  # Example order: 5 units of product 1, 10 units of product 2

# Send requests
#send_item_creation_request(item_data)
send_order(order_data)

connection.close()
