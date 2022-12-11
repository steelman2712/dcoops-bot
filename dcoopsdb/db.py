from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os


user = os.environ.get("DB_USERNAME")
password = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
port = os.environ.get("DB_PORT")

sqlalchemy_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/discord"
engine = create_engine(sqlalchemy_url, echo=False, pool_recycle=3600, pool_pre_ping=True)
Session = scoped_session(sessionmaker(engine))
