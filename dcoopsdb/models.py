from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, UniqueConstraint

from dcoopsdb.db import session_scope

Base = declarative_base()

class BaseFile(object):

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return f"{cls.__name__.lower()}s"

    id = Column(Integer, primary_key=True)
    alias = Column(String(256), nullable=False)
    file_url = Column(String(256), nullable=False)
    server = Column(String(32), nullable=False)

    __table_args__ = (UniqueConstraint(alias, server),)

    @classmethod
    def upload(cls, db_file):
        with session_scope() as session:
            session.add(db_file)

    @classmethod
    def load(cls, server, alias):
        alias = alias.lower()
        with session_scope() as session:
            query = (
                session.query(cls)
                .filter_by(alias=alias)
                .filter_by(server=server)
            )
            db_file = query.one()
            session.close()

        return db_file

    @classmethod
    def delete(cls, server, alias):
        alias = alias.lower()
        with session_scope() as session:
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
        with session_scope() as session:
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
        with session_scope() as session:
            query = session.query(cls).filter_by(server=server)
            rowCount = int(query.count())
            randomRow = query.offset(int(rowCount * random.random())).first()
            session.close()
        return randomRow

class File(Base, BaseFile):
    __tablename__ = "files"

    def __repr__(self):
        return f"""<File(alias=${self.alias}, file_url = ${self.file_url}, server=${self.server})>"""


class Bind(Base, BaseFile):
    __tablename__ = "binds"

    def __repr__(self):
        return f"""<Bind(alias=${self.alias}, file_url = ${self.file_url}, server=${self.server})>"""


class Settings(Base):
    __tablename__ = "settings"
    server = Column(String(32), nullable=False, unique=True, primary_key=True)
