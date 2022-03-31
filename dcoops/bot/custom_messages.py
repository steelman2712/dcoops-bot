import discord
from discord.ext import commands
from discord.errors import ClientException
from sqlalchemy import exists

from dcoops.bot.tts import tts_to_file
from dcoopsdb.models import CustomMessage
from dcoopsdb.db import Session

async def default_message(name, message_type):
    if message_type == CustomMessage.JOIN_MESSAGE_TYPE:
        tts_message = f"{name} has joined the voice channel"
    elif message_type == CustomMessage.LEAVE_MESSAGE_TYPE:
        tts_message = f"{name} has left the voice channel"
    return tts_message


async def play_file(voice_client, filename):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename))
    try:
        voice_client.play(
            source, after=lambda e: print("Player error: %s" % e) if e else None
        )
    except ClientException:
        pass

async def play_tts(voice_client, message):
    await tts_to_file(message)
    await play_file(voice_client=voice_client, filename="tts.mp3")

async def send_message(voice_client, member, message_type):
    if member.nick:
        name = member.nick
    else:
        name = member.name
    custom_message = CustomMessage().load_message(server=member.guild.id, user_id=member.id, message_type=message_type)
    if custom_message:
        tts_message = custom_message.message
        if "%name" in tts_message:
            tts_message = tts_message.replace("%name", name)
        print(tts_message)
    else:
        tts_message = await default_message(name, message_type)
    await play_tts(voice_client=voice_client, message=tts_message)

async def join_message(voice_client, member):
    await send_message(voice_client, member, CustomMessage.JOIN_MESSAGE_TYPE)

async def leave_message(voice_client, member):
    await send_message(voice_client, member, CustomMessage.LEAVE_MESSAGE_TYPE)

async def set_message(ctx, message, message_type):
    try:
        server = ctx.guild.id
        user_id = ctx.author.id
        print(user_id)
        with Session() as session:
            existing = session.query(CustomMessage).filter_by(user_id=user_id).filter_by(server=server).filter_by(message_type=message_type).first()
            if existing:
                existing.message = message
            else:
                new_message = CustomMessage(server=server, user_id=user_id, message=message, message_type=message_type)
                session.add(new_message)
            session.commit()
            await ctx.send("Message set")
    except Exception as e:
            print(e)
            await ctx.send("Unable to set join message")


class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command()
    async def set_join_message(self, ctx, *message):
        message = " ".join(list(message))
        await set_message(ctx, message, CustomMessage.JOIN_MESSAGE_TYPE)

        
    @commands.command()
    async def set_leave_message(self, ctx, *message):
        message = " ".join(list(message))
        await set_message(ctx, message, CustomMessage.LEAVE_MESSAGE_TYPE)

