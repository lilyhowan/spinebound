from pathlib import Path

import pytest

from library.adapters.repository import RepositoryException
from library.domain.model import Book, Author, Publisher, User, make_review, Review


def test_repository_can_add_a_user(in_memory_repo):
    user = User('dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_add_book(in_memory_repo):
    book = Book(984819, "Fruits Basket")
    in_memory_repo.add_book(book)

    assert in_memory_repo.get_book(984819) is book


def test_repository_can_retrieve_book(in_memory_repo):
    book = in_memory_repo.get_book(12413392)

    # Check that the Book has the expected properties
    assert book.title == "Washington B.C (Ben 10 Comic Book)"
    assert book.description == ""
    assert str(book.publisher) == "<Publisher N/A>"
    assert book.authors == [Author(169662, "Duncan Rouleau"), Author(23519, "Joe Casey"), Author(18119, "Joe Kelly"),
                            Author(29688, "Steven T. Seagle")]
    assert book.release_year == 2005
    assert book.ebook is False
    assert book.num_pages is None
    assert book.image_url == "https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png"

    review1 = [review for review in book.reviews if review.review_text == 'This is a review 1' and review.rating == 3]
    review2 = [review for review in book.reviews if review.review_text == 'This is a review 2' and review.rating == 2]


def test_repository_does_not_retrieve_a_non_existent_book(in_memory_repo):
    book = in_memory_repo.get_book(101)
    assert book is None


def test_repository_can_get_books_by_ids(in_memory_repo):
    books = in_memory_repo.get_books([12413392, 35452242, 780918])

    assert len(books) == 3
    assert books[0].title == 'Washington B.C (Ben 10 Comic Book)'
    assert books[1].title == "Bounty Hunter 4/3: My Life in Combat from Marine Scout Sniper to MARSOC"
    assert books[2].title == 'Rite of Conquest (William the Conqueror, #1)'


def test_repository_does_not_retrieve_book_for_non_existent_id(in_memory_repo):
    books = in_memory_repo.get_books([780918, 9])

    assert len(books) == 1
    assert books[0].title == 'Rite of Conquest (William the Conqueror, #1)'


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    books = in_memory_repo.get_books([0, 9])

    assert len(books) == 0


def test_repository_can_retrieve_book_count(in_memory_repo):
    number_of_books = in_memory_repo.get_number_of_books()

    # Check that the query returned 10 Books
    assert number_of_books == 14


def test_repository_can_fully_search_by_title(in_memory_repo):
    title = 'Rite of Conquest (William the Conqueror, #1)'
    matching_book_ids = in_memory_repo.partial_search_books_by_title(title)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'Rite of Conquest (William the Conqueror, #1)'


def test_repository_can_partially_search_by_title(in_memory_repo):
    title = 'Conquest (William the Conqueror, #1)'
    matching_book_ids = in_memory_repo.partial_search_books_by_title(title)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'Rite of Conquest (William the Conqueror, #1)'


def test_repository_can_partially_search_by_title_lowercase(in_memory_repo):
    title = 'america'
    matching_book_ids = in_memory_repo.partial_search_books_by_title(title)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 2
    assert Book(13571772, 'Captain America: Winter Soldier '
                          '(The Ultimate Graphic Novels Collection: Publication Order, #7)') in matching_books
    assert Book(18355356, 'An Historical Introduction to American Education') in matching_books


def test_repository_can_partially_search_by_title_with_surrounding_whitespace(in_memory_repo):
    title = ' america '
    matching_book_ids = in_memory_repo.partial_search_books_by_title(title)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 2
    assert Book(13571772, 'Captain America: Winter Soldier '
                          '(The Ultimate Graphic Novels Collection: Publication Order, #7)') in matching_books
    assert Book(18355356, 'An Historical Introduction to American Education') in matching_books


def test_repository_partial_search_by_title_does_not_return_all_if_empty_string(in_memory_repo):
    title = ""
    matching_book_ids = in_memory_repo.partial_search_books_by_title(title)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_partial_search_by_title_does_not_return_all_if_whitespace(in_memory_repo):
    title = "  "
    matching_book_ids = in_memory_repo.partial_search_books_by_title(title)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_partial_search_by_title_does_not_return_all_if_invalid(in_memory_repo):
    title = 2
    matching_book_ids = in_memory_repo.partial_search_books_by_title(title)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_get_all_book_ids(in_memory_repo):
    book_ids = in_memory_repo.get_all_book_ids()

    assert len(book_ids) == 14


def test_repository_get_book_ids_by_year(in_memory_repo):
    year = 2013
    book_ids = in_memory_repo.get_book_ids_by_year(year)
    books = in_memory_repo.get_books(book_ids)

    assert len(books) == 1
    assert books[0].title == "L'isola dell'amore proibito"


def test_repository_get_book_ids_by_year_when_year_does_not_exist_or_invalid(in_memory_repo):
    year = 0
    book_ids = in_memory_repo.get_book_ids_by_year(year)
    books = in_memory_repo.get_books(book_ids)
    assert len(books) == 0

    year = "2005"
    book_ids = in_memory_repo.get_book_ids_by_year(year)
    books = in_memory_repo.get_books(book_ids)
    assert len(books) == 0


def test_repository_can_add_an_author(in_memory_repo):
    author = Author(134, "Nick")
    in_memory_repo.add_author(author)

    assert in_memory_repo.get_author(134) is author


def test_repository_can_retrieve_an_author(in_memory_repo):
    author = in_memory_repo.get_author(18119)
    assert author == Author(18119, 'Joe Kelly')


def test_repository_does_not_retrieve_a_non_existent_author(in_memory_repo):
    author = in_memory_repo.get_author(1)
    assert author is None


def test_repository_get_all_authors(in_memory_repo):
    authors = in_memory_repo.get_authors()
    assert len(authors) == 20


def test_repository_get_book_ids_by_author(in_memory_repo):
    author = Author(6601585, 'Spike Brown')
    book_ids = in_memory_repo.get_book_ids_by_author(author)
    books = in_memory_repo.get_books(book_ids)

    assert len(books) == 1
    assert books[0].title == 'Little Bigfoot Goes to Town'


def test_repository_get_book_ids_by_author_when_author_does_not_exist(in_memory_repo):
    author = Author(1, 'Jane')
    book_ids = in_memory_repo.get_book_ids_by_author(author)
    books = in_memory_repo.get_books(book_ids)

    assert len(books) == 0


def test_repository_get_all_publishers(in_memory_repo):
    publishers = in_memory_repo.get_publishers()
    assert len(publishers) == 7


def test_repository_can_get_book_ids_by_authors(in_memory_repo):
    book_ids = in_memory_repo.get_book_ids_by_multiple_authors(
        [Author(6601585, 'Spike Brown'), Author(18119, 'Joe Kelly')])

    assert len(book_ids) == 2
    assert 12413392 in book_ids
    assert 16201706 in book_ids


def test_repository_does_not_retrieve_book_ids_for_non_existent_authors(in_memory_repo):
    book_ids = in_memory_repo.get_book_ids_by_multiple_authors(
        [Author(1, 'Jane'), Author(2, 'John'), Author(18119, 'Joe Kelly')])

    assert len(book_ids) == 1
    assert 12413392 in book_ids


def test_repository_returns_an_empty_list_for_non_existent_authors(in_memory_repo):
    book_ids = in_memory_repo.get_book_ids_by_multiple_authors([Author(1, 'Jane'), Author(2, 'John')])

    assert len(book_ids) == 0


def test_repository_can_fully_search_by_author_name(in_memory_repo):
    author = 'Joe Kelly'
    matching_authors = in_memory_repo.partial_search_authors(author)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'Washington B.C (Ben 10 Comic Book)'


def test_repository_can_partially_search_by_author_name(in_memory_repo):
    author = 'Joe K'
    matching_authors = in_memory_repo.partial_search_authors(author)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'Washington B.C (Ben 10 Comic Book)'


def test_repository_can_partially_search_by_author_name_lowercase(in_memory_repo):
    author = 'joe k'
    matching_authors = in_memory_repo.partial_search_authors(author)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'Washington B.C (Ben 10 Comic Book)'


def test_repository_can_partially_search_by_author_name_with_surrounding_whitespace(in_memory_repo):
    author = ' joe ke '
    matching_authors = in_memory_repo.partial_search_authors(author)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'Washington B.C (Ben 10 Comic Book)'


def test_repository_partial_search_by_author_name_does_not_return_all_if_empty_string(in_memory_repo):
    author = ""
    matching_authors = in_memory_repo.partial_search_authors(author)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_partial_search_by_author_name_does_not_return_all_if_whitespace(in_memory_repo):
    author = "  "
    matching_authors = in_memory_repo.partial_search_authors(author)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_partial_search_by_author_does_not_return_all_if_invalid(in_memory_repo):
    author = 2
    matching_authors = in_memory_repo.partial_search_authors(author)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_authors(matching_authors)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_can_add_and_retrieve_a_publisher(in_memory_repo):
    publisher = Publisher('Apple')
    in_memory_repo.add_publisher(publisher)

    assert in_memory_repo.get_publisher('Apple') is publisher


def test_repository_does_not_retrieve_a_non_existent_publisher(in_memory_repo):
    publisher = in_memory_repo.get_publisher("a")
    assert publisher is None


def test_repository_get_book_ids_by_publisher(in_memory_repo):
    publisher = Publisher('Ingram')
    book_ids = in_memory_repo.get_book_ids_by_publisher(publisher)
    books = in_memory_repo.get_books(book_ids)

    assert len(books) == 1
    assert books[0].title == 'An Historical Introduction to American Education'


def test_repository_get_book_ids_by_publisher_when_publisher_does_not_exist(in_memory_repo):
    publisher = Publisher('Fake Publisher')
    book_ids = in_memory_repo.get_book_ids_by_author(publisher)
    books = in_memory_repo.get_books(book_ids)

    assert len(books) == 0


def test_repository_can_get_book_ids_by_publishers(in_memory_repo):
    book_ids = in_memory_repo.get_book_ids_by_multiple_publishers([Publisher('Ingram'), Publisher('Createspace')])

    assert len(book_ids) == 2
    assert 18355356 in book_ids
    assert 16201706 in book_ids


def test_repository_does_not_retrieve_book_ids_for_non_existent_publishers(in_memory_repo):
    book_ids = in_memory_repo.get_book_ids_by_multiple_publishers([Publisher('a'), Publisher('b'), Publisher('Ingram')])

    assert len(book_ids) == 1
    assert 18355356 in book_ids


def test_repository_returns_an_empty_list_for_non_existent_publishers(in_memory_repo):
    book_ids = in_memory_repo.get_book_ids_by_multiple_publishers([Publisher('a'), Publisher('b')])

    assert len(book_ids) == 0


def test_repository_can_fully_search_by_publisher_name(in_memory_repo):
    publisher = 'Ingram'
    matching_publishers = in_memory_repo.partial_search_publishers(publisher)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'An Historical Introduction to American Education'


def test_repository_can_partially_search_by_publisher_name(in_memory_repo):
    publisher = 'Ing'
    matching_publishers = in_memory_repo.partial_search_publishers(publisher)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'An Historical Introduction to American Education'


def test_repository_can_partially_search_by_publisher_name_lowercase(in_memory_repo):
    publisher = 'ingr'
    matching_publishers = in_memory_repo.partial_search_publishers(publisher)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'An Historical Introduction to American Education'


def test_repository_can_partially_search_by_publisher_name_with_surrounding_whitespace(in_memory_repo):
    publisher = ' Ingram   '
    matching_publishers = in_memory_repo.partial_search_publishers(publisher)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert len(matching_books) == 1
    assert matching_books[0].title == 'An Historical Introduction to American Education'


def test_repository_partial_search_by_publisher_name_does_not_return_all_if_empty_string(in_memory_repo):
    publisher = ''
    matching_publishers = in_memory_repo.partial_search_publishers(publisher)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_partial_search_by_publisher_name_does_not_return_all_if_whitespace(in_memory_repo):
    publisher = '   '
    matching_publishers = in_memory_repo.partial_search_publishers(publisher)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_partial_search_by_publisher_name_does_not_return_all_if_invalid(in_memory_repo):
    publisher = 2
    matching_publishers = in_memory_repo.partial_search_publishers(publisher)
    matching_book_ids = in_memory_repo.get_book_ids_by_multiple_publishers(matching_publishers)
    matching_books = in_memory_repo.get_books(matching_book_ids)

    assert matching_books == []


def test_repository_can_add_a_review(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    book = in_memory_repo.get_book(12413392)
    review = make_review(user, book, "This is a review", 5)

    in_memory_repo.add_review(review)

    assert review in in_memory_repo.get_reviews()


def test_repository_does_not_add_a_review_without_a_user(in_memory_repo):
    book = in_memory_repo.get_book(12413392)
    review = Review(None, book, "This is a review", 5)

    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(review)


def test_repository_does_not_add_a_review_without_a_book(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    review = Review(user, None, "This is a review", 5)

    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(review)


def test_repository_does_not_add_a_review_without_a_user_properly_attached1(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    book = in_memory_repo.get_book(10866987)
    review = Review(None, book, "This is a review", 2)

    user.add_review(review)
    book.add_review(review)

    with pytest.raises(RepositoryException):
        # Exception expected because the Review doesn't refer to the User
        in_memory_repo.add_review(review)


def test_repository_does_not_add_a_review_without_a_user_properly_attached2(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    book = in_memory_repo.get_book(10866987)
    review = Review(user, book, "This is a review", 2)

    book.add_review(review)

    with pytest.raises(RepositoryException):
        # Exception expected because the User doesn't refer to the Review
        in_memory_repo.add_review(review)


def test_repository_does_not_add_a_review_without_a_book_properly_attached1(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    book = in_memory_repo.get_book(10866987)
    review = Review(user, None, "This is a review", 2)

    user.add_review(review)
    book.add_review(review)

    with pytest.raises(RepositoryException):
        # Exception expected because the Review doesn't refer to the Book
        in_memory_repo.add_review(review)


def test_repository_does_not_add_a_review_without_a_book_properly_attached2(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    book = in_memory_repo.get_book(10866987)
    review = Review(user, book, "This is a review", 2)

    user.add_review(review)

    with pytest.raises(RepositoryException):
        # Exception expected because the Book doesn't refer to the Review
        in_memory_repo.add_review(review)


def test_repository_can_retrieve_reviews(in_memory_repo):
    assert len(in_memory_repo.get_reviews()) == 3
