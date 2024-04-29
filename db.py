from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from settings import DATABASE_URL  # , DEBUG

DEBUG = False
# engine = create_engine(DATABASE_URL, echo=DEBUG, pool_size=10, max_overflow=20)
engine = create_engine(DATABASE_URL, echo=DEBUG)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
