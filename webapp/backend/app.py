from flask import Flask, Blueprint, request, render_template, url_for, redirect
import os
import time
import pika
import asyncio
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
import json

# import os
# from steelforge_site_utils.aws_verify import verify_jwt, authed, get_user_type, verify_access_token

# while True:
#    time.sleep(10)
import sys

current_dir = os.path.dirname(__file__)
root = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
sys.path.append(root)

# from dcoopsdb.models import Bind
from webapp.backend.soundboard import Soundboard


app = Flask(__name__)
from webapp.backend.src.api import dcoops_api

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
# app.secret_key = SECRET_KEY
dcoops = Blueprint("dcoops", __name__)
# app.register_blueprint(dcoops, url_prefix="/dcoops")
app.register_blueprint(dcoops_api)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI")
app.config["DISCORD_BOT_TOKEN"] = os.getenv("DISCORD_BOT_TOKEN")


discord = DiscordOAuth2Session(app)

print("Started")


@dcoops.route("/login")
def login():
    return discord.create_session()


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("dcoops.login"))


@dcoops.route("/login-redirect")
def callback():
    discord.callback()
    return redirect(url_for(".me"))


@dcoops.route("/me/")
@requires_authorization
def me():
    user = discord.fetch_user()
    return f"""
    <html>
        <head>
            <title>{user.name}</title>
        </head>
        <body>
            <img src='{user.avatar_url}' />
        </body>
    </html>"""


@dcoops.route("/guilds")
@requires_authorization
def guilds():
    guilds = discord.fetch_guilds()
    guild_json = [guild_to_json(guild) for guild in guilds]
    return json.dumps(guild_json)


def guild_to_json(guild):
    guild_info = {"id": guild.id, "name": guild.name, "icon": guild.icon_url}
    return guild_info


@dcoops.route("/soundboard")
@requires_authorization
def soundboard():
    # guild = discord.fetch_guilds()[0]
    server = os.environ.get("TEST_SERVER")
    binds = Soundboard().load_bind_names(server)
    return render_template("soundboard.html", binds=binds, server=server)


# background process happening without any refreshing
@dcoops.route("/play_sound", methods=["POST"])
@requires_authorization
def background_process_test():
    bind = request.form["id"]
    # server = request.form["server"]
    print(bind)
    send_rabbit(f"groans {bind}")
    return "Playing bind"


@dcoops.route("/hello-world", methods=["GET"])
def hello_world():
    return "ping"


@dcoops.route("/ping", methods=["GET"])
def ping():
    print(app.url_map)
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return f"ping - {current_time}"


@dcoops.route("/groans", methods=["GET"])
def groans():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    send_rabbit("groans")
    return f"groans - {current_time}"


@dcoops.route("/tts", methods=["GET", "POST"])
def tts():
    if request.method == "GET":
        return render_template("basic_form.html")
    else:
        text = request.form["text"]
        send_rabbit(text)
        return f"Sent tts of {text}"


def connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitMQ"))
    channel = connection.channel()

    channel.queue_declare(queue="hello")

    channel.basic_publish(exchange="", routing_key="hello", body="Hello World!")
    print(" [x] Sent 'Hello World!'")
    connection.close()


def get_connection():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitMQ"))
    return conn


def send_rabbit(message):
    asyncio.set_event_loop(asyncio.new_event_loop())
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue="hello")

    channel.basic_publish(exchange="", routing_key="hello", body=message)
    print(" [x] Sent 'Hello World!'")
    connection.close()


if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == "__main__":
    app.run()

app.register_blueprint(dcoops, url_prefix="/dcoops")
