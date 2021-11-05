from discord.ext import commands

from dcoopsdb.models import File, Bind
from dcoopsdb.db import Session


def list_items(item_class, server):
    with Session() as session:
        try:
            db_query = session.query(item_class).filter_by(server=server)
            files = db_query.all()
            if len(files) == 0:
                output_text = "Nothing found"
            else:
                output_text = "\n".join((item.alias) for item in files)
            return output_text
        except Exception:
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
        except Exception:
            await ctx.send("Could not retrieve the list of files")

    @commands.command()
    async def list_binds(self, ctx):
        """Lists binds"""
        server = ctx.guild.id
        try:
            output_text = list_items(Bind, server)
            await ctx.send(f"`{output_text}`")
        except Exception:
            await ctx.send("Could not retrieve the list of files")

    @commands.command()
    async def list_groans(self, ctx):
        server = ctx.guild.id
        with Session() as session:
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
