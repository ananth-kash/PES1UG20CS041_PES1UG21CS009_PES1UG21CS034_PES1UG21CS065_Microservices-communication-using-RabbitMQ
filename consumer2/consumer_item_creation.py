# consumer_item_creation.py
import pika
import mysql.connector
import json
import time
time.sleep(20)


connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()



def create_item(item_data):
    try:
        cnx = mysql.connector.connect(user='root', password='badyal2003',
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
        if count == 0:
            cursor.execute("INSERT INTO items (itemID, name, price, quantity) VALUES (%s, %s, %s, %s)",
                           (item_id, name, price, quantity))  # Fixing the order of parameters
            print("Item created:", item_data)
        else:
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
