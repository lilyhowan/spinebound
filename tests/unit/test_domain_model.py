from datetime import datetime
from pathlib import Path
from typing import Iterable

import pytest

from utils import get_project_root

from library.domain.model import Publisher, Author, Book, Review, User, make_review, make_author_association, \
    ModelException, make_publisher_association
from library.adapters.json_data_reader import BooksJSONReader


@pytest.fixture()
def user():
    return User('lily', 'Password1')


@pytest.fixture()
def book():
    return Book(874658, "Harry Potter")


@pytest.fixture()
def author():
    return Author(123312, "Jane")


@pytest.fixture()
def publisher():
    return Publisher("Books Inc")


@pytest.fixture()
def review():
    return Review(user, book, "Review text", 5)


class TestPublisher:

    def test_construction(self):
        publisher1 = Publisher("Avatar Press")
        assert str(publisher1) == "<Publisher Avatar Press>"

        publisher2 = Publisher("  ")
        assert str(publisher2) == "<Publisher N/A>"

        publisher3 = Publisher("  DC Comics ")
        assert str(publisher3) == "<Publisher DC Comics>"

        publisher4 = Publisher(42)
        assert str(publisher4) == "<Publisher N/A>"

    def test_comparison(self):
        publisher1 = Publisher("Avatar Press")
        publisher2 = Publisher("DC Comics")
        publisher3 = Publisher("Avatar Press")
        publisher4 = Publisher("")
        assert str(publisher4) == "<Publisher N/A>"
        assert publisher1 == publisher3
        assert publisher1 != publisher2
        assert publisher3 != publisher2
        assert publisher2 != publisher3

    def test_sorting(self):
        publisher1 = Publisher("Avatar Press")
        publisher2 = Publisher("Penguin Books")
        publisher3 = Publisher("DC Comics")
        assert publisher1 < publisher2
        assert publisher1 < publisher3
        assert publisher2 > publisher3

    def test_set_operations(self):
        publisher1 = Publisher("Avatar Press")
        publisher2 = Publisher("DC Comics")
        publisher3 = Publisher("Avatar Press")
        set_of_publisher = set()
        set_of_publisher.add(publisher1)
        set_of_publisher.add(publisher2)
        set_of_publisher.add(publisher3)
        assert str(sorted(set_of_publisher)) == "[<Publisher Avatar Press>, <Publisher DC Comics>]"

    def test_attribute_setters(self):
        publisher1 = Publisher("Avatar Press")
        assert str(publisher1) == "<Publisher Avatar Press>"
        assert publisher1.name == "Avatar Press"
        publisher1.name = "DC Comics"
        assert str(publisher1) == "<Publisher DC Comics>"

    def test_adding_book(self):
        book = Book(84765876, "Harry Potter")
        publisher = Publisher("Avatar Press")
        publisher.add_book(book)
        assert isinstance(publisher.books, list)
        assert isinstance(publisher.books[0], Book)
        assert str(publisher.books) == "[<Book Harry Potter, book id = 84765876>]"

        assert len(publisher.books) == 1

        # Invalid input
        publisher.add_book(92)
        assert len(publisher.books) == 1

    def test_removing_book(self):
        book = Book(84765876, "Harry Potter")
        publisher = Publisher("Avatar Press")
        publisher.add_book(book)
        assert len(publisher.books) == 1

        # Book not in list
        publisher.remove_book(Book(123, "Nonexistent book"))
        assert len(publisher.books) == 1

        # Invalid input
        publisher.remove_book("Invalid book")
        assert len(publisher.books) == 1

        # Book in list
        publisher.remove_book(book)
        assert len(publisher.books) == 0


