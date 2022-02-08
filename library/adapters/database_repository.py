from datetime import date
from typing import List

from sqlalchemy import desc, asc, func
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack

from library.domain.model import User, Book, Review, Author, Publisher
from library.adapters.repository import AbstractRepository


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, user_name: str) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter(func.lower(User._User__user_name) == func.lower(user_name)).one()
        except NoResultFound:
            # Ignore any exception and return None
            pass

        return user

    def update_favourites(self, user: User, book: Book):
        # Add the book to favourites if it isn't in favourites, remove if it is
        with self._session_cm as scm:
            if book in user.favourites:
                user.unfavourite_a_book(book)
                book.remove_user(user)
            else:
                user.favourite_a_book(book)
                book.add_user(user)
            scm.commit()

    def add_book(self, book: Book):
        with self._session_cm as scm:
            scm.session.add(book)
            scm.commit()

    def get_book(self, id: int) -> Book:
        book = None
        try:
            book = self._session_cm.session.query(Book).filter(Book._Book__book_id == id).one()
        except NoResultFound:
            # Ignore any exception and return None
            pass

        return book

    def get_books(self, id_list):
        books = self._session_cm.session.query(Book).filter(Book._Book__book_id.in_(id_list)).all()
        return books

    def get_number_of_books(self):
        number_of_books = self._session_cm.session.query(Book).count()
        return number_of_books

    def partial_search_books_by_title(self, title_string: str):
        if not isinstance(title_string, str) or len(title_string.strip()) == 0:
            return []
        else:
            # Return book ids containing title_string in their title; return an empty list if there are no matches.
            books = self._session_cm.session.query(Book).filter(Book._Book__title.contains(title_string.strip())).all()
            return [book.book_id for book in books]

    def get_all_book_ids(self):
        book_ids = self._session_cm.session.execute('SELECT id FROM books').all()

        if book_ids is None:
            return []
        else:
            book_ids = [id[0] for id in book_ids]

        return book_ids

    def get_book_ids_by_author(self, author: Author):
        if not isinstance(author, Author):
            return []
        else:
            row = self._session_cm.session.execute(
                'SELECT id FROM authors WHERE id= :id',
                {'id': author.unique_id}).fetchone()

            if row is None:
                return []
            else:
                author_id = row[0]
                # Retrieve book ids of all books associated with the author
                book_ids = self._session_cm.session.execute(
                    'SELECT book_id FROM book_authors WHERE author_id = :author_id',
                    {'author_id': author_id}).fetchall()

                return [id[0] for id in book_ids]

    def get_book_ids_by_multiple_authors(self, author_list: List[Author]):
        book_ids = []
        for author in author_list:
            for book_id in self.get_book_ids_by_author(author):
                book_ids.append(book_id)
        return book_ids

    def get_book_ids_by_publisher(self, publisher: Publisher):
        if not isinstance(publisher, Publisher):
            return []
        else:
            row = self._session_cm.session.execute(
                'SELECT name FROM publishers WHERE name= :name',
                {'name': publisher.name}).fetchone()

            if row is None:
                return []
            else:
                publisher_name = row[0]

                # Retrieve book ids of all books associated with the publisher
                book_ids = self._session_cm.session.execute(
                    'SELECT id FROM books WHERE publisher_name = :publisher',
                    {'publisher': publisher_name}).fetchall()

                return [id[0] for id in book_ids]

    def get_book_ids_by_multiple_publishers(self, publisher_list: List[Publisher]):
        book_ids = []
        for publisher in publisher_list:
            for book_id in self.get_book_ids_by_publisher(publisher):
                book_ids.append(book_id)
        return book_ids

    def get_book_ids_by_year(self, year: int):
        if isinstance(year, int):
            book_ids = self._session_cm.session.execute(f'SELECT id FROM books WHERE release_year={year}').all()
            if book_ids is None:
                return []
            else:
                return [id[0] for id in book_ids]
        return []

    def add_author(self, author: Author):
        with self._session_cm as scm:
            scm.session.add(author)
            scm.commit()

    def get_author(self, author_id: int) -> Author:
        author = None
        try:
            author = self._session_cm.session.query(Author).filter(Author._Author__unique_id == author_id).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return author

    def get_authors(self):
        authors = self._session_cm.session.query(Author).all()
        return authors

    def partial_search_authors(self, author_string: str):
        if not isinstance(author_string, str) or len(author_string.strip()) == 0:
            return []
        else:
            authors = self._session_cm.session.query(Author).filter(Author._Author__full_name.contains(author_string.strip())).all()
            return authors

    def add_publisher(self, publisher: Publisher):
        with self._session_cm as scm:
            scm.session.add(publisher)
            scm.commit()

    def get_publisher(self, publisher_name: str) -> Publisher:
        publisher = None
        try:
            publisher = self._session_cm.session.query(Publisher).filter(Publisher._Publisher__name == publisher_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return publisher

    def get_publishers(self):
        publishers = self._session_cm.session.query(Publisher).all()
        return publishers

    def partial_search_publishers(self, publisher_string: str):
        if not isinstance(publisher_string, str) or len(publisher_string.strip()) == 0:
            return []
        else:
            publishers = self._session_cm.session.query(Publisher).filter(
                Publisher._Publisher__name.contains(publisher_string.strip())).all()
            return publishers

    def add_review(self, review: Review):
        super().add_review(review)
        with self._session_cm as scm:
            scm.session.add(review)
            scm.commit()

    def get_reviews(self):
        reviews = self._session_cm.session.query(Review).all()
        return reviews
