from flask import Flask, Blueprint
import os
import time
import pika
import asyncio
from threading import Thread


# import os
# from steelforge_site_utils.aws_verify import verify_jwt, authed, get_user_type, verify_access_token

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

app = Flask(__name__)
# app.secret_key = SECRET_KEY
dcoops = Blueprint("dcoops", __name__)


print("Started")


@dcoops.route("/hello-world", methods=["GET"])
def hello_world():
    return "ping"


@dcoops.route("/ping", methods=["GET"])
def ping():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return f"ping - {current_time}"

@dcoops.route("/groans", methods=["GET"])
def groans():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    send_rabbit()
    return f"groans - {current_time}"




def connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitMQ'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
    print(" [x] Sent 'Hello World!'")
    connection.close()

def get_connection():
    credentials = pika.PlainCredentials('guest', 'guest')
    conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitMQ'))
    return conn

def send_rabbit():
    asyncio.set_event_loop(asyncio.new_event_loop())
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
    print(" [x] Sent 'Hello World!'")
    connection.close()

if __name__=="__main__":
    app.run()
    
app.register_blueprint(dcoops, url_prefix="/dcoops")