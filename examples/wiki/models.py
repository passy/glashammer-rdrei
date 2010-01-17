
from sqlalchemy import *
from sqlalchemy.orm import *

from glashammer.bundles.sqlalchdb import metadata, session

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(metadata=metadata)


class Page(Base):

    __tablename__ = 'pages'

    name = Column(String, primary_key=True)


class Revision(Base):

    __tablename__ = 'revision'
    id = Column(Integer, primary_key=True)
    page_name = Column(String, ForeignKey('pages.name'))
    text = Column(UnicodeText)

    page = relation(Page, backref='revisions')


