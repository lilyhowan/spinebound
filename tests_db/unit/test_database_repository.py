from datetime import date, datetime

import pytest

import library.adapters.repository as repo
from library.adapters.database_repository import SqlAlchemyRepository
from library.domain.model import User, Book, Author, Publisher, Review, make_review
from library.adapters.repository import RepositoryException


def make_book():
    book = Book(1, "Fruits Basket")
    book.description = "Test description"
    book.release_year = 1998
    book.ebook = False
    book.num_pages = 136
    book.image_url = "https://cdn.myanimelist.net/images/manga/2/155964.jpg"
    return book


def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Dave', '123456789')
    repo.add_user(user)

    repo.add_user(User('Martin', '123456789'))

    user2 = repo.get_user('Dave')

    assert user2 == user and user2 is user


def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_book_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_books = repo.get_number_of_books()

    # Check that the query returned 20 Books.
    assert number_of_books == 20


def test_repository_can_add_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = make_book()
    repo.add_book(book)

    assert repo.get_book(1) == book


def test_repository_can_retrieve_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(18955715)
    print(book)

    # Check that the Book has the expected title.
    assert book.title == 'D.Gray-man, Vol. 16: Blood & Chains'

    # Check that the Book is reviewed as expected.
    review_one = [review for review in book.reviews if review.review_text == 'Could have been better'][0]
    review_two = [review for review in book.reviews if review.review_text == 'Great book'][0]

    assert review_one.user.user_name == 'thorke'
    assert review_two.user.user_name == 'fmercury'

    # Check that the Book has the expected authors
    assert Author(311098, "Katsura Hoshino") in book.authors


def test_repository_does_not_retrieve_a_non_existent_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(201)
    assert book is None


def test_repository_can_get_books_by_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    books = repo.get_books([707611, 13571772, 23272155])

    assert len(books) == 3
    assert books[0].title == 'Superman Archives, Vol. 2'
    assert books[1].title == "Captain America: Winter Soldier (The Ultimate Graphic Novels Collection: Publication Order, #7)"
    assert books[2].title == 'The Breaker New Waves, Vol 11'


def test_repository_does_not_retrieve_book_for_non_existent_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    books = repo.get_books([707611, 209])

    assert len(books) == 1
    assert books[0].title == 'Superman Archives, Vol. 2'


def test_repository_returns_an_empty_list_for_non_existent_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    books = repo.get_books([0, 199])
    assert len(books) == 0


def test_repository_can_retrieve_book_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_books = repo.get_number_of_books()
    assert number_of_books == 20


