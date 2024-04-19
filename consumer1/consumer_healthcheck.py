# health_check_microservice.py
import time
import pika
import mysql.connector


time.sleep(30)
def check_health():
    try:
        # Check RabbitMQ connection
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        connection.close()
        print("RabbitMQ is healthy.")

        # Check MySQL connection
        cnx = mysql.connector.connect(user='root', password='badyal2003', host='mysql', database='cc_project')
        cursor = cnx.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchall()
        cursor.close()
        cnx.close()
        print("MySQL is healthy.")
    except Exception as e:
        print("Error:", e)

while True:
    check_health()
    time.sleep(60)  # Check health every 60 seconds
