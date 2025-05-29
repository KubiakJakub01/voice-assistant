"""Create database tables and load initial data."""

from app.data_loader import load_data_from_json
from app.database import Base, engine
from app.settings import DATA_FILE_PATH
from app.utils import log_info


def create_and_populate_tables():
    log_info('Creating database tables...')
    Base.metadata.create_all(bind=engine)
    log_info('Database tables created.')

    log_info('\nLoading initial data from JSON...')
    load_data_from_json(str(DATA_FILE_PATH))
    log_info('Initial data loaded.')


def drop_db():
    log_info('Dropping database tables...')
    Base.metadata.drop_all(bind=engine)
    log_info('Database tables dropped.')


def main():
    drop_db()
    create_and_populate_tables()


if __name__ == '__main__':
    main()
