
import os
from repoze.catalog.catalog import ConnectionManager
from repoze.catalog.catalog import Catalog
from repoze.catalog.catalog import FileStorageCatalogFactory
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex


from glashammer.utils import emit_event
from glashammer.utils.local import local

DBPATH_CONF = 'repozecatalog/dbpath'
DBNAME_CONF = 'repozecatalog/dbname'

INDEX_TYPES = {
    'field': CatalogFieldIndex,
    'text': CatalogTextIndex,
    'keywords': CatalogKeywordIndex
}

def get_repozecatalog():
    """Get this thread's catalog"""
    return local.application.repozecatalog


def default_attr_getter_factory(attr_name):
    """A factory to create a dumb index attr getter"""
    def f(item, default, attr_name=attr_name):
        return getattr(item, attr_name, default)
    return f


def create_dumb_index(index_type, attr_name, catalog=None, override=False):
    """Create a dumb index, ie one that just reads an attribute for the same
    named index
    """
    if catalog is None:
        catalog = get_repozecatalog()
    if override or attr_name not in catalog:
        index_factory = INDEX_TYPES.get(index_type)
        if index_factory is None:
            index_factory = index_type
        catalog[attr_name] = index_factory(default_attr_getter_factory(attr_name))


def index_document(docid, document, catalog=None):
    """Index a document to the current application catalog"""
    manager = ConnectionManager()
    if catalog is None:
        catalog = get_repozecatalog()
    catalog.index_doc(docid, document)
    manager.commit()


def search_catalog(**terms):
    """Search the catalog for the terms"""
    catalog = get_repozecatalog()
    return catalog.search(**terms)



def setup_repozecatalog(app, default_dbpath='repozecatalog.db',
                             default_dbname='catalog'):
    """Set up full text searching with repoze.catalog"""
    # if its not an absolute path, make it relative to the instance dir
    if not os.path.isabs(default_dbpath):
        default_dbpath = os.path.join(app.instance_dir, default_dbpath)
    app.add_config_var(DBPATH_CONF, str, default_dbpath)
    app.add_config_var(DBNAME_CONF, str, default_dbname)

    manager = ConnectionManager()
    catalog_factory = FileStorageCatalogFactory(
        app.cfg[DBPATH_CONF], app.cfg[DBNAME_CONF])
    catalog = catalog_factory()
    app.repozecatalog = catalog
    manager.commit()

    emit_event('repozecatalog-installed', catalog)