class TestAuthor:

    def test_construction(self):
        author = Author(3675, "J.R.R. Tolkien")
        assert str(author) == "<Author J.R.R. Tolkien, author id = 3675>"

        with pytest.raises(ValueError):
            author = Author(123, "  ")

        with pytest.raises(ValueError):
            author = Author(42, 42)

    def test_comparison(self):
        author1 = Author(1, "J.R.R. Tolkien")
        author2 = Author(2, "Neil Gaiman")
        author3 = Author(3, "J.K. Rowling")
        assert author1 != author3
        assert author1 != author2
        assert author3 != author2

    def test_comparison_with_identical_author_ids(self):
        # for two authors to be the same, our specification just asks for the unique id to match!
        author1 = Author(1, "Angelina Jolie")
        author2 = Author(2, "Angelina Jolie")
        author3 = Author(1, "J.K. Rowling")
        assert author1 == author3
        assert author1 != author2
        assert author3 != author2

    def test_sorting_names_and_ids_same_sort_order(self):
        author1 = Author(1, "J.K. Rowling")
        author2 = Author(2, "J.R.R. Tolkien")
        author3 = Author(3, "Neil Gaiman")
        assert author1 < author2
        assert author1 < author3
        assert author3 > author2

    def test_sorting_names_and_ids_differ_in_sort_order(self):
        author1 = Author(1, "Neil Gaiman")
        author2 = Author(2, "J.K. Rowling")
        author3 = Author(3, "J.R.R. Tolkien")
        assert author1 < author2
        assert author1 < author3
        assert author3 > author2

    def test_sorting_names_are_alphabetical(self):
        author1 = Author(13, "J.R.R. Tolkien")
        author2 = Author(2, "Neil Gaiman")
        author3 = Author(98, "J.K. Rowling")
        assert author1 > author2
        assert author1 < author3
        assert author3 > author2

    def test_set_operations(self):
        author1 = Author(13, "J.R.R. Tolkien")
        author2 = Author(2, "Neil Gaiman")
        author3 = Author(98, "J.K. Rowling")
        set_of_authors = set()
        set_of_authors.add(author1)
        set_of_authors.add(author2)
        set_of_authors.add(author3)
        assert str(sorted(
            set_of_authors)) == "[<Author Neil Gaiman, author id = 2>, <Author J.R.R. Tolkien, author id = 13>, <Author J.K. Rowling, author id = 98>]"

    def test_coauthors(self):
        author1 = Author(1, "Neil Gaiman")
        author2 = Author(2, "J.K. Rowling")
        author3 = Author(3, "J.R.R. Tolkien")
        author4 = Author(4, "Barack Obama")
        author1.add_coauthor(author2)
        author1.add_coauthor(author3)
        assert author1.check_if_this_author_coauthored_with(author2) is True
        assert author1.check_if_this_author_coauthored_with(author3) is True
        assert author1.check_if_this_author_coauthored_with(author4) is False
        assert author2.check_if_this_author_coauthored_with(author1) is False
        author2.add_coauthor(author1)
        assert author2.check_if_this_author_coauthored_with(author1) is True

    def test_coauthor_same_as_author(self):
        author = Author(1, "Neil Gaiman")
        author.add_coauthor(author)
        assert author.check_if_this_author_coauthored_with(author) is False

    def test_invalid_author_ids(self):
        author = Author(0, "J.R.R. Tolkien")
        assert str(author) == "<Author J.R.R. Tolkien, author id = 0>"

        with pytest.raises(ValueError):
            author = Author(-1, "J.R.R. Tolkien")

        with pytest.raises(ValueError):
            author = Author(13.786, "J.R.R. Tolkien")

        with pytest.raises(ValueError):
            author = Author(Publisher("DC Comics"), "J.R.R. Tolkien")

    def test_attribute_setters(self):
        author1 = Author(3675, "Barack Obama")
        assert str(author1) == "<Author Barack Obama, author id = 3675>"
        author1.full_name = "J.R.R. Tolkien"
        assert str(author1) == "<Author J.R.R. Tolkien, author id = 3675>"
        with pytest.raises(AttributeError):
            author1.unique_id = 12

    def test_adding_book(self):
        book = Book(84765876, "Harry Potter")
        author = Author(635, "J.K. Rowling")
        author.add_book(book)
        assert isinstance(author.books, list)
        assert isinstance(author.books[0], Book)
        assert str(author.books) == "[<Book Harry Potter, book id = 84765876>]"
        assert len(author.books) == 1

        # Invalid input
        author.add_book(92)
        assert len(author.books) == 1

    def test_removing_book(self):
        book = Book(84765876, "Harry Potter")
        author = Author(635, "J.K. Rowling")
        author.add_book(book)
        assert len(author.books) == 1

        # Book not in list
        author.remove_book(Book(123, "Nonexistent book"))
        assert len(author.books) == 1

        # Invalid input
        author.remove_book("Invalid book")
        assert len(author.books) == 1

        # Book in list
        author.remove_book(book)
        assert len(author.books) == 0


