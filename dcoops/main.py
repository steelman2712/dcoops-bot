import os
from dotenv import load_dotenv
from discord.ext import commands
from pretty_help import PrettyHelp
import discord
import time

from pathlib import Path
import sys

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

import sys
import asyncio

# sys.path.append(root_path)
from dcoops.bot.music import Music
from dcoops.bot.files import Files
from dcoops.bot.utilities import Utilities
from dcoops.bot.activity import Resident
from dcoops.bot.groans import Groans
from dcoops.bot.jigsaw import Jigsaw
from dcoops.bot.events import Events, play_bind, play_tts
from dcoops.bot.custom_messages import Messages
from threading import Thread
import pika

WEB_APP_ACTIVE = os.environ.get("WEB_APP_ACTIVE") or False
TEST_SERVER = os.environ.get("TEST_SERVER")
print("TEST SERVER: ", TEST_SERVER)

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="DCoops bot",
    case_insensitive=True,
    help_command=PrettyHelp(),
)


@bot.event
async def on_ready():
    print("Logged in as {0} ({0.id})".format(bot.user))
    print("------")


token = os.environ.get("DISCORD_TOKEN")
print(token)
bot.add_cog(Music(bot))
bot.add_cog(Files(bot))
bot.add_cog(Utilities(bot))
bot.add_cog(Resident(bot))
bot.add_cog(Groans(bot))
bot.add_cog(Jigsaw(bot))
bot.add_cog(Events(bot))
bot.add_cog(Messages(bot))


def get_connection():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitMQ"))
    return conn


async def rabbit_groans():
    try:
        server_id = TEST_SERVER
        guild = bot.get_guild(server_id)
        print(guild)
        voice_client = discord.utils.get(bot.voice_clients, guild=guild)
        print(voice_client)
        await play_bind(server=server_id, voice_client=voice_client)
    except Exception as e:
        print("Error on callback: ", e)
        return None


async def rabbit_tts():
    try:
        server_id = TEST_SERVER
        guild = bot.get_guild(server_id)
        print(guild)
        voice_client = discord.utils.get(bot.voice_clients, guild=guild)
        print(voice_client)
        await play_bind(server=server_id, voice_client=voice_client)
    except Exception as e:
        print("Error on callback: ", e)
        return None


async def on_rabbitmq_message(text):
    try:
        server_id = int(TEST_SERVER)
        print(server_id)
        guild = bot.get_guild(server_id)
        print(guild)
        voice_client = discord.utils.get(bot.voice_clients, guild=guild)
        if text.startswith("groans"):
            bind = text.split()[1] if len(text.split()) > 1 else "groans"
            await play_bind(server=server_id, voice_client=voice_client, groan=bind)
        else:
            await play_tts(voice_client=voice_client, message=text)
    except Exception as e:
        print("Error on callback: ", e)
        return None


def callback(ch, method, properties, body):
    text = body.decode("utf-8")
    print("Rabbitmq message: ", text)
    asyncio.run(on_rabbitmq_message(text))


def start_consumers():
    asyncio.set_event_loop(asyncio.new_event_loop())
    channel = get_connection().channel()
    channel.queue_declare(queue="hello")
    channel.basic_consume(queue="hello", on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


def send_rabbit():
    asyncio.set_event_loop(asyncio.new_event_loop())
    channel = get_connection().channel()

    channel.queue_declare(queue="hello")

    channel.basic_publish(exchange="", routing_key="hello", body="Hello World!")
    print(" [x] Sent 'Hello World!'")


def run_bot(bot, token):
    bot.run(token)


def start_with_webapp():
    rabbitMQ_connected = False
    while not rabbitMQ_connected:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="rabbitMQ")
            )
            print("DCoops RabbitMQ connection established")
            rabbitMQ_connected = True
            connection.close()
        except Exception:
            print("Unable to connect to RabbitMQ")
            time.sleep(1)
            pass
    threadC = Thread(target=start_consumers)
    threadC.start()
    bot.run(token)


if __name__ == "__main__":
    if WEB_APP_ACTIVE:
        start_with_webapp()
    else:
        bot.run(token)
