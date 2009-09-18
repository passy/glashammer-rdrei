
import os


from ZODB import FileStorage, DB
from ZODB.config import databaseFromURL


from glashammer.utils import local, get_app


def get_zodb_db():
    return local.zodb_db

def get_zodb_conn():
    return local.zodb_conn

def get_zodb_root():
    return local.zodb_conn.root()


def setup_zodb(app, config_file=None):

    def _open_conn():
        db = get_app().zodb_db
        local.zodb_db = db
        local.zodb_conn = db.open()

    def _close_conn(*args):
        local.zodb_conn.close()

    def _setup_db(app, config_file=config_file):


        if config_file:
            if not os.path.is_abs(config_file):
                config_file = os.path.join(app.instance_dir, config_file)
            db = ZODB.config.databaseFromURL(config_file)
        else:
            # Sane default
            db_path = os.path.join(app.instance_dir, 'gh.zodb')
            db = DB(FileStorage.FileStorage(db_path))

        app.zodb_db = db
        # for use by the data init functions
        _open_conn()

    app.connect_event('app-start', _setup_db)
    app.connect_event('app-setup', _close_conn)
    app.connect_event('wsgi-call', _open_conn)
    app.connect_event('response-end', _close_conn)


setup_app = setup_zodb