class TestBook:

    def test_construction_modification(self):
        book = Book(84765876, "Harry Potter")
        assert str(book) == "<Book Harry Potter, book id = 84765876>"

        publisher = Publisher("Bloomsbury")
        book.publisher = publisher
        assert str(book.publisher) == "<Publisher Bloomsbury>"
        assert isinstance(book.publisher, Publisher)

        book = Book(1, "    Harry Potter    ")
        assert str(book) == "<Book Harry Potter, book id = 1>"

    def test_adding_author(self):
        book = Book(84765876, "Harry Potter")
        author = Author(635, "J.K. Rowling")
        book.add_author(author)
        assert isinstance(book.authors, list)
        assert isinstance(book.authors[0], Author)
        assert str(book.authors) == "[<Author J.K. Rowling, author id = 635>]"
        assert len(book.authors) == 1

        # Invalid input
        book.add_author(84)
        assert len(book.authors) == 1

    def test_adding_review(self):
        book = Book(84765876, "Harry Potter")
        user = User("lily", "Password1")
        review = Review(user, book, "Review text", 3)

        book.add_review(review)
        assert isinstance(book.reviews, Iterable)
        assert isinstance(list(book.reviews)[0], Review)
        assert list(book.reviews)[0].review_text == "Review text"
        assert list(book.reviews)[0].rating == 3

        review2 = "This is not a review"
        book.add_review(review2)  # No review is added

        with pytest.raises(IndexError):
            print(list(book.reviews)[1].review_text)

    def test_attribute_setters(self):
        book = Book(84765876, "Harry Potter")
        book.description = "    Harry Potter was a highly unusual boy in many ways. For one thing, he hated the summer holidays more than any other time of year. For another, he really wanted to do his homework but was forced to do it in secret, in the dead of night. And he also happened to be a wizard.     "
        assert book.description == "Harry Potter was a highly unusual boy in many ways. For one thing, he hated the summer holidays more than any other time of year. For another, he really wanted to do his homework but was forced to do it in secret, in the dead of night. And he also happened to be a wizard."
        book.release_year = 1930
        assert book.release_year == 1930
        book.ebook = True
        assert book.ebook is True
        book.num_pages = 130
        assert book.num_pages == 130
        book.image_url = "https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png"
        assert book.image_url == "https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png"

    def test_attributes_fail(self):
        book = Book(84765876, "Harry Potter")

        book.num_pages = -1
        assert book.num_pages is None
        book.image_url = 3
        assert book.image_url is None
        book.image_url = ""
        assert book.image_url is None

        with pytest.raises(ValueError):
            book.release_year = -12

        with pytest.raises(ValueError):
            book.release_year = 3.5

        with pytest.raises(ValueError):
            book.title = 42

        with pytest.raises(AttributeError):
            book.book_id = 12

    def test_invalid_title(self):
        with pytest.raises(ValueError):
            book = Book(84765876, "")
        with pytest.raises(ValueError):
            book = Book(84765876, Publisher("DC Comics"))

    def test_invalid_book_ids(self):
        book = Book(0, "Harry Potter")
        assert str(book) == "<Book Harry Potter, book id = 0>"

        with pytest.raises(ValueError):
            book = Book(-1, "Harry Potter")

        with pytest.raises(ValueError):
            book = Book(13.786, "Harry Potter")

        with pytest.raises(ValueError):
            book = Book(Publisher("DC Comics"), "Harry Potter")

    def test_sorting(self):
        book1 = Book(874658, "Harry Potter")
        book2 = Book(2675376, "Hitchhiker's Guide to the Galaxy")
        book3 = Book(89576, "West Side Story")
        assert book1 < book2
        assert book1 > book3
        assert book2 > book3

    def test_set(self):
        book1 = Book(874658, "Harry Potter")
        book2 = Book(2675376, "Hitchhiker's Guide to the Galaxy")
        book3 = Book(89576, "West Side Story")
        set_of_books = set()
        set_of_books.add(book1)
        set_of_books.add(book2)
        set_of_books.add(book3)
        assert str(sorted(
            set_of_books)) == "[<Book West Side Story, book id = 89576>, <Book Harry Potter, book id = 874658>, <Book Hitchhiker's Guide to the Galaxy, book id = 2675376>]"

    def test_comparison(self):
        book1 = Book(874658, "Harry Potter")
        book2 = Book(2675376, "Hitchhiker's Guide to the Galaxy")
        book3 = Book(89576, "Harry Potter")
        book4 = Book(89576, "West Side Story")
        assert book1 != book2
        assert book1 != book3
        assert book3 == book4

    def test_remove_author(self):
        book = Book(89576, "Harry Potter")

        author1 = Author(1, "J.R.R. Tolkien")
        author2 = Author(2, "Neil Gaiman")
        author3 = Author(3, "Ernest Hemingway")
        author4 = Author(4, "J.K. Rowling")

        authors = [author1, author2, author3, author4]
        for author in authors:
            book.add_author(author)

        assert str(
            book.authors) == "[<Author J.R.R. Tolkien, author id = 1>, <Author Neil Gaiman, author id = 2>, <Author Ernest Hemingway, author id = 3>, <Author J.K. Rowling, author id = 4>]"

        # remove an Author who is not in the list
        book.remove_author(Author(5, "George Orwell"))
        assert str(
            book.authors) == "[<Author J.R.R. Tolkien, author id = 1>, <Author Neil Gaiman, author id = 2>, <Author Ernest Hemingway, author id = 3>, <Author J.K. Rowling, author id = 4>]"

        # remove an Author who is in the list
        book.remove_author(author2)
        assert str(
            book.authors) == "[<Author J.R.R. Tolkien, author id = 1>, <Author Ernest Hemingway, author id = 3>, <Author J.K. Rowling, author id = 4>]"

    def test_add_user_who_favourited(self):
        book = Book(89576, "Harry Potter")
        user = User("Nick", "Password1")

        # Invalid input
        book.add_user(1)
        assert len(book.users_who_favourited) == 0

        # Valid input
        book.add_user(user)
        assert len(book.users_who_favourited) == 1

    def test_remove_user(self):
        book = Book(89576, "Harry Potter")
        user = User("Nick", "Password1")
        book.add_user(user)

        # User not in list
        book.remove_user(User("Jane", "8w988832"))
        assert len(book.users_who_favourited) == 1

        # Invalid input
        book.remove_user(32)
        assert len(book.users_who_favourited) == 1

        # Valid user
        book.remove_user(user)
        assert len(book.users_who_favourited) == 0

