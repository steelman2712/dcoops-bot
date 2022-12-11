from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UniqueConstraint, Text

from dcoopsdb.db import Session
import random


class BaseFile(object):

    __abstract__ = True

    @classmethod
    def load(cls, server, alias):
        alias = alias.lower()
        with Session() as session:
            query = session.query(cls).filter_by(alias=alias).filter_by(server=server)
            db_file = query.first()
            session.close()

        return db_file

    @classmethod
    def load_all(cls, server):
        with Session() as session:
            query = session.query(cls).filter_by(server=server)
            entries = query.all()
            session.close()

        return entries

    @classmethod
    def delete(cls, server, alias):
        alias = alias.lower()
        with Session() as session:
            query = (  # noqa: F841
                session.query(cls)
                .filter_by(alias=alias)
                .filter_by(server=server)
                .delete()
            )
            session.commit()
            session.close()

    @classmethod
    def exists(cls, server, alias):
        alias = alias.lower()
        with Session() as session:
            exists = (
                session.query(cls)
                .filter_by(alias=alias)
                .filter_by(server=server)
                .scalar()
            )
            session.close()
            if exists is not None:
                return True
            else:
                return False

    @classmethod
    def random(cls, server):
        with Session() as session:
            query = session.query(cls).filter_by(server=server)
            rowCount = int(query.count())
            randomRow = query.offset(int(rowCount * random.random())).first()
            session.close()
        return randomRow


FileBase = declarative_base(cls=BaseFile)


class File(FileBase):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    alias = Column(String(256), nullable=False)
    file_url = Column(String(256), nullable=False)
    server = Column(String(32), nullable=False)

    __table_args__ = (UniqueConstraint(alias, server),)

    def __repr__(self):
        return f"""<File(alias=${self.alias}, file_url = ${self.file_url}, server=${self.server})>"""


class Bind(FileBase):
    __tablename__ = "binds"

    id = Column(Integer, primary_key=True)
    alias = Column(String(256), nullable=False)
    file_url = Column(String(256), nullable=False)
    server = Column(String(32), nullable=False)

    __table_args__ = (UniqueConstraint(alias, server),)

    def __repr__(self):
        return f"""<Bind(alias=${self.alias}, file_url = ${self.file_url}, server=${self.server})>"""


Base = declarative_base()


class CustomMessage(Base):
    __tablename__ = "custom_messages"
    JOIN_MESSAGE_TYPE = "join_message"
    LEAVE_MESSAGE_TYPE = "leave_message"

    id = Column(Integer, primary_key=True)
    server = Column(String(32), nullable=False)
    user_id = Column(String(32))
    message_type = Column(Text, nullable=False)
    message = Column(Text)

    def load_message(self, server, user_id, message_type):
        with Session() as session:
            query = (
                session.query(CustomMessage)
                .filter_by(user_id=user_id)
                .filter_by(server=server)
                .filter_by(message_type=message_type)
            )
            message = query.first()
            session.close()
        return message


class Settings(Base):
    __tablename__ = "settings"
    server = Column(String(32), nullable=False, unique=True, primary_key=True)
