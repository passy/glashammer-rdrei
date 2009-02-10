
import os
from repoze.catalog.catalog import Catalog
from repoze.catalog.catalog import FileStorageCatalogFactory

from glashammer.utils import emit_event
from glashammer.utils.local import local

DBPATH_CONF = 'repozecatalog/dbpath'
DBNAME_CONF = 'repozecatalog/dbname'


def get_repozecatalog():
    """Get this thread's catalog"""
    return local.repozecatalog


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
        catalog[attr_name] = index_type(default_attr_getter_factory(attr_name))


def index_document(docid, document, catalog=None):
    """Index a document to the current application catalog"""
    if catalog is None:
        catalog = get_repozecatalog()
    catalog.index_doc(docid, document)


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

    catalog_factory = FileStorageCatalogFactory(
        app.cfg[DBPATH_CONF], app.cfg[DBNAME_CONF])
    catalog = catalog_factory()
    local.repozecatalog = catalog

    emit_event('repozecatalog-installed', catalog)