class TestReview:

    def test_construction(self, user, book):
        review_text = "  This book was very enjoyable.   "
        rating = 4
        review = Review(user, book, review_text, rating)

        assert str(review.user) == "<User lily>"
        assert str(review.book) == "<Book Harry Potter, book id = 874658>"
        assert str(review.review_text) == "This book was very enjoyable."
        assert review.rating == 4

    def test_attributes_access(self, user, book):
        review = Review(user, book, 42, 3)

        assert str(review.user) == "<User lily>"
        assert str(review.book) == "<Book Harry Potter, book id = 874658>"
        assert str(review.review_text) == "N/A"
        assert review.rating == 3

    def test_invalid_parameters(self, user, book):
        review_text = "This book was very enjoyable."

        with pytest.raises(ValueError):
            review = Review(user, book, review_text, -1)

        with pytest.raises(ValueError):
            review = Review(user, book, review_text, 6)

    def test_set_of_reviews(self, user):
        book1 = Book(2675376, "Harry Potter")
        book2 = Book(874658, "Lord of the Rings")
        review1 = Review(user, book1, "I liked this book", 4)
        review2 = Review(user, book2, "This book was ok", 3)
        review3 = Review(user, book1, "This book was exceptional", 5)
        assert review1 != review2
        assert review1 != review3
        assert review3 != review2

    def test_wrong_book_object(self, user):
        publisher = Publisher("DC Comics")
        review = Review(user, publisher, "I liked this book", 4)
        assert review.book is None

    def test_wrong_user_object(self, book):
        publisher = Publisher("DC Comics")
        review = Review(publisher, book, "I liked this book", 4)
        assert review.user is None


