import sqlalchemy
from sqlalchemy.orm import sessionmaker

import os

from contextlib import contextmanager


user = os.environ.get("DB_USERNAME")
password = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")

sqlalchemy_url = f'mysql+pymysql://{user}:{password}@{host}/discord'

sqlalchemy.engine = sqlalchemy.create_engine(sqlalchemy_url, echo=False)
Session = sessionmaker(sqlalchemy.engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    