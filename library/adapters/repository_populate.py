from pathlib import Path

from library.adapters.repository import AbstractRepository
from library.adapters.json_data_importer import load_reviews, load_users, load_books_authors_and_publishers


def populate(data_path: Path, repo: AbstractRepository, database_mode: bool):
    # Load books, authors and publishers into the repository
    load_books_authors_and_publishers(data_path, repo, database_mode)

    # Load users into the repository
    users = load_users(data_path, repo)

    # Load reviews into the repository
    load_reviews(data_path, repo, users)
