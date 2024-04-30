from sqlalchemy import Column, Computed  # type: ignore
from sqlalchemy import Integer, String, DateTime  # type: ignore
from sqlalchemy.sql import func  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from db import Base, Session, engine  # type: ignore


class Token(Base):
    """Annotation tokens of interest"""

    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())

    token = Column(String, nullable=False)
    stemmer = Column(String, nullable=False)
    token_class = Column(String, nullable=False)


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())

    name = Column(String, nullable=False)
    fname = Column(String, nullable=False)
    corpus = Column(String, nullable=False)
    fulltext = Column(String, nullable=False)


class Sentence(Base):
    """Sentence of tokenized words"""

    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())

    sentence = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    text_id = Column(Integer, nullable=False)
    # stemmer = Column(String, nullable=False)


class Word(Base):
    """Tokenized words in a sentence"""

    __tablename__ = "words"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())

    word = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    sentence_id = Column(Integer, nullable=False)
    stemmer = Column(String, nullable=False)


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())

    text_id = Column(Integer, nullable=False)
    stemmer = Column(String, nullable=False)
    html = Column(String, nullable=False)
    # text_id = relationship("Text", back_populates="appuser_rel")
