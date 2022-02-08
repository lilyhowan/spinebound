import pytest

import datetime

from sqlalchemy.exc import IntegrityError

from library.domain.model import User, Book, Review, Author, Publisher, make_review, \
    make_author_association, make_publisher_association

book_timestamp = datetime.date(2020, 2, 28)


def insert_user(empty_session, values=None):
    new_name = "Andrew"
    new_password = "1234567"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (user_name, password) VALUES (:user_name, :password)',
                          {'user_name': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where user_name = :user_name',
                                {'user_name': new_name}).fetchone()
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (user_name, password) VALUES (:user_name, :password)',
                              {'user_name': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT id from users'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_book(empty_session):
    empty_session.execute(
        'INSERT INTO books (id, title, description, release_year, ebook, num_pages, image_url) VALUES '
        '(1, '
        '"Fruits Basket", '
        '"Test description", '
        '1998, '
        'False, '
        '136, '
        '"https://cdn.myanimelist.net/images/manga/2/155964.jpg")'
    )
    row = empty_session.execute('SELECT id from books').fetchone()
    return row[0]


def insert_authors(empty_session):
    empty_session.execute(
        'INSERT INTO authors (full_name) VALUES ("Natsuki Takaya")'
    )
    rows = list(empty_session.execute('SELECT id from authors'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_book_author_associations(empty_session, book_key, author_keys):
    stmt = 'INSERT INTO book_authors (book_id, author_id) VALUES (:book_id, :author_id)'
    for author_key in author_keys:
        empty_session.execute(stmt, {'book_id': book_key, 'author_id': author_key})


def insert_reviewed_book(empty_session):
    book_key = insert_book(empty_session)
    user_key = insert_user(empty_session)

    timestamp_1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    empty_session.execute(
        'INSERT INTO reviews (user_id, book_id, review_text, rating, timestamp) VALUES '
        '(:user_id, :book_id, "Comment 1", 5, :timestamp_1),'
        '(:user_id, :book_id, "Comment 2", 4, :timestamp_2)',
        {'user_id': user_key, 'book_id': book_key, 'timestamp_1': timestamp_1, 'timestamp_2': timestamp_2}
    )

    row = empty_session.execute('SELECT id from books').fetchone()
    return row[0]


def make_book():
    book = Book(1, "Fruits Basket")
    book.description = "Test description"
    book.release_year = 1998
    book.ebook = False
    book.num_pages = 136
    book.image_url = "https://cdn.myanimelist.net/images/manga/2/155964.jpg"
    return book


def make_user():
    user = User("Andrew", "111222333")
    return user


def make_author():
    author = Author(12, "Natsuki Takaya")
    return author


def make_publisher():
    publisher = Publisher("Madman Entertainment")
    return publisher


def test_loading_of_users(empty_session):
    users = list()
    users.append(("andrew", "1234567"))
    users.append(("cindy", "1111222333"))
    insert_users(empty_session, users)

    expected = [
        User("andrew", "12344567"),
        User("cindy", "9990009")
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_name, password FROM users'))
    assert rows == [("andrew", "111222333")]


def test_saving_of_users_with_common_user_name(empty_session):
    insert_user(empty_session, ("Andrew", "1234567"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_book(empty_session):
    book_key = insert_book(empty_session)
    expected_book = make_book()
    fetched_book = empty_session.query(Book).one()

    assert expected_book == fetched_book
    assert book_key == fetched_book.book_id


def test_loading_of_book_author(empty_session):
    book_key = insert_book(empty_session)
    author_keys = insert_authors(empty_session)
    insert_book_author_associations(empty_session, book_key, author_keys)

    book = empty_session.query(Book).get(book_key)
    authors = [empty_session.query(Author).get(key) for key in author_keys]

    for author in authors:
        assert book in author.books
        assert author in book.authors


def test_loading_of_reviewed_book(empty_session):
    insert_reviewed_book(empty_session)

    rows = empty_session.query(Book).all()
    book = rows[0]

    for review in book.reviews:
        assert review.book is book


def test_saving_of_review(empty_session):
    book_key = insert_book(empty_session)
    user_key = insert_user(empty_session, ("Andrew", "1234567"))

    rows = empty_session.query(Book).all()
    book = rows[0]
    user = empty_session.query(User).filter(User._User__user_name == "Andrew").one()

    # Create a new Review that is bidirectionally linked with the User and Book
    review_text = "Some review text."
    rating = 3
    review = make_review(user, book, review_text, rating)

    # Note: if the bidirectional links between the new Review and the User and
    # Book objects hadn't been established in memory, they would exist following
    # committing the addition of the Review to the database
    empty_session.add(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, book_id, review_text, rating FROM reviews'))

    assert rows == [(user_key, book_key, review_text, rating)]


def test_saving_of_book(empty_session):
    book = make_book()
    empty_session.add(book)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT id, title FROM books'))
    assert rows == [(1, "Fruits Basket")]


def test_saving_book_with_authors(empty_session):
    book = make_book()
    author = make_author()

    # Establish the bidirectional relationship between the Book and the Author
    make_author_association(book, author)

    # Persist the Book (and Author)
    # Note: it doesn't matter whether we add the Author or the Book. They are connected
    # bidirectionally, so persisting either one will persist the other
    empty_session.add(book)
    empty_session.commit()

    # Test test_saving_of_book() checks for insertion into the books table
    rows = list(empty_session.execute('SELECT id FROM books'))
    book_key = rows[0][0]

    # Check that the authors table has a new record
    rows = list(empty_session.execute('SELECT id, full_name FROM authors'))
    author_key = rows[0][0]
    assert rows[0][1] == "Natsuki Takaya"

    # Check that the book_authors table has a new record
    rows = list(empty_session.execute('SELECT book_id, author_id from book_authors'))
    book_foreign_key = rows[0][0]
    author_foreign_key = rows[0][1]

    assert book_key == book_foreign_key
    assert author_key == author_foreign_key


def test_saving_book_with_publisher(empty_session):
    book = make_book()
    publisher = make_publisher()

    # Establish the bidirectional relationship between the Book and the Publisher
    make_publisher_association(book, publisher)

    # Persist the Book (and Publisher).
    # Note: it doesn't matter whether we add the Publisher or the Book. They are connected
    # bidirectionally, so persisting either one will persist the other
    empty_session.add(book)
    empty_session.commit()

    # Test test_saving_of_book() checks for insertion into the books table
    rows = list(empty_session.execute('SELECT publisher_name FROM books'))
    assert rows[0][0] == "Madman Entertainment"

    # Check that the publishers table has a new record
    rows = list(empty_session.execute('SELECT name FROM publishers'))
    assert rows[0][0] == "Madman Entertainment"


def test_save_reviewed_book(empty_session):
    # Create Book, User objects
    book = make_book()
    user = make_user()

    # Create a new Review that is bidirectionally linked with the User and Book
    review_text = "Some review text."
    review = make_review(book, user, review_text, 5)

    # Save the new Book
    empty_session.add(book)
    empty_session.commit()

    # Test test_saving_of_book() checks for insertion into the books table
    rows = list(empty_session.execute('SELECT id FROM books'))
    book_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table
    rows = list(empty_session.execute('SELECT id FROM users'))
    user_key = rows[0][0]

    # Check that the reviews table has a new record that links to the books and users
    # tables
    rows = list(empty_session.execute('SELECT user_id, book_id, review_text, rating FROM reviews'))
    assert rows == [(user_key, book_key, review_text, 5)]