class TestUser:

    def test_construction(self):
        user1 = User('Shyamli', 'pw12345')
        user2 = User('Martin', 'pw67890')
        user3 = User('Daniel', 'pw87465')
        assert str(user1) == "<User shyamli>"
        assert str(user2) == "<User martin>"
        assert str(user3) == "<User daniel>"

    def test_sort_ordering(self):
        user1 = User("Shyamli", "pw12345")
        user2 = User("Martin", "pw67890")
        user3 = User("daniel", "pw12345")
        assert user1 > user2
        assert user1 > user3
        assert user2 > user3

    def test_comparison(self):
        user1 = User("Martin", "pw12345")
        user2 = User("Shyamli", "pw67890")
        user3 = User("martin", "pw45673")
        assert user1 == user3
        assert user1 != user2
        assert user3 != user2

    def test_set_operations(self):
        user1 = User('Shyamli', 'pw12345')
        user2 = User('Martin', 'pw67890')
        user3 = User('Daniel', 'pw87465')
        set_of_users = set()
        set_of_users.add(user1)
        set_of_users.add(user2)
        set_of_users.add(user3)
        assert str(sorted(set_of_users)) == "[<User daniel>, <User martin>, <User shyamli>]"

    def test_reading_a_book(self):
        books = [Book(874658, "Harry Potter"), Book(89576, "Lord of the Rings")]
        books[0].num_pages = 107
        books[1].num_pages = 121
        user = User("Martin", "pw12345")
        assert user.read_books == []
        assert user.pages_read == 0
        for book in books:
            user.read_a_book(book)
        assert str(
            user.read_books) == "[<Book Harry Potter, book id = 874658>, <Book Lord of the Rings, book id = 89576>]"
        assert user.pages_read == 228

    def test_favoriting_a_book(self):
        books = [Book(874658, "Harry Potter"), Book(89576, "Lord of the Rings")]
        user = User("Martin", "pw12345")
        assert user.favourites == []
        for book in books:
            user.favourite_a_book(book)
        assert str(
            user.favourites) == "[<Book Harry Potter, book id = 874658>, <Book Lord of the Rings, book id = 89576>]"

        # Book is only added to favourites once
        user.favourite_a_book(books[1])
        assert str(
            user.favourites) == "[<Book Harry Potter, book id = 874658>, <Book Lord of the Rings, book id = 89576>]"

    def test_unfavoriting_a_book(self):
        books = [Book(874658, "Harry Potter"), Book(89576, "Lord of the Rings")]
        user = User("Martin", "pw12345")
        for book in books:
            user.favourite_a_book(book)

        user.unfavourite_a_book(books[0])
        assert str(user.favourites) == "[<Book Lord of the Rings, book id = 89576>]"

        user.unfavourite_a_book(books[1])
        assert user.favourites == []

    def test_cannot_favourite_or_unfavourite_invalid_book(self):
        books = [Book(874658, "Harry Potter"), 1]
        user = User("Martin", "pw12345")

        user.favourite_a_book(books[1])
        assert user.favourites == []

        user.unfavourite_a_book(books[1])
        assert user.favourites == []

        user.favourite_a_book(books[0])
        user.unfavourite_a_book(books[1])
        assert str(user.favourites) == "[<Book Harry Potter, book id = 874658>]"

    def test_user_reviews(self):
        books = [Book(874658, "Harry Potter"), Book(89576, "Lord of the Rings")]
        user = User("Martin", "pw12345")
        assert list(user.reviews) == []
        review1 = Review(user, books[0], "I liked this book", 4)
        review2 = Review(user, books[1], "This book was ok", 2)
        user.add_review(review1)
        user.add_review(review2)

        # Reviews are inserted at the front of the list
        assert str(list(user.reviews)[1].review_text) == "I liked this book"
        assert list(user.reviews)[1].rating == 4
        assert str(list(user.reviews)[0].review_text) == "This book was ok"
        assert list(user.reviews)[0].rating == 2

    def test_cannot_add_invalid_review(self):
        review = 25
        user = User("Martin", "pw12345")
        user.add_review(review)
        assert len(list(user.reviews)) == 0

    def test_passwords(self):
        user1 = User('  Shyamli   ', 'pw12345')
        user2 = User('Martin', 'p90')
        user3 = User('Lily', 2)
        assert str(user1) == "<User shyamli>"
        assert str(user1.password) == "pw12345"
        assert str(user2) == "<User martin>"
        assert user2.password is None
        assert user3.password is None


