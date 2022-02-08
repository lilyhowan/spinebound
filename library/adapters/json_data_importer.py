import csv
from pathlib import Path

from werkzeug.security import generate_password_hash

from library.adapters.json_data_reader import BooksJSONReader
from library.adapters.repository import AbstractRepository
from library.domain.model import User, Book, Author, Publisher, make_review, make_author_association, \
    make_publisher_association


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)
        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_books_authors_and_publishers(data_path: Path, repo: AbstractRepository, database_mode: bool):
    author_file = str(data_path / "book_authors_excerpt.json")
    book_file = str(data_path / "comic_books_excerpt.json")

    reader = BooksJSONReader(book_file, author_file)
    reader.read_json_files()

    for book in reader.dataset_of_books:
        repo.add_book(book)

    for publisher_name in reader.publisher_book_associations:
        publisher = Publisher(publisher_name)
        for book_id in reader.publisher_book_associations[publisher_name]:
            book = repo.get_book(int(book_id))
            if database_mode is True:
                # the ORM takes care of the association between books and publishers
                book.publisher = publisher
            else:
                make_publisher_association(book, publisher)
        repo.add_publisher(publisher)

    for author_id in reader.author_book_associations:
        author = Author(int(author_id), reader.author_book_associations[author_id][0])
        for i in range(1, len(reader.author_book_associations[author_id])):
            book = repo.get_book(int(reader.author_book_associations[author_id][i]))
            if database_mode is True:
                # the ORM takes care of the association between books and authors
                book.add_author(author)
            else:
                make_author_association(book, author)
        repo.add_author(author)


def load_users(data_path: Path, repo: AbstractRepository):
    users = dict()

    users_filename = str(Path(data_path) / "users.csv")
    for data_row in read_csv_file(users_filename):
        user = User(
            user_name=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_reviews(data_path: Path, repo: AbstractRepository, users):
    reviews_filename = str(Path(data_path) / "reviews.csv")
    for data_row in read_csv_file(reviews_filename):
        review = make_review(user=users[data_row[1]],
                             book=repo.get_book(int(data_row[2])),
                             review_text=data_row[3],
                             rating=int(data_row[4]))
        repo.add_review(review)
