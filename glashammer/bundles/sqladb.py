
import os



def _get_default_db_uri(app):
    db_file = os.path.join(app.instance_dir, 'gh.sqlite')
    return 'sqlite:///' + db_file


def data_init(app):
    from glashammer.database import metadata
    metadata.create_all()


def setup_sqladb(app):
    from glashammer.database import db, metadata
    app.add_config_var('sqla_db_uri', str, _get_default_db_uri(app))
    app.sqla_db_engine = db.create_engine(app.cfg['sqla_db_uri'],
                                          convert_unicode=True)
    metadata.bind = app.sqla_db_engine
    app.add_data_func(data_init)
