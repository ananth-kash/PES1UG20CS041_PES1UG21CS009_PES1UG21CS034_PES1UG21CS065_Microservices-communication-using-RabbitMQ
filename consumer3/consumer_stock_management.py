import pika
import mysql.connector
import json
import logging

logging.basicConfig(level=logging.INFO)

def update_item_quantity(cursor, item_id, quantity):
    cursor.execute("UPDATE items SET quantity = quantity + %s WHERE itemID = %s", (quantity, item_id))

def update_item_quantity2(cursor, item_id, quantity):
    cursor.execute("UPDATE items SET quantity = %s WHERE itemID = %s", (quantity, item_id))



def handle_inventory_creation(message_data):
    try:
        cnx = mysql.connector.connect(user='root', password='badyal2003',
                                      host='mysql', database='cc_project')
        cursor = cnx.cursor()
        item_data = json.loads(message_data)
        item_id = item_data['id']
        quantity = item_data['quantity']
        update_item_quantity(cursor, item_id, quantity)
        logging.info("Item quantity updated in inventory manager: %s", item_data)
        cnx.commit()
    except mysql.connector.Error as err:
        logging.error("MySQL error: %s", err)
    except Exception as e:
        logging.error("Error: %s", e)
    finally:
        cursor.close()
        cnx.close()

def handle_order_processing(message_data):
    try:
        cnx = mysql.connector.connect(user='root', password='badyal2003',
                                      host='mysql', database='cc_project')
        cursor = cnx.cursor()
        order_data = json.loads(message_data)
        for item_id, quantity in order_data.items():
            cursor.execute("SELECT quantity FROM items WHERE itemID = %s", (item_id,))
            current_quantity = cursor.fetchone()[0]
            logging.info("fetched quantity: %s", current_quantity)
            updated_quantity = current_quantity - quantity
            logging.info("updated quantity: %s", updated_quantity)
            if updated_quantity < 0:
                logging.warning("Stock insufficient for order: %s", order_data)
                channel.basic_publish(exchange='', routing_key='stock_to_order', body="unsuccessful")
                return
            else:
                update_item_quantity2(cursor, item_id, updated_quantity)
        logging.info("Inventory managed for order: %s", order_data)
        channel.basic_publish(exchange='', routing_key='stock_to_order', body=json.dumps(order_data))
        cnx.commit()
    except mysql.connector.Error as err:
        logging.error("MySQL error: %s", err)
    except Exception as e:
        logging.error("Error: %s", e)
    finally:
        cursor.close()
        cnx.close()

def callback(ch, method, properties, body):
    message_data = body.decode('utf-8')
    if method.routing_key == 'forward_to_inventory_manager':
        handle_inventory_creation(message_data)
    elif method.routing_key == 'order_to_stock':
        print("works")
        handle_order_processing(message_data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

channel.basic_consume(queue='forward_to_inventory_manager', on_message_callback=callback)
channel.basic_consume(queue='order_to_stock', on_message_callback=callback)

logging.info('Inventory Manager Microservice is waiting for messages...')
channel.start_consuming()
