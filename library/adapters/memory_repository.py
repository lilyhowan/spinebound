import csv
import json
from bisect import insort_left
from datetime import datetime
from pathlib import Path
from typing import List

from werkzeug.security import generate_password_hash

from library.adapters.json_data_reader import BooksJSONReader
from library.adapters.repository import AbstractRepository, RepositoryException
from library.domain.model import Publisher, Author, Book, User, Review, make_review


class MemoryRepository(AbstractRepository):

    def __init__(self):
        self.__books = list()
        self.__books_index = dict()
        self.__users = list()
        self.__authors = list()
        self.__publishers = set()
        self.__reviews = list()

    # User methods
    def add_user(self, user: User):
        self.__users.append(user)

    def get_user(self, user_name) -> User:
        if isinstance(user_name, str):
            return next((user for user in self.__users if user.user_name == user_name.lower()), None)
        return None

    def update_favourites(self, user: User, book: Book):
        # Add the book to favourites if it isn't in favourites, remove if it is
        # Domain model will not add book if it is already in user's favourites
        if book in user.favourites:
            user.unfavourite_a_book(book)
            book.remove_user(user)
        else:
            user.favourite_a_book(book)
            book.add_user(user)

    # Book methods
    def add_book(self, book: Book):
        insort_left(self.__books, book)
        self.__books_index[book.book_id] = book

    def get_book(self, book_id: int) -> Book:
        book = None
        try:
            book = self.__books_index[book_id]
        except KeyError:
            pass  # Ignore exception and return None

        return book

    def get_books(self, id_list):
        # Strip out any ids in id_list that don't represent Book ids in the repository
        existing_ids = [book_id for book_id in id_list if book_id in self.__books_index]

        # Fetch the Books
        books = [self.__books_index[book_id] for book_id in existing_ids]
        return books

    def get_number_of_books(self):
        return len(self.__books)

    def partial_search_books_by_title(self, title_string: str):
        matching_book_ids = []
        # If empty string or whitespace, return empty list
        if not isinstance(title_string, str) or len(title_string.strip()) == 0:
            return matching_book_ids

        title_string = title_string.strip()

        for book in self.__books:
            if title_string.lower() in book.title.lower():
                matching_book_ids.append(book.book_id)
        return matching_book_ids

    def get_all_book_ids(self):
        return [book.book_id for book in self.__books]

    def get_book_ids_by_year(self, year: int):
        if isinstance(year, int):
            return [book.book_id for book in self.__books if year == book.release_year]
        return []

    # Author methods
    def add_author(self, author: Author):
        self.__authors.append(author)

    def get_author(self, author_id: int):
        for author in self.__authors:
            if author.unique_id == author_id:
                return author
        return None

    def get_authors(self):
        return self.__authors

    def get_book_ids_by_author(self, author: Author):
        return [book.book_id for book in self.__books if author in book.authors]

    def get_book_ids_by_multiple_authors(self, author_list: List[Author]):
        book_ids = []
        for author in author_list:
            for book_id in self.get_book_ids_by_author(author):
                book_ids.append(book_id)
        return book_ids

    def partial_search_authors(self, author_string: str):
        matching_authors = []

        if not isinstance(author_string, str) or len(author_string.strip()) == 0:
            return matching_authors

        author_string = author_string.strip()

        for author in self.__authors:
            if author_string.lower() in author.full_name.lower():
                matching_authors.append(author)
        return matching_authors

    # Publisher methods
    def add_publisher(self, publisher: Publisher):
        self.__publishers.add(publisher)

    def get_publisher(self, publisher_name: str):
        for publisher in self.__publishers:
            if publisher.name == publisher_name:
                return publisher
        return None

    def get_publishers(self):
        # Do not return publisher with name "N/A"
        return [publisher for publisher in self.__publishers if publisher.name != "N/A"]

    def get_book_ids_by_publisher(self, publisher: Publisher):
        return [book.book_id for book in self.__books if publisher == book.publisher]

    def get_book_ids_by_multiple_publishers(self, publisher_list: List[Publisher]):
        book_ids = []
        for publisher in publisher_list:
            for book_id in self.get_book_ids_by_publisher(publisher):
                book_ids.append(book_id)
        return book_ids

    def partial_search_publishers(self, publisher_string: str):
        matching_publishers = []

        if not isinstance(publisher_string, str) or len(publisher_string.strip()) == 0:
            return matching_publishers

        publisher_string = publisher_string.strip()

        for publisher in self.__publishers:
            if publisher_string.lower() in publisher.name.lower():
                matching_publishers.append(publisher)
        return matching_publishers

    # Review methods
    def add_review(self, review: Review):
        # Call parent class first, add_review relies on implementation of code common to all derived classes
        super().add_review(review)
        self.__reviews.insert(0, review)

    def get_reviews(self):
        return self.__reviews