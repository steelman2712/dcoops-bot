from files import Binds, Files
from music import YTDLSource
import os
from discord.ext import commands
import imgur
import discord

CACHE_LOCATION = "video-cache"


class Groans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def yt_groans(self, ctx, url, start, stop, *, alias):
        """Creates a bind and file from a youtube video.
        Format: !yt_groan video-url start stop groan-name"""
        async with ctx.typing():
            if await self.groan_exists(ctx, alias):
                return await ctx.send("Groan already exists *groans*")
            else:
                filename = await YTDLSource.video_details(url)
                if await self.is_cached(filename):
                    print("Getting cached video")
                    uncropped_file = filename
                else:
                    print("Not cached")
                    uncropped_file = await YTDLSource.yt_video_download(url)
                print(uncropped_file)
                filename = os.path.splitext(uncropped_file)[0]
                extension = os.path.splitext(uncropped_file)[1]
                cropped_video_name = f"{filename}+_cropped_video{extension}"
                cropped_audio_name = f"{filename}+_cropped_audio.mp3"
                cropped_video = await YTDLSource.crop_video(
                    input=uncropped_file,
                    output=cropped_video_name,
                    start=start,
                    stop=stop,
                )
                cropped_audio = await YTDLSource.crop(
                    input=uncropped_file,
                    output=cropped_audio_name,
                    start=start,
                    stop=stop,
                )
                print(cropped_video)
                imgur_link = await imgur.upload_video(cropped_video)
                my_file = discord.File(cropped_audio)
                message = await ctx.send(file=my_file)
                cdn_url = message.attachments[0].url
                await Binds().upload_bind(ctx, cdn_url, alias)
                message = await ctx.send(imgur_link)
                # await self.play(ctx=ctx,query=cdn_url)
                await ctx.invoke(
                    self.bot.get_command("upload_embed"), url=imgur_link, alias=alias
                )
                # os.remove(uncropped_file)
                os.remove(cropped_video_name)
                os.remove(cropped_audio_name)

    async def groan_exists(self, ctx, alias):
        file_exists = await Files(self.bot).exists(ctx, alias)
        bind_exists = await Binds().exists(ctx, alias)
        print(file_exists)
        print(bind_exists)
        if file_exists or bind_exists:
            return True
        else:
            return False

    async def is_cached(self, filename):
        root_dir = os.path.dirname(os.path.dirname(__file__))
        cache_directory = os.path.join(root_dir, CACHE_LOCATION)
        filepath = os.path.join(cache_directory, filename)
        if os.path.isfile(filepath):
            return True
        else:
            return False

    @commands.command()
    async def delete_groans(self, ctx, alias):
        await ctx.invoke(self.bot.get_command("delete_file"), alias=alias)
        await ctx.invoke(self.bot.get_command("delete_bind"), alias=alias)
        await ctx.send(f"Deleted groan {alias}")
