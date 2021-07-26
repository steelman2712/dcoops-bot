import asyncio
import os 

import discord
import youtube_dl

from discord.ext import commands

from models.models import File, Bind
from models.db import session_scope

from files import Binds, Files
import imgur

import time
import shlex
import subprocess
import moviepy.editor as mpy
import ffmpeg

# Suppress noise about console usage from errors
CACHE_LOCATION = "video-cache"
root_dir = os.path.dirname(os.path.dirname(__file__))
cache_directory = os.path.join(root_dir,CACHE_LOCATION)
print(cache_directory)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(cache_directory,'%(extractor)s-%(id)s-%(title)s.%(ext)s'),
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl_video_options = ytdl_format_options
ytdl_video_options["format"]="bestvideo[height<=480,ext=mp4]+bestaudio[ext=m4a]/best[height<=480,ext=mp4]/best[ext=mp4]/best"

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
ytdl_video = youtube_dl.YoutubeDL(ytdl_video_options)

async def audio_source_from_query(query, server):
    with session_scope() as session:
        query = query.lower()
        try:
            db_query = session.query(Bind).filter_by(alias=query).filter_by(server=server)
            bind = db_query.one()
            session.close()
        except:
            bind = False
    if bind:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(bind.file_url))
    else:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
    return source

class YTDLSource(discord.PCMVolumeTransformer):
       
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def crop(cls, input, output, start, stop):
        ffmpeg_options = f"-vn -hide_banner -loglevel warning -ss {start} -to {stop} -i {input} -c copy -c:a libmp3lame {output} -y"
        args = ["ffmpeg"]
        args.extend(shlex.split(ffmpeg_options))
        subprocess.run(args)
        return output

    @classmethod
    async def crop_video(cls, input, output, start, stop):
        ffmpeg_options = f"-ss {start} -to {stop} -i {input} -c copy -movflags faststart {output} -y -loglevel warning -nostats"
        args = ["ffmpeg"]
        args.extend(shlex.split(ffmpeg_options))
        subprocess.run(args)
        return output

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
    
    @classmethod
    async def from_url_with_timestamp(cls, url, *, loop=None, stream=False, start=0, stop=10000):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        ffmpeg_options["options"] = f"-vn -ss {start} -to {stop}"
        await cls.crop(filename,start,stop)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def yt_download(cls,url, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = ytdl.prepare_filename(data)
        return filename

    @classmethod
    async def yt_video_download(cls,url, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl_video.extract_info(url, download=True))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = ytdl.prepare_filename(data)
        return filename

    @classmethod
    async def video_details(cls, url, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl_video.extract_info(url, download=False))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = ytdl.prepare_filename(data)
        return filename
        
class Queue():
    queue = []

    def __repr__(self):
        message = "Queue: \n"
        index = 1
        for song in self.queue:
            message += f"{index}) {song}"
        return message

    async def add(self, song):
        self.queue.append(song)
    
    async def remove(self,position):
        del queue[i-1]

    

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        server = ctx.guild.id 
        source = await audio_source_from_query(query = query, server = server)
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        #await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @commands.command()
    async def yt_bind(self, ctx, url, start, stop, *, alias):
        """Creates a bind from a youtube video.
        Format: !yt_bind video-url start stop bind-name"""
        async with ctx.typing():
            uncropped_file = await YTDLSource.yt_download(url)
            print(uncropped_file)
            filename = os.path.splitext(uncropped_file)[0]
            extension = os.path.splitext(uncropped_file)[1]
            cropped_name = f"{filename}+_out.mp3"
            cropped_file = await YTDLSource.crop(input=uncropped_file, output=cropped_name, start=start, stop=stop)
            my_file = discord.File(cropped_file) 
            message = await ctx.send(file=my_file)
            cdn_url = message.attachments[0].url
            bind = await Binds().upload_bind(ctx,cdn_url,alias)
            os.remove(uncropped_file)
            os.remove(cropped_file)
            await self.play(ctx=ctx,query=cdn_url)

    @commands.command()
    async def groans(self, ctx, alias="groans"):
        """Plays a bind and loads an image at the same time"""
        await self.play(ctx=ctx,query=alias)
        await ctx.invoke(self.bot.get_command('load'), alias=alias)

    
    
    @commands.command()
    async def yt_details(self,ctx,url):
        details = await YTDLSource.video_details(url)
        print(details)

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    @yt_bind.before_invoke
    @groans.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

