from datetime import datetime
from typing import List, Iterable


class Publisher:

    def __init__(self, publisher_name: str):
        # This makes sure the setter is called here in the initializer/constructor as well.
        self.name = publisher_name
        self.__books: List[Book] = list()

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, publisher_name: str):
        self.__name = "N/A"
        if isinstance(publisher_name, str):
            # Make sure leading and trailing whitespace is removed.
            publisher_name = publisher_name.strip()
            if publisher_name != "":
                self.__name = publisher_name

    @property
    def books(self) -> List['Book']:
        return self.__books

    def add_book(self, book: 'Book'):
        if not isinstance(book, Book):
            return

        if book in self.__books:
            return

        self.__books.append(book)

    def remove_book(self, book: 'Book'):
        if not isinstance(book, Book):
            return

        if book in self.__books:
            self.__books.remove(book)

    def __repr__(self):
        return f'<Publisher {self.name}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.name == self.name

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)


class Author:

    def __init__(self, author_id: int, author_full_name: str):
        if not isinstance(author_id, int):
            raise ValueError

        if author_id < 0:
            raise ValueError

        self.__unique_id = author_id

        # Uses the attribute setter method.
        self.full_name = author_full_name

        self.__books = []

        # Initialize author colleagues data structure with empty set.
        # We use a set so each unique author is only represented once.
        self.__authors_this_one_has_worked_with = set()

    @property
    def unique_id(self) -> int:
        return self.__unique_id

    @property
    def full_name(self) -> str:
        return self.__full_name

    @full_name.setter
    def full_name(self, author_full_name: str):
        if isinstance(author_full_name, str):
            # make sure leading and trailing whitespace is removed
            author_full_name = author_full_name.strip()
            if author_full_name != "":
                self.__full_name = author_full_name
            else:
                raise ValueError
        else:
            raise ValueError

    @property
    def books(self) -> List['Book']:
        return self.__books

    def add_book(self, book: 'Book'):
        if not isinstance(book, Book):
            return

        if book in self.__books:
            return

        self.__books.append(book)

    def remove_book(self, book: 'Book'):
        if not isinstance(book, Book):
            return

        if book in self.__books:
            self.__books.remove(book)

    def add_coauthor(self, coauthor):
        if isinstance(coauthor, self.__class__) and coauthor.unique_id != self.unique_id:
            self.__authors_this_one_has_worked_with.add(coauthor)

    def check_if_this_author_coauthored_with(self, author):
        return author in self.__authors_this_one_has_worked_with

    def __repr__(self):
        return f'<Author {self.full_name}, author id = {self.unique_id}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.unique_id == other.unique_id

    def __lt__(self, other):
        return self.unique_id < other.unique_id

    def __hash__(self):
        return hash(self.unique_id)


class Book:

    def __init__(self, book_id: int, book_title: str):
        if not isinstance(book_id, int):
            raise ValueError

        if book_id < 0:
            raise ValueError

        self.__book_id = book_id

        # use the attribute setter
        self.title = book_title

        self.__description = None
        self.__publisher = None
        self.__authors = []
        self.__release_year = None
        self.__ebook = None
        self.__num_pages = None
        self.__image_url = None
        self.__reviews: List[Review] = list()
        self.__users_who_favourited: List[User] = list()

    @property
    def book_id(self) -> int:
        return self.__book_id

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, book_title: str):
        if isinstance(book_title, str):
            book_title = book_title.strip()
            if book_title != "":
                self.__title = book_title
            else:
                raise ValueError
        else:
            raise ValueError

    @property
    def reviews(self) -> Iterable['Review']:
        return iter(self.__reviews)

    def add_review(self, review: 'Review'):
        if isinstance(review, Review):
            # Review objects are in practice always considered different due to their timestamp.
            self.__reviews.insert(0, review)

    @property
    def release_year(self) -> int:
        return self.__release_year

    @release_year.setter
    def release_year(self, release_year: int):
        if isinstance(release_year, int) and release_year >= 0:
            self.__release_year = release_year
        else:
            raise ValueError

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, description: str):
        if isinstance(description, str):
            self.__description = description.strip()

    @property
    def publisher(self) -> Publisher:
        return self.__publisher

    @publisher.setter
    def publisher(self, publisher: Publisher):
        if isinstance(publisher, Publisher):
            self.__publisher = publisher
        else:
            self.__publisher = None

    @property
    def authors(self) -> List[Author]:
        return self.__authors

    def add_author(self, author: Author):
        if not isinstance(author, Author):
            return

        if author in self.__authors:
            return

        self.__authors.append(author)

    def remove_author(self, author: Author):
        if not isinstance(author, Author):
            return

        if author in self.__authors:
            self.__authors.remove(author)

    @property
    def users_who_favourited(self) -> List['User']:
        return self.__users_who_favourited

    def add_user(self, user: 'User'):
        if not isinstance(user, User):
            return

        if user in self.__users_who_favourited:
            return

        self.__users_who_favourited.append(user)

    def remove_user(self, user: 'User'):
        if not isinstance(user, User):
            return

        if user in self.__users_who_favourited:
            self.__users_who_favourited.remove(user)

    @property
    def ebook(self) -> bool:
        return self.__ebook

    @ebook.setter
    def ebook(self, is_ebook: bool):
        if isinstance(is_ebook, bool):
            self.__ebook = is_ebook

    @property
    def num_pages(self) -> int:
        return self.__num_pages

    @num_pages.setter
    def num_pages(self, num_pages: int):
        if isinstance(num_pages, int) and num_pages > 0:
            self.__num_pages = num_pages

    @property
    def image_url(self) -> str:
        return self.__image_url

    @image_url.setter
    def image_url(self, image_url: str):
        if isinstance(image_url, str) and len(image_url) > 0:
            self.__image_url = image_url

    def __repr__(self):
        return f'<Book {self.title}, book id = {self.book_id}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.book_id == other.book_id

    def __lt__(self, other):
        return self.book_id < other.book_id

    def __hash__(self):
        return hash(self.book_id)