@pytest.fixture
def read_books_and_authors():
    books_file_name = 'comic_books_excerpt.json'
    authors_file_name = 'book_authors_excerpt.json'

    # we use a method from a utils file in the root folder to figure out the root
    # this way testing code is always finding the right path to the data files
    root_folder = get_project_root()
    data_folder = Path("tests/data")
    path_to_books_file = str(root_folder / data_folder / books_file_name)
    path_to_authors_file = str(root_folder / data_folder / authors_file_name)
    reader = BooksJSONReader(path_to_books_file, path_to_authors_file)
    reader.read_json_files()
    return reader.dataset_of_books, reader.author_book_associations, reader.publisher_book_associations


class TestBooksJSONReader:

    def test_read_books_from_file(self, read_books_and_authors):
        dataset_of_books = read_books_and_authors[0]
        assert str(dataset_of_books[0]) == "<Book Washington B.C (Ben 10 Comic Book), book id = 12413392>"
        assert str(dataset_of_books[10]) == "<Book The Thing: Idol of Millions, book id = 2168737>"
        assert str(dataset_of_books[11]) == "<Book D.Gray-man, Vol. 16: Blood & Chains, book id = 18955715>"

    def test_read_books_from_file_and_check_authors(self, read_books_and_authors):
        dataset_of_authors = read_books_and_authors[1]
        assert str(dataset_of_authors['169662'][0]) == "Duncan Rouleau"
        assert str(dataset_of_authors['853385'][0]) == "Chris  Martin"
        assert len(dataset_of_authors['618935']) - 1 == 1
        assert '35452242' in dataset_of_authors['853385']

    def test_read_books_from_file_and_check_publishers(self, read_books_and_authors):
        dataset_of_authors = read_books_and_authors[2]
        assert len(dataset_of_authors['Marvel']) == 1
        assert '2168737' in dataset_of_authors['Marvel']

    def test_read_books_from_file_and_check_other_attributes(self, read_books_and_authors):
        dataset_of_books = read_books_and_authors[0]
        assert dataset_of_books[3].release_year == 2012
        assert dataset_of_books[11].description == "Lenalee is determined to confront a Level 4 Akuma that's out to " \
                                                   "kill Komui, but her only chance is to reclaim her Innocence and " \
                                                   "synchronize with it. The Level 4 is not inclined to wait around " \
                                                   "and pursues its mission even against the best efforts of Lavi " \
                                                   "and Kanda. It's left to Allen to hold the line, but it soon " \
                                                   "becomes obvious he has no hope of doing it all by himself!"
        assert dataset_of_books[2].ebook is False
        assert dataset_of_books[11].ebook is True
        assert dataset_of_books[0].num_pages is None
        assert dataset_of_books[4].num_pages == 212
        assert dataset_of_books[6].num_pages == 329

    def test_read_books_from_file_special_characters(self, read_books_and_authors):
        dataset_of_books = read_books_and_authors[0]
        assert dataset_of_books[13].title == "續．星守犬"


def test_make_review_establishes_relationships(book, user):
    review_text = "I didn't enjoy this book"
    rating = 1
    review = make_review(user, book, review_text, rating)

    # Check that the User object knows about the Review
    assert review in user.reviews

    # Check that the Review knows about the User
    assert review.user is user

    # Check that Book knows about the Review
    assert review in book.reviews

    # Check that the Review knows about the Book
    assert review.book is book


def test_make_author_associations(book, author):
    make_author_association(book, author)

    # Check that the Book knows about the Author
    assert len(book.authors) > 0
    assert author in book.authors

    # check that the Author knows about the Book
    assert len(author.books) > 0
    assert book in author.books


def test_make_author_associations_with_book_already_associated(book, author):
    make_author_association(book, author)

    with pytest.raises(ModelException):
        make_author_association(book, author)


def test_make_publisher_associations(book, publisher):
    make_publisher_association(book, publisher)

    # Check that the Book knows about the Author
    assert book.publisher is not None
    assert publisher == book.publisher

    # check that the Author knows about the Book
    assert len(publisher.books) > 0
    assert book in publisher.books


def test_make_publisher_associations_with_book_already_associated(book, publisher):
    make_publisher_association(book, publisher)

    with pytest.raises(ModelException):
        make_publisher_association(book, publisher)
