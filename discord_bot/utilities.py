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
                    output_text = "No files found"
                else:
                    output_text = '\n'.join((item.alias) for item in files)
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
            output_text = list_items(File,server)
            await ctx.send(f"`{output_text}`")
        except:
            await ctx.send("Could not retrieve the list of files")

    @commands.command()
    async def list_binds(self, ctx):
        """Lists binds"""
        server = ctx.guild.id 
        try:
            output_text = list_items(Bind,server)
            await ctx.send(f"`{output_text}`")
        except:
            await ctx.send("Could not retrieve the list of files")
    