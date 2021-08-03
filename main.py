import os
from dotenv import load_dotenv
from discord.ext import commands
from pretty_help import PrettyHelp
import discord

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(".", "discord_bot")))
from music import Music
from files import Files
from utilities import Utilities
from activity import Resident
from groans import Groans
from jigsaw import Jigsaw
from events import Events, play_bind
from threading import Thread
import pika

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
bot.add_cog(Music(bot))
bot.add_cog(Files(bot))
bot.add_cog(Utilities(bot))
bot.add_cog(Resident(bot))
bot.add_cog(Groans(bot))
bot.add_cog(Jigsaw(bot))
bot.add_cog(Events(bot))


def get_connection():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitMQ"))
    return conn


async def my_event():
    try:
        server_id = 123456789
        guild = bot.get_guild(server_id)
        print(guild)
        voice_client = discord.utils.get(bot.voice_clients, guild=guild)
        print(voice_client)
        await play_bind(server=server_id, voice_client=voice_client)
    except Exception as e:
        print("Error on callback: ", e)
        return None


def callback(ch, method, properties, body):
    print(" [x] %s" % (body))
    asyncio.run(my_event())


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
    connection.close()


def run_bot(bot, token):
    bot.run(token)


if __name__ == "__main__":
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
            pass
    threadC = Thread(target=start_consumers)
    threadC.start()
    bot.run(token)
