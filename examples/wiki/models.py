
from sqlalchemy import *
from sqlalchemy.orm import *

from glashammer.bundles.sqlalchdb import ModelBase


class Page(ModelBase):

    __tablename__ = 'pages'
    name = Column(String, primary_key=True)


class Revision(ModelBase):

    __tablename__ = 'revision'
    id = Column(Integer, primary_key=True)
    page_name = Column(String, ForeignKey('pages.name'))
    page = relation(Page, backref='revisions')
    text = Column(UnicodeText)


