from discord.ext import commands

from dcoopsdb.models import File, Bind
from dcoopsdb.db import session_scope

audio_files = (".mp3", ".wav", ".ogg", ".webm", ".m4a")
from sqlalchemy.orm.exc import NoResultFound
import random


def create_file(alias, url, server):
    alias = alias.lower()
    if url.endswith(audio_files):
        db_file = Bind(alias=alias, file_url=url, server=server)
    else:
        db_file = File(alias=alias, file_url=url, server=server)
    return db_file


class Files(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _upload_file(self, ctx, alias, url):
        server = ctx.guild.id
        db_file = create_file(alias, url, server)
        with session_scope() as session:
            session.add(db_file)
            session.close()

    @commands.command()
    async def upload(self, ctx, alias):
        try:
            print(f"Uploading new file with alias {alias}")
            url = ctx.message.attachments[0].url
            await self._upload_file(ctx, alias, url)
            await ctx.send(f"Created {alias}")
        except Exception as e:
            await ctx.send(f"Could not create {alias}")
            raise

    @commands.command()
    async def upload_embed(self, ctx, url, alias):
        try:
            print(f"Uploading new file with alias {alias}")
            await self._upload_file(ctx, alias, url)
            await ctx.send(f"Created {alias}")
        except Exception as e:
            await ctx.send(f"Could not create {alias}")
            raise

    @commands.command()
    async def load(self, ctx, alias):
        try:
            server = ctx.guild.id
            db_file = File.load(server=server,alias=alias)
            print(f"Sending file with alias {alias}")
            await ctx.send(db_file.file_url)
        except NoResultFound:
            pass
        except Exception:
            raise

    @commands.command()
    async def delete_file(self, ctx, alias):
        server = ctx.guild.id
        try:
            File.delete(server=server, alias=alias)
            await ctx.send(f"Deleted {alias}")
        except Exception:
            await ctx.send(f"Could not delete {alias}")

    @commands.command()
    async def delete_bind(self, ctx, alias):
        server = ctx.guild.id
        try:
            Bind.delete(server, alias=alias)
            await ctx.send(f"Deleted {alias}")
        except Exception:
            await ctx.send(f"Could not delete {alias}")

    async def exists(self, ctx, alias):
        server = ctx.guild.id
        exists = File.exists(server=server, alias=alias)
        return exists


class Binds():
    async def upload_bind(self, ctx, url, alias):
        server = ctx.guild.id
        db_file = Bind(alias=alias, file_url=url, server=server)
        db_file.upload()

    async def load_bind(self, ctx, alias):
        server = ctx.guild.id
        await Bind.load(server=server, alias=alias)

    async def exists(self, ctx, alias):
        server = ctx.guild.id
        exists = Bind.exists(server=server, alias=alias)
        return exists

    async def random(self, ctx):
        bind = Bind.random(server=ctx.guild.id)
        return bind
