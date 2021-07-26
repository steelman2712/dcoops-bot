import discord

from discord.ext import commands

from models.models import File, Bind
from models.db import session_scope


def list_items(item_class, server):
    with session_scope() as session:
        try:
            db_query = session.query(item_class).filter_by(server=server)
            files = db_query.all()
            if len(files) == 0:
                output_text = "Nothing found"
            else:
                output_text = "\n".join((item.alias) for item in files)
            return output_text
        except:
            raise


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def list_files(self, ctx):
        """Lists files"""
        server = ctx.guild.id
        try:
            output_text = list_items(File, server)
            await ctx.send(f"`{output_text}`")
        except:
            await ctx.send("Could not retrieve the list of files")

    @commands.command()
    async def list_binds(self, ctx):
        """Lists binds"""
        server = ctx.guild.id
        try:
            output_text = list_items(Bind, server)
            await ctx.send(f"`{output_text}`")
        except:
            await ctx.send("Could not retrieve the list of files")

    @commands.command()
    async def list_groans(self, ctx):
        server = ctx.guild.id
        with session_scope() as session:
            # try:
            for files, binds in (
                session.query(File, Bind)
                .join(File.alias == Bind.alias)
                .filter_by(server=server)
                .all()
            ):
                print(files)
                files = files.alias
                if len(files) == 0:
                    output_text = "Nothing found"
                else:
                    output_text = "\n".join((item.alias) for item in files)
                await ctx.send(f"`{output_text}`")
            # except:
            # await ctx.send("Could not retrieve the list of files")

    """ @commands.command()
    async def reload_binds(self,ctx):
        server = ctx.guild.id 
        reloaded_binds = []
        for channels in ctx.guild.channels:
            print(channels.name)
            if channels.name == "safe-groan-zone":
                channel = channels
        async for message in channel.history(limit=1500):
            if message.content.startswith("!yt_groans "):
                try:
                    content = message.content.split()
                    url = content[1]
                    start = content[2]
                    stop = content[3]
                    alias = content[4]
                    print(url)
                    print(start)
                    print(stop)
                    print(alias)
                    if all(v is not None for v in [url,start,stop,alias]):
                        if alias not in reloaded_binds:
                            reloaded_binds.append(alias) 
                            await ctx.invoke(self.bot.get_command('delete_bind'), alias=alias)
                            await ctx.invoke(self.bot.get_command('yt_bind'), url=url,start=start,stop=stop,alias=alias)
                            await asyncio.sleep(10)
                
                except Exception as e:
                    print(e)
                    print("Couldn't do") """