class User:

    def __init__(self, user_name: str, password: str):
        if user_name == "" or not isinstance(user_name, str):
            self.__user_name = None
        else:
            self.__user_name = user_name.strip().lower()

        if password == "" or not isinstance(password, str) or len(password) < 7:
            self.__password = None
        else:
            self.__password = password

        self.__favourites = []
        self.__read_books = []
        self.__reviews = []
        self.__pages_read = 0

    @property
    def user_name(self) -> str:
        return self.__user_name

    @property
    def password(self) -> str:
        return self.__password

    @property
    def favourites(self) -> List[Book]:
        return self.__favourites

    @property
    def read_books(self) -> List[Book]:
        return self.__read_books

    @property
    def reviews(self) -> Iterable['Review']:
        return iter(self.__reviews)

    @property
    def pages_read(self) -> int:
        return self.__pages_read

    def favourite_a_book(self, book: Book):
        if isinstance(book, Book) and book not in self.__favourites:
            self.__favourites.append(book)

    def unfavourite_a_book(self, book: Book):
        if isinstance(book, Book) and book in self.__favourites:
            self.__favourites.remove(book)

    def read_a_book(self, book: Book):
        if isinstance(book, Book):
            self.__read_books.append(book)
            if book.num_pages is not None:
                self.__pages_read += book.num_pages

    def add_review(self, review: 'Review'):
        if isinstance(review, Review):
            # Review objects are in practice always considered different due to their timestamp.
            self.__reviews.insert(0, review)

    def __repr__(self):
        return f'<User {self.user_name}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.user_name == self.user_name

    def __lt__(self, other):
        return self.user_name < other.user_name

    def __hash__(self):
        return hash(self.user_name)


class Review:

    def __init__(self, user: User, book: Book, review_text: str, rating: int):
        if isinstance(user, User):
            self.__user = user
        else:
            self.__user = None

        if isinstance(book, Book):
            self.__book = book
        else:
            self.__book = None

        if isinstance(review_text, str):
            self.__review_text = review_text.strip()
        else:
            self.__review_text = "N/A"

        if isinstance(rating, int) and 1 <= rating <= 5:
            self.__rating = rating
        else:
            raise ValueError

        self.__timestamp = datetime.now()

    @property
    def user(self) -> User:
        return self.__user

    @property
    def book(self) -> Book:
        return self.__book

    @property
    def review_text(self) -> str:
        return self.__review_text

    @property
    def rating(self) -> int:
        return self.__rating

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return other.book == self.book and other.review_text == self.review_text \
               and other.rating == self.rating and other.timestamp == self.timestamp

    def __repr__(self):
        return f'<Review of book {self.book}, rating = {self.rating}, timestamp = {self.timestamp}>'


class ModelException(Exception):
    pass


def make_review(user: User, book: Book, review_text: str, rating: int):
    review = Review(user, book, review_text, rating)
    user.add_review(review)
    book.add_review(review)

    return review


def make_author_association(book: Book, author: Author):
    if author in book.authors:
        raise ModelException(f'Author {author.full_name} already applied to Book "{book.title}"')

    book.add_author(author)
    author.add_book(book)


def make_publisher_association(book: Book, publisher: Publisher):
    if book.publisher == publisher:
        raise ModelException(f'Publisher {publisher.name} already applied to Book "{book.title}"')

    book.publisher = publisher
    publisher.add_book(book)
