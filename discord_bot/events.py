import discord
from discord.ext import commands
from music import audio_source_from_query
from tts import tts_to_file

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel = after.channel
        if channel is None:
            channel = before.channel
        if channel is None:
            return
        else:
            await self.ensure_voice(channel)
            server = member.guild.id
            voice_client = member.guild.voice_client
            if member.nick:
                name = member.nick
            else:
                name = member.name
            if before.channel is None:
                await tts_to_file(f"{name} has joined the voice channel")
                await self.play_file(voice_client = voice_client)
            elif after.channel is None:
                await tts_to_file(f"{name} has left the bloody bastard voice channel")
                await self.play_file(voice_client = voice_client)
            else:
                return
            #await self.play_groan(server=server, voice_client = voice_client, groan="groans")

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        print(message)
        print(message.attachments)
        attachment_urls = None
        if message.attachments:
            attachment_url_list = [attachment.url for attachment in message.attachments]
            attachment_urls = " ".join(attachment_url_list)
            print(attachment_urls)
        channel = message.channel
        author = message.author.name
        if attachment_urls:
            message = f"{author} deleted message. Message contents: {message.content}. Attached file(s): {attachment_urls}"
        else:
            message = f"{author} deleted message. Message contents: {message.content}"
        await self.send_message(channel,message)

    @commands.Cog.listener()
    async def on_message_edit(self,before,after):
        print(before)
        print(after)



    async def play_groan(self, server, voice_client, groan="groans"):
        source = await audio_source_from_query(server = server, query = groan)
        voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    async def play_file(self, voice_client, filename = "tts.mp3"):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename))
        voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    async def send_message(self, channel, message):
        await channel.send(message)

    
    async def ensure_voice(self, channel):
        member_ids = [members.id for members in channel.members]
        bot_id = self.bot.user.id
        if bot_id not in member_ids:
            await channel.connect()