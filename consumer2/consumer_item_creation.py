# consumer_item_creation.py
'''
import pika
import mysql.connector
import json
import time
import logging
time.sleep(20)


connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

logging.basicConfig(level=logging.INFO)
# channel.basic_consume(queue='heath2C2', auto_ack=True)
# channel.basic_publish(queue='heath2C2', body="yeah I'm running")
'''
# def callback2(ch, method, properties, body):
#     print("Received health check request:", body.decode())
#     # Process the health check request
#     # Respond back to health_check if Consumer2 is running
#     channel.basic_publish(exchange='', routing_key='response', body="Yeah")

# # Consume messages
# channel.basic_consume(queue='health2C2', on_message_callback=callback2, auto_ack=True)

# print('Waiting for health check requests from health_check...')
# channel.start_consuming()
'''

def create_item(item_data):
    try:
        cnx = mysql.connector.connect(user='root', password='Akshay*1',
                                      host='mysql', database='cc_project')
        cursor = cnx.cursor()
        # Extract item details from the message
        item_id = item_data["id"]
        name = item_data["name"]
        quantity = item_data["quantity"]
        price = item_data["price"]
        # Check if item already exists
        cursor.execute("SELECT COUNT(*) FROM items WHERE itemID = %s", (item_id,))
        count = cursor.fetchone()[0]
        logging.info("  INSIDE CREATE ITEM, COUNT = %s",str(count))
        logging.info("  RESULT = %s",str(cursor.fetchone()))
        if count == 0:
            cursor.execute("INSERT INTO items (itemID, name, price, quantity) VALUES (%s, %s, %s, %s)",
                           (item_id, name, price, quantity))  # Fixing the order of parameters
            logging.info("Item created:", item_data)
        else:
            cursor.execute("SELECT itemID, name, price FROM items WHERE itemID = %s", (item_id,))
            result = cursor.fetchone()  # Assuming you only expect one row
            logging.info("    INSIDE ELSE !!!                                  ")
            logging.info(result)
            logging.info("  RESULT = %s %s %s ",str(result[0]),str(result[1]),str(result[2]) )
            if item_id == str(result[0]) and name == str(result[1]) and float(price) == result[2]:
            # Forward the message to the inventory manager queue
                channel.basic_publish(exchange='', routing_key='forward_to_inventory_manager', body=json.dumps(item_data))
                print("Item with ID", item_id, "already exists, message forwarded to inventory manager queue.")
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as e:
        print("Error:", e)

def callback(ch, method, properties, body):
    item_data = json.loads(body)
    create_item(item_data)

channel.basic_consume(queue='item_creation_queue', on_message_callback=callback, auto_ack=True)

print('Item Creation Microservice is waiting for messages...')
channel.start_consuming()
'''


import pika
import mysql.connector
import json
import time
import logging
import threading

logging.basicConfig(level=logging.INFO)
time.sleep(20)

def create_item(item_data):
    try:
        cnx = mysql.connector.connect(user='root', password='Akshay*1',
                                      host='mysql', database='cc_project')
        cursor = cnx.cursor()
        # Extract item details from the message
        item_id = item_data["id"]
        name = item_data["name"]
        quantity = item_data["quantity"]
        price = item_data["price"]
        # Check if item already exists
        cursor.execute("SELECT COUNT(*) FROM items WHERE itemID = %s", (item_id,))
        count = cursor.fetchone()[0]
        logging.info("INSIDE CREATE ITEM, COUNT = %s", str(count))
        if count == 0:
            cursor.execute("INSERT INTO items (itemID, name, price, quantity) VALUES (%s, %s, %s, %s)",
                           (item_id, name, price, quantity))  # Fixing the order of parameters
            logging.info("Item created: %s", item_data)
        else:
            cursor.execute("SELECT itemID, name, price FROM items WHERE itemID = %s", (item_id,))
            result = cursor.fetchone()  # Assuming you only expect one row
            logging.info("INSIDE ELSE !!!")
            logging.info(result)
            logging.info("RESULT = %s %s %s ", str(result[0]), str(result[1]), str(result[2]))
            if item_id == str(result[0]) and name == str(result[1]) and float(price) == result[2]:
                logging.info("Item with ID %s already exists, message forwarded to inventory manager queue.", item_id)
                # Forward the message to the inventory manager queue
                channel.basic_publish(exchange='', routing_key='forward_to_inventory_manager', body=json.dumps(item_data))
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as e:
        logging.error("Error: %s", e)

def callback(ch, method, properties, body):
    item_data = json.loads(body)
    create_item(item_data)

def health_check():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='health2C2')

        while True:
            # Publish a message indicating Consumer2 is running to the health check queue
            channel.basic_publish(exchange='', routing_key='health2C2', body="Consumer2 is running")
            logging.info("Health check message sent to health2C2")
            time.sleep(30)  # Adjust the interval as needed
    except Exception as e:
        logging.error("Error in health check: %s", e)

# Start the health check thread
health_check_thread = threading.Thread(target=health_check)
health_check_thread.daemon = True  # Daemonize the thread so it exits when the main thread exits
health_check_thread.start()

# Main function
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='item_creation_queue')

channel.basic_consume(queue='item_creation_queue', on_message_callback=callback, auto_ack=True)

print('Item Creation Microservice is waiting for messages...')
channel.start_consuming()
