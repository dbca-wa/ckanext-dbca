# db_log_handler.py
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ckan.plugins.toolkit import config, asbool

from ckanext.dbca.model import dbca_logs


class SQLAlchemyHandler(logging.Handler):
    def __init__(self, db_url):
        logging.Handler.__init__(self)
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def emit(self, record):
        self.session.execute(
            dbca_logs.insert().values(
                timestamp=record.asctime,
                level=record.levelname,
                name=record.name,
                message=record.getMessage()
            )
        )
        self.session.commit()


def configure_logging():
    if asbool(config.get('ckanext.dbca.enable_db_logging', False)):
        # Add SQLAlchemyHandler to log to database
        db_handler = SQLAlchemyHandler(config.get('sqlalchemy.url'))
        keys = ['root', 'ckan', 'ckanext', 'werkzeug', 'saml2']
        for key in keys:
            logger = logging.getLogger(key)
            logger.addHandler(db_handler)
