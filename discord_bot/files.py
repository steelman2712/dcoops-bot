from discord.ext import commands

dictionary = {}
from models.models import File, Bind
from models.db import session_scope

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


class BaseFile:
    async def upload(self, db_file):
        with session_scope() as session:
            session.add(db_file)

    async def load(self, ctx, alias, class_type):
        alias = alias.lower()
        server = ctx.guild.id
        with session_scope() as session:
            query = (
                session.query(class_type)
                .filter_by(alias=alias)
                .filter_by(server=server)
            )
            db_file = query.one()
            session.close()

        return db_file

    async def delete(self, ctx, alias, class_type):
        alias = alias.lower()
        server = ctx.guild.id
        with session_scope() as session:
            query = (  # noqa: F841
                session.query(class_type)
                .filter_by(alias=alias)
                .filter_by(server=server)
                .delete()
            )
            session.commit()
            session.close()

    async def exists(self, ctx, alias, class_type):
        alias = alias.lower()
        server = ctx.guild.id
        with session_scope() as session:
            exists = (
                session.query(class_type)
                .filter_by(alias=alias)
                .filter_by(server=server)
                .scalar()
            )
            session.close()
            if exists is not None:
                return True
            else:
                return False

    async def random(self,server,class_type):
        with session_scope() as session:
            query = session.query(class_type).filter_by(server=server)
            rowCount = int(query.count())
            randomRow = query.offset(int(rowCount*random.random())).first()
            session.close()
        return randomRow


class Files(BaseFile, commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _upload_file(self, ctx, alias, url):
        server = ctx.guild.id
        db_file = create_file(alias, url, server)
        await super().upload(db_file)

    @commands.command()
    async def upload(self, ctx, alias):
        try:
            print(f"Uploading new file with alias {alias}")
            url = ctx.message.attachments[0].url
            await self._upload_file(ctx, alias, url)
            await ctx.send(f"Created {alias}")
        except Exception:
            await ctx.send(f"Could not create {alias}")

    @commands.command()
    async def upload_embed(self, ctx, url, alias):
        try:
            print(f"Uploading new file with alias {alias}")
            await self._upload_file(ctx, alias, url)
            await ctx.send(f"Created {alias}")
        except Exception:
            await ctx.send(f"Could not create {alias}")

    @commands.command()
    async def load(self, ctx, alias):
        try:
            db_file = await super().load(ctx, alias=alias, class_type=File)
            print(f"Sending file with alias {alias}")
            await ctx.send(db_file.file_url)
        except NoResultFound:
            pass
        except Exception:
            raise

    @commands.command()
    async def delete_file(self, ctx, alias):
        try:
            await super().delete(ctx, alias=alias, class_type=File)
            await ctx.send(f"Deleted {alias}")
        except Exception:
            await ctx.send(f"Could not delete {alias}")

    @commands.command()
    async def delete_bind(self, ctx, alias):
        try:
            await super().delete(ctx, alias=alias, class_type=Bind)
            await ctx.send(f"Deleted {alias}")
        except Exception:
            await ctx.send(f"Could not delete {alias}")

    async def exists(self, ctx, alias):
        exists = await super().exists(ctx, alias=alias, class_type=File)
        return exists
    

class Binds(BaseFile):
    async def upload_bind(self, ctx, url, alias):
        server = ctx.guild.id
        db_file = Bind(alias=alias, file_url=url, server=server)
        await super().upload(db_file=db_file)

    async def load_bind(self, ctx, alias):
        await super().load(ctx, alias, Bind)

    async def exists(self, ctx, alias):
        exists = await super().exists(ctx, alias=alias, class_type=Bind)
        return exists
    
    async def random(self,ctx):
        bind = await super().random(server=ctx.guild.id,class_type=Bind)
        return bind