def test_repository_can_fully_search_by_title(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    title = 'The Breaker New Waves, Vol 11'
    matching_book_ids = repo.partial_search_books_by_title(title)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'The Breaker New Waves, Vol 11'


def test_repository_can_partially_search_by_title(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    title = 'The Breaker New Waves'
    matching_book_ids = repo.partial_search_books_by_title(title)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'The Breaker New Waves, Vol 11'


def test_repository_can_partially_search_by_title_lowercase(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    title = 'crossed'
    matching_book_ids = repo.partial_search_books_by_title(title)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_books) == 2
    assert Book(27036538, 'Crossed + One Hundred, Volume 2 (Crossed +100 #2)') in matching_books
    assert Book(27036537, 'Crossed, Volume 15') in matching_books


def test_repository_can_partially_search_by_title_with_surrounding_whitespace(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    title = ' crossed '
    matching_book_ids = repo.partial_search_books_by_title(title)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_books) == 2
    assert Book(27036538, 'Crossed + One Hundred, Volume 2 (Crossed +100 #2)') in matching_books
    assert Book(27036537, 'Crossed, Volume 15') in matching_books


def test_repository_partial_search_by_title_does_not_return_all_if_empty_string(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    title = ""
    matching_book_ids = repo.partial_search_books_by_title(title)
    matching_books = repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_partial_search_by_title_does_not_return_all_if_whitespace(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    title = "  "
    matching_book_ids = repo.partial_search_books_by_title(title)
    matching_books = repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_partial_search_by_title_does_not_return_all_if_invalid(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    title = 2
    matching_book_ids = repo.partial_search_books_by_title(title)
    matching_books = repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_get_all_book_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book_ids = repo.get_all_book_ids()

    assert len(book_ids) == 20


def test_repository_get_book_ids_by_year(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    year = 2016
    book_ids = repo.get_book_ids_by_year(year)
    books = repo.get_books(book_ids)

    assert len(books) == 5
    assert books[0].title == "War Stories, Volume 3"


def test_repository_get_book_ids_by_year_when_year_does_not_exist_or_invalid(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    year = 0
    book_ids = repo.get_book_ids_by_year(year)
    books = repo.get_books(book_ids)
    assert len(books) == 0

    year = "2005"
    book_ids = repo.get_book_ids_by_year(year)
    books = repo.get_books(book_ids)
    assert len(books) == 0


def test_repository_can_add_an_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = Author(134, "Nick")
    repo.add_author(author)

    assert repo.get_author(134) is author


def test_repository_can_retrieve_an_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = repo.get_author(24781)
    assert author == Author(24781, 'Dan Slott')


def test_repository_does_not_retrieve_a_non_existent_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = repo.get_author(1)
    assert author is None


def test_repository_get_all_authors(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    authors = repo.get_authors()

    # Only authors with books are added to the database from the data file
    assert len(authors) == 31

    author_one = [author for author in authors if author.full_name == 'Katsura Hoshino'][0]
    author_two = [author for author in authors if author.full_name == 'Rich Tommaso'][0]
    author_three = [author for author in authors if author.full_name == 'Naoki Urasawa'][0]

    assert len(author_one.books) == 1
    assert len(author_two.books) == 1
    assert len(author_three.books) == 3


def test_repository_get_book_ids_by_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = Author(169661, 'Kieron Dwyer')
    book_ids = repo.get_book_ids_by_author(author)
    books = repo.get_books(book_ids)

    assert len(books) == 1
    assert books[0].title == 'The Thing: Idol of Millions'


def test_repository_get_book_ids_by_author_when_author_does_not_exist(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = Author(1, 'Jane')
    book_ids = repo.get_book_ids_by_author(author)
    books = repo.get_books(book_ids)

    assert len(books) == 0


def test_repository_get_all_publishers(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publishers = repo.get_publishers()
    assert len(publishers) == 12


def test_repository_can_get_book_ids_by_authors(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book_ids = repo.get_book_ids_by_multiple_authors(
        [Author(169661, 'Kieron Dwyer'), Author(311098, 'Katsura Hoshino')])

    assert len(book_ids) == 2
    assert 2168737 in book_ids
    assert 18955715 in book_ids


def test_repository_does_not_retrieve_book_ids_for_non_existent_authors(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book_ids = repo.get_book_ids_by_multiple_authors(
        [Author(1, 'Jane'), Author(2, 'John'), Author(311098, 'Katsura Hoshino')])

    assert len(book_ids) == 1
    assert 18955715 in book_ids


def test_repository_returns_an_empty_list_for_non_existent_authors(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book_ids = repo.get_book_ids_by_multiple_authors([Author(1, 'Jane'), Author(2, 'John')])

    assert len(book_ids) == 0


def test_repository_can_fully_search_by_author_name(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = 'Katsura Hoshino'
    matching_authors = repo.partial_search_authors(author)
    matching_book_ids = repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_authors) == 1
    assert len(matching_books) == 1
    assert matching_books[0].title == 'D.Gray-man, Vol. 16: Blood & Chains'


def test_repository_can_partially_search_by_author_name(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = 'Katsura H'
    matching_authors = repo.partial_search_authors(author)
    matching_book_ids = repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_authors) == 1
    assert len(matching_books) == 1
    assert matching_books[0].title == 'D.Gray-man, Vol. 16: Blood & Chains'


def test_repository_can_partially_search_by_author_name_lowercase(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = 'katsura h'
    matching_authors = repo.partial_search_authors(author)
    matching_book_ids = repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_authors) == 1
    assert len(matching_books) == 1
    assert matching_books[0].title == 'D.Gray-man, Vol. 16: Blood & Chains'


def test_repository_can_partially_search_by_author_name_with_surrounding_whitespace(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = ' katsura h '
    matching_authors = repo.partial_search_authors(author)
    matching_book_ids = repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_authors) == 1
    assert len(matching_books) == 1
    assert matching_books[0].title == 'D.Gray-man, Vol. 16: Blood & Chains'


def test_repository_partial_search_by_author_name_does_not_return_all_if_empty_string(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = ""
    matching_authors = repo.partial_search_authors(author)
    matching_book_ids = repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_authors) == 0
    assert matching_books == []


def test_repository_partial_search_by_author_name_does_not_return_all_if_whitespace(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = "  "
    matching_authors = repo.partial_search_authors(author)
    matching_book_ids = repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_authors) == 0
    assert matching_books == []


def test_repository_partial_search_by_author_does_not_return_all_if_invalid(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = 2
    matching_authors = repo.partial_search_authors(author)
    matching_book_ids = repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_authors) == 0
    assert matching_books == []


def test_repository_can_add_and_retrieve_a_publisher(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = Publisher('Apple')
    repo.add_publisher(publisher)

    assert repo.get_publisher('Apple') is publisher


def test_repository_does_not_retrieve_a_non_existent_publisher(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = repo.get_publisher("a")
    assert publisher is None


def test_repository_get_book_ids_by_publisher(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = Publisher('Marvel')
    book_ids = repo.get_book_ids_by_publisher(publisher)
    books = repo.get_books(book_ids)

    assert len(books) == 1
    assert books[0].title == 'The Thing: Idol of Millions'


def test_repository_get_book_ids_by_publisher_when_publisher_does_not_exist(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = Publisher('Fake Publisher')
    book_ids = repo.get_book_ids_by_author(publisher)
    books = repo.get_books(book_ids)

    assert len(books) == 0


def test_repository_can_get_book_ids_by_publishers(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book_ids = repo.get_book_ids_by_multiple_publishers([Publisher('Marvel'), Publisher('Hakusensha')])

    assert len(book_ids) == 2
    assert 2168737 in book_ids
    assert 17405342 in book_ids


def test_repository_does_not_retrieve_book_ids_for_non_existent_publishers(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book_ids = repo.get_book_ids_by_multiple_publishers([Publisher('a'), Publisher('b'), Publisher('Hakusensha')])

    assert len(book_ids) == 1
    assert 17405342 in book_ids


def test_repository_returns_an_empty_list_for_non_existent_publishers(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book_ids = repo.get_book_ids_by_multiple_publishers([Publisher('a'), Publisher('b')])

    assert len(book_ids) == 0


def test_repository_can_fully_search_by_publisher_name(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = 'Marvel'
    matching_publishers = repo.partial_search_publishers(publisher)
    matching_book_ids = repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_publishers) == 1
    assert len(matching_books) == 1
    assert matching_books[0].title == 'The Thing: Idol of Millions'


def test_repository_can_partially_search_by_publisher_name(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = 'Mar'
    matching_publishers = repo.partial_search_publishers(publisher)
    matching_book_ids = repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_publishers) == 1
    assert len(matching_books) == 1
    assert matching_books[0].title == 'The Thing: Idol of Millions'


def test_repository_can_partially_search_by_publisher_name_lowercase(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = 'mar'
    matching_publishers = repo.partial_search_publishers(publisher)
    matching_book_ids = repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_publishers) == 1
    assert len(matching_books) == 1
    assert matching_books[0].title == 'The Thing: Idol of Millions'


def test_repository_can_partially_search_by_publisher_name_with_surrounding_whitespace(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = ' Marve   '
    matching_publishers = repo.partial_search_publishers(publisher)
    matching_book_ids = repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_publishers) == 1
    assert len(matching_books) == 1
    assert matching_books[0].title == 'The Thing: Idol of Millions'


def test_repository_partial_search_by_publisher_name_does_not_return_all_if_empty_string(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = ''
    matching_publishers = repo.partial_search_publishers(publisher)
    matching_book_ids = repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_publishers) == 0
    assert matching_books == []


def test_repository_partial_search_by_publisher_name_does_not_return_all_if_whitespace(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = '   '
    matching_publishers = repo.partial_search_publishers(publisher)
    matching_book_ids = repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_publishers) == 0
    assert matching_books == []


def test_repository_partial_search_by_publisher_name_does_not_return_all_if_invalid(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = 2
    matching_publishers = repo.partial_search_publishers(publisher)
    matching_book_ids = repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = repo.get_books(matching_book_ids)

    assert len(matching_publishers) == 0
    assert matching_books == []


def test_repository_can_add_a_review(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    book = repo.get_book(17405342)
    review = make_review(user, book, "This is a review", 5)

    repo.add_review(review)

    assert review in repo.get_reviews()


def test_repository_does_not_add_a_review_without_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(17405342)
    review = Review(None, book, "This is a review", 5)

    with pytest.raises(RepositoryException):
        repo.add_review(review)


def test_repository_does_not_add_a_review_without_a_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    review = Review(user, None, "This is a review", 5)

    with pytest.raises(RepositoryException):
        repo.add_review(review)


def test_repository_does_not_add_a_review_without_a_user_properly_attached1(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    book = repo.get_book(17405342)
    review = Review(None, book, "This is a review", 2)

    # The ORM will associate the User and Book with the review automatically, so no exception is raised
    # like in the in-memory database
    user.add_review(review)
    book.add_review(review)

    # Despite the Review not referencing the User when created, the User is still associated with the Review
    assert review.user == user


def test_repository_does_not_add_a_review_without_a_user_properly_attached2(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    book = repo.get_book(17405342)
    review = Review(user, book, "This is a review", 2)

    book.add_review(review)

    # Despite the User not referencing the Review, the Review is still associated with the User
    assert review in user.reviews


def test_repository_does_not_add_a_review_without_a_book_properly_attached1(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    book = repo.get_book(17405342)
    review = Review(user, None, "This is a review", 2)

    user.add_review(review)
    book.add_review(review)

    # Despite the Review not referencing the Book when created, the Book is still associated with the Review
    assert review.book == book


def test_repository_does_not_add_a_review_without_a_book_properly_attached2(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    book = repo.get_book(17405342)
    review = Review(user, book, "This is a review", 2)

    user.add_review(review)

    # Despite the Book not referencing the Review, the Review is still associated with the Book
    assert review in book.reviews


def test_repository_can_retrieve_reviews(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    assert len(repo.get_reviews()) == 8

