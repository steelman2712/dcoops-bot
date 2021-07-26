from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UniqueConstraint

Base = declarative_base()


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    alias = Column(String(256), nullable=False)
    file_url = Column(String(256), nullable=False)
    server = Column(String(32), nullable=False)

    __table_args__ = (UniqueConstraint(alias, server),)

    def __repr__(self):
        return f"""<File(file_url = ${self.file_url}, server=${self.server})>"""


class Bind(Base):
    __tablename__ = "binds"

    id = Column(Integer, primary_key=True)
    alias = Column(String(256), nullable=False)
    file_url = Column(String(256), nullable=False)
    server = Column(String(32), nullable=False)

    __table_args__ = (UniqueConstraint(alias, server),)

    def __repr__(self):
        return f"""<Bind(file_url = ${self.file_url}, server=${self.server})>"""
