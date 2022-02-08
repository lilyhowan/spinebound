import abc
from typing import List

from library.domain.model import Publisher, Author, Book, User, Review

repo_instance = None


class RepositoryException(Exception):

    def __init__(self, message=None):
        pass


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add_user(self, user: User):
        """" Adds a User to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, user_name) -> User:
        """ Returns the User named user_name from the repository.

        If there is no User with the given user_name, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_favourites(self, user: User, book: Book):
        """ Update user's favourites and book's users_who_favourited """
        raise NotImplementedError

    @abc.abstractmethod
    def add_book(self, book: Book):
        """ Adds a Book to the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book(self, book_id: int) -> Book:
        """ Returns Book with matching id from the repository

        If there is no Book with the given id, this method returns None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_books(self, id_list):
        """ Returns a list of Books, whose ids match those in id_list, from the repository.

        If there are no matches, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_books(self):
        """ Returns number of Book objects in the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def partial_search_books_by_title(self, title_string: str):
        """ Returns all Book objects in the repository which have titles that contain the input string """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_book_ids(self):
        """ Returns id of all Book objects in the repository - used when no filters are required """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_by_author(self, author: Author):
        """ Returns id of Book objects in the repository which were written by the given Author """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_by_multiple_authors(self, author_list: List[Author]):
        """ Returns id of Book objects in the repository which were written by the given Authors """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_by_publisher(self, publisher: Publisher):
        """ Returns id of Book objects in the repository which were published by the given Publisher """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_by_multiple_publishers(self, publisher_list: List[Publisher]):
        """ Returns id of Book objects in the repository which were published by the given Publishers """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_by_year(self, year: int):
        """ Returns id of Book objects in the repository which were published in the given year """
        raise NotImplementedError

    @abc.abstractmethod
    def add_author(self, author: Author):
        """" Adds an Author to the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_author(self, author_id: int) -> Author:
        """ Returns Author with matching id from the repository

        If there is no Author with the given id, this method returns None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_authors(self):
        """ Returns all Author objects in the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def partial_search_authors(self, author_string: str):
        """ Returns all Author objects in the repository which have names that contain the input string """
        raise NotImplementedError

    @abc.abstractmethod
    def add_publisher(self, publisher: Publisher):
        """" Adds a Publisher to the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_publisher(self, publisher_name: str) -> Publisher:
        """ Returns Publisher with matching name from the repository

        If there is no Publisher with the given name, this method returns None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_publishers(self):
        """ Returns all Publisher objects in the repository, except those with name "N/A" """
        raise NotImplementedError

    @abc.abstractmethod
    def partial_search_publishers(self, publisher_string: str):
        """ Returns all Publisher objects in the repository which have names that contain the input string """
        raise NotImplementedError

    @abc.abstractmethod
    def add_review(self, review: Review):
        """ Adds a Review to the repository.

        If the Review doesn't have bidirectional links with a Book and a User, this method raises a
        RepositoryException and doesn't update the repository.
        """
        if review.user is None or review not in review.user.reviews:
            raise RepositoryException('Review not correctly attached to a User')
        if review.book is None or review not in review.book.reviews:
            raise RepositoryException('Review not correctly attached to a Book')

    @abc.abstractmethod
    def get_reviews(self):
        """ Returns the Reviews stored in the repository. """
        raise NotImplementedError
