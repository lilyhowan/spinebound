"""Initialize Flask app"""

from pathlib import Path
from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.pool import NullPool

import library.adapters.repository as repo
from library.adapters import memory_repository, database_repository, repository_populate
from library.adapters.orm import metadata, map_model_to_tables


def create_app(test_config=None):
    # Create the Flask app object
    app = Flask(__name__)

    # Configure app from config file settings
    app.config.from_object('config.Config')
    data_path = Path('library') / 'adapters' / 'data'

    if test_config is not None:
        # Load test configuration, and override any configuration settings
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']

    if app.config['REPOSITORY'] == 'memory':
        # Create the MemoryRepository implementation for a memory-based repository
        repo.repo_instance = memory_repository.MemoryRepository()
        database_mode = False
        repository_populate.populate(data_path, repo.repo_instance, database_mode)

    elif app.config['REPOSITORY'] == 'database':
        # Configure database
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        database_echo = app.config['SQLALCHEMY_ECHO']
        database_engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=NullPool,
                                        echo=database_echo)
        session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)
        repo.repo_instance = database_repository.SqlAlchemyRepository(session_factory)

        if app.config['TESTING'] == 'True' or len(database_engine.table_names()) == 0:
            print("REPOPULATING DATABASE...")
            # For testing, or first-time use of the web application, reinitialise the database
            clear_mappers()
            metadata.create_all(database_engine)  # Conditionally create database tables
            for table in reversed(metadata.sorted_tables):  # Remove any data from the tables
                database_engine.execute(table.delete())

            # Generate mappings that map domain model classes to the database tables
            map_model_to_tables()

            database_mode = True
            repository_populate.populate(data_path, repo.repo_instance, database_mode)
            print("REPOPULATING DATABASE... FINISHED")

        else:
            # Solely generate mappings that map domain model classes to the database tables
            map_model_to_tables()

    with app.app_context():
        # Register blueprints
        from .home import home
        app.register_blueprint(home.home_blueprint)

        from .authentication import authentication
        app.register_blueprint(authentication.authentication_blueprint)

        from .browse import browse
        app.register_blueprint(browse.browse_blueprint)

        from .book import book
        app.register_blueprint(book.book_blueprint)

        # Register a callback the makes sure that database sessions are associated with http requests
        # We reset the session inside the database repository before a new flask request is generated
        @app.before_request
        def before_flask_http_request_function():
            if isinstance(repo.repo_instance, database_repository.SqlAlchemyRepository):
                repo.repo_instance.reset_session()

        # Register a tear-down method that will be called after each request has been processed
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            if isinstance(repo.repo_instance, database_repository.SqlAlchemyRepository):
                repo.repo_instance.close_session()

    return app
