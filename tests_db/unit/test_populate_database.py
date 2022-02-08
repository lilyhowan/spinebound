from sqlalchemy import select, inspect

from library.adapters.orm import metadata


def test_database_populate_inspect_table_names(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['authors', 'book_authors', 'books',
                                           'publishers', 'reviews', 'user_favourites', 'users']


def test_database_populate_select_all_publishers(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_publishers_table = inspector.get_table_names()[3]

    with database_engine.connect() as connection:
        # query for records in table publishers
        select_statement = select([metadata.tables[name_of_publishers_table]])
        result = connection.execute(select_statement)

        all_publisher_names = []
        for row in result:
            all_publisher_names.append(row['name'])

        assert all_publisher_names == ['N/A', 'Garzanti', 'Hachette Partworks Ltd.', 'Createspace', 'Ingram',
                                       'lmjls lwTny llthqf@ wlfnwn wladb - lkwyt', 'Marvel', 'VIZ Media']


def test_database_populate_select_all_authors(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_authors_table = inspector.get_table_names()[0]

    with database_engine.connect() as connection:
        # query for records in table authors
        select_statement = select([metadata.tables[name_of_authors_table]])
        result = connection.execute(select_statement)

        all_authors = []
        for row in result:
            all_authors.append((row['id'], row['full_name']))

        nr_authors = len(all_authors)
        assert nr_authors == 20

        assert all_authors[0] == (18119, 'Joe Kelly')


def test_database_populate_select_all_users(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = inspector.get_table_names()[6]

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['user_name'])

        assert all_users == ['thorke', 'fmercury']


def test_database_populate_select_all_reviews(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_reviews_table = inspector.get_table_names()[4]

    with database_engine.connect() as connection:
        # query for records in table reviews
        select_statement = select([metadata.tables[name_of_reviews_table]])
        result = connection.execute(select_statement)

        all_reviews = []
        for row in result:
            all_reviews.append((row['id'], row['user_id'], row['book_id'], row['review_text'], row['rating']))

        assert all_reviews == [(1, 1, 12413392, 'This is a review 1', 3),
                               (2, 1, 12413392, 'This is a review 2', 2),
                               (3, 2, 35452242, 'Great book', 5)]


def test_database_populate_select_all_books(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_books_table = inspector.get_table_names()[2]

    with database_engine.connect() as connection:
        # query for records in table books
        select_statement = select([metadata.tables[name_of_books_table]])
        result = connection.execute(select_statement)

        all_books = []
        for row in result:
            all_books.append((row['id'], row['title']))

        nr_books = len(all_books)
        assert nr_books == 14

        assert all_books[0] == (780918, 'Rite of Conquest (William the Conqueror, #1)')
