import os
from contextlib import contextmanager

from sqlalchemy import (
    create_engine,
    MetaData,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base(metadata=MetaData(schema="gesina"))

user = os.getenv("DATABASE_USER", "user")
password = os.getenv("DATABASE_PASSWORD", "password")
database_name = os.getenv("DATABASE_NAME", "main")

engine = create_engine(f"postgresql://{user}:{password}@localhost:5432/{database_name}")


@contextmanager
def get_session():
    session = Session(expire_on_commit=False)
    try:
        yield session
        session.commit()
        session.expunge_all()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def persist(persistable_object):
    with get_session() as session:
        session.add(persistable_object)
