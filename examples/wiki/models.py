
from sqlalchemy import *
from sqlalchemy.orm import *

from glashammer.bundles.sqlalchdb import ModelBase, session


class Page(ModelBase):

    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Revision(ModelBase):

    __tablename__ = 'revision'
    id = Column(Integer, primary_key=True)
    page_name = Column(String, ForeignKey('pages.name'))
    page = relation(Page, backref='revisions')
    text = Column(UnicodeText)

    def __str__(self):
        return 'r%s' % self.id


