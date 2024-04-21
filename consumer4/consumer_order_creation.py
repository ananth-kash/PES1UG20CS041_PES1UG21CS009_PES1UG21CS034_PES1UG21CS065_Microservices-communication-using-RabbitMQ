import pika
import mysql.connector
import json
import logging

logging.basicConfig(level=logging.INFO)

# Establish RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()



# Establish MySQL connection
cnx = mysql.connector.connect(user='root', password='badyal2003',
                                  host='mysql', database='cc_project')
cursor = cnx.cursor()

# Function to process order messages from order_queue
def process_order_message(order_data):
    try:
        # Forward the order message to stock manager
        channel.basic_publish(exchange='', routing_key='order_to_stock', body=order_data)
        logging.info("Order forwarded to stock manager: %s", order_data)
    except Exception as e:
        logging.error("Error forwarding order to stock manager: %s", e)

# Function to calculate total price after receiving response from stock manager
def calculate_total_price(order_data):
    try:
        order = json.loads(order_data)
        total_price = 0
        for item in order:
            item_id = item['id']
            quantity = int(item['quantity'])
            cursor.execute("SELECT price FROM items WHERE itemID = %s", (item_id,))
            item_price = cursor.fetchone()[0]
            total_price += item_price * quantity
        logging.info("Order processed successfully. Total price: %s", str(total_price))
        channel.basic_publish(exchange='', routing_key='bill_data', body=str(total_price))

    except mysql.connector.Error as err:
        logging.error("MySQL error: %s", err)
    except Exception as e:
        logging.error("Error calculating total price: %s", e)


# Callback function for consuming messages from order_queue
def order_callback(ch, method, properties, body):
    order_data = body.decode('utf-8')
    process_order_message(order_data)

# Callback function for consuming messages from stock_to_order
def stock_callback(ch, method, properties, body):
    order_data = body.decode('utf-8')
    calculate_total_price(order_data)
    logging.info("consumed message from stock_to_order")

# Consume messages from order_queue
channel.basic_consume(queue='order_queue', on_message_callback=order_callback, auto_ack=True)

# Consume messages from stock_to_order
channel.basic_consume(queue='stock_to_order', on_message_callback=stock_callback, auto_ack=True)

# Start consuming
print('Order Processing Microservice is waiting for messages...')
channel.start_consuming()

# Close connections
cursor.close()
cnx.close()
