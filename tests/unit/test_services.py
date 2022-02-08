from datetime import date

import pytest

from library.authentication.services import AuthenticationException, NameNotUniqueException, UnknownUserException
from library.book.services import NonExistentBookException
from library.browse import services as browse_services
from library.book import services as book_services
from library.authentication import services as auth_services
from library.domain.model import Book


class TestAuthServices:

    def test_adding_invalid_user(self, in_memory_repo):
        new_user_name = 'apple'
        new_password = 'abcd1A23'

        auth_services.add_user(new_user_name, new_password, in_memory_repo)

        # Try to add the same username and password
        with pytest.raises(NameNotUniqueException):
            auth_services.add_user(new_user_name, new_password, in_memory_repo)

        # Try to add the same username
        with pytest.raises(NameNotUniqueException):
            auth_services.add_user(new_user_name, '8989sdfjk', in_memory_repo)

    def test_authentication_with_valid_credentials(self, in_memory_repo):
        new_user_name = 'apple'
        new_password = 'abcd1A23'

        auth_services.add_user(new_user_name, new_password, in_memory_repo)

        assert auth_services.authenticate_user(new_user_name, new_password, in_memory_repo) is True

    def test_authentication_with_invalid_credentials(self, in_memory_repo):
        new_user_name = 'pmccartney'
        new_password = 'abcd1A23'

        auth_services.add_user(new_user_name, new_password, in_memory_repo)

        with pytest.raises(AuthenticationException):
            auth_services.authenticate_user(new_user_name, '0987654321', in_memory_repo)

    def test_add_and_get_valid_user(self, in_memory_repo):
        new_user_name = 'apple'
        new_password = 'abcd1A23'

        auth_services.add_user(new_user_name, new_password, in_memory_repo)
        user = auth_services.get_user(new_user_name, in_memory_repo)

        assert type(user) == dict
        assert user['user_name'] == 'apple'

    def test_get_invalid_user(self, in_memory_repo):
        user_name = 'apple'

        with pytest.raises(UnknownUserException):
            user = auth_services.get_user(user_name, in_memory_repo)


class TestBookServices:

    def test_get_book_by_valid_id(self, in_memory_repo):
        book_id = 12413392
        book = book_services.get_book_by_id(book_id, in_memory_repo)
        assert book['title'] == 'Washington B.C (Ben 10 Comic Book)'

    def test_cannot_get_book_by_invalid_id(self, in_memory_repo):
        book_id = 1
        with pytest.raises(book_services.NonExistentBookException):
            book_services.get_book_by_id(book_id, in_memory_repo)

    def test_get_reviews_for_existing_book(self, in_memory_repo):
        book_id = 12413392
        reviews = book_services.get_reviews_for_book(12413392, in_memory_repo)
        assert reviews[0]['review_text'] == "This is a review 2"
        assert reviews[1]['review_text'] == "This is a review 1"

    def test_cannot_get_reviews_for_non_existent_book(self, in_memory_repo):
        book_id = 7
        with pytest.raises(book_services.NonExistentBookException):
            book_services.get_reviews_for_book(book_id, in_memory_repo)

    def test_can_add_to_favourites(self, in_memory_repo):
        book_id = 30525379
        user_name = 'fmercury'

        book_services.add_or_remove_book_from_favourites(book_id, user_name, in_memory_repo)
        assert book_services.check_if_book_in_favourites(book_id, user_name, in_memory_repo) is True

        book_services.add_or_remove_book_from_favourites(book_id, 'testuser', in_memory_repo)
        assert book_services.check_if_book_in_favourites(book_id, 'testuser', in_memory_repo) is False

        book_services.add_or_remove_book_from_favourites(23523, user_name, in_memory_repo)
        assert book_services.check_if_book_in_favourites(23523, user_name, in_memory_repo) is False

    def test_can_remove_from_favourites(self, in_memory_repo):
        book_id = 30525379
        user_name = 'fmercury'

        book_services.add_or_remove_book_from_favourites(book_id, user_name, in_memory_repo)  # Add book
        book_services.add_or_remove_book_from_favourites(book_id, user_name, in_memory_repo)  # Remove book
        assert book_services.check_if_book_in_favourites(book_id, user_name, in_memory_repo) is False

    def test_cannot_add_nonexistent_book_to_favourites(self, in_memory_repo):
        book_id = 1
        user_name = 'fmercury'

        book_services.add_or_remove_book_from_favourites(book_id, user_name, in_memory_repo)
        assert book_services.check_if_book_in_favourites(book_id, user_name, in_memory_repo) is False

    def test_can_add_review(self, in_memory_repo):
        book_id = 30525379
        review_text = 'I loved it!'
        rating = 4
        user_name = 'fmercury'

        # Call the service layer to add the review
        book_services.add_review(book_id, review_text, rating, user_name, in_memory_repo)

        # Retrieve the reviews for the article from the repository
        reviews_as_dict = book_services.get_reviews_for_book(book_id, in_memory_repo)

        # Check that the reviews include a review with the new comment text.
        assert next(
            (dictionary['review_text'] for dictionary in reviews_as_dict if dictionary['review_text'] == review_text),
            None) is not None

    def test_cannot_add_review_for_non_existent_book(self, in_memory_repo):
        book_id = 7
        review_text = 'I loved it!'
        rating = 4
        user_name = 'fmercury'

        # Call the service layer to attempt to add the review
        with pytest.raises(book_services.NonExistentBookException):
            book_services.add_review(book_id, review_text, rating, user_name, in_memory_repo)

    def test_cannot_add_review_by_unknown_user(self, in_memory_repo):
        book_id = 30525379
        review_text = 'I loved it!'
        rating = 4
        user_name = 'abba'

        # Call the service layer to attempt to add the review
        with pytest.raises(book_services.UnknownUserException):
            book_services.add_review(book_id, review_text, rating, user_name, in_memory_repo)

    def test_calculate_rating_stats(self, in_memory_repo):
        book_id = 30525379
        review_text = 'I loved it!'
        rating = 4
        user_name = 'fmercury'

        book_services.add_review(book_id, review_text, rating, user_name, in_memory_repo)

        stats = book_services.calculate_rating_stats(book_id, in_memory_repo)

        assert stats == {'average': 4.0, 'stars': 4}

    def test_stats_for_invalid_id(self, in_memory_repo):
        book_id = 1
        with pytest.raises(NonExistentBookException):
            book_services.calculate_rating_stats(book_id, in_memory_repo)


class TestBrowseServices:

    def test_get_books_by_valid_ids(self, in_memory_repo):
        book_id = 12413392
        books = browse_services.get_books_by_id([book_id], in_memory_repo)
        assert len(books) == 1
        assert books[0]['title'] == 'Washington B.C (Ben 10 Comic Book)'

    def test_cannot_get_book_by_invalid_ids(self, in_memory_repo):
        book_id = 12413392

        books = browse_services.get_books_by_id([book_id, 12], in_memory_repo)
        assert len(books) == 1

        books = browse_services.get_books_by_id([5, 12], in_memory_repo)
        assert len(books) == 0

    def test_get_all_book_ids(self, in_memory_repo):
        book_ids = browse_services.get_book_ids(in_memory_repo);
        assert len(book_ids) == 14

    def test_get_favourite_book_ids(self, in_memory_repo):
        book_id = 30525379
        user_name = 'fmercury'

        assert browse_services.get_favourite_book_ids(user_name, in_memory_repo) == []

        book_services.add_or_remove_book_from_favourites(book_id, user_name, in_memory_repo)
        assert browse_services.get_favourite_book_ids(user_name, in_memory_repo) == [30525379]

    def test_get_book_ids_by_title(self, in_memory_repo):
        # Uses partial search - "Marvel" will be returned for input strings "Marvel", "marvel", "mar", "  marv ", etc.
        input1 = "The Fisherman"
        input2 = "fisherman"
        input3 = "Fis"
        input4 = "  fish "

        book_ids1 = browse_services.get_book_ids_by_title(input1, in_memory_repo)
        book_ids2 = browse_services.get_book_ids_by_title(input2, in_memory_repo)
        book_ids3 = browse_services.get_book_ids_by_title(input3, in_memory_repo)
        book_ids4 = browse_services.get_book_ids_by_title(input4, in_memory_repo)

        assert book_ids1 == book_ids2 == book_ids3 == book_ids4

    def test_get_book_ids_by_title_invalid_input(self, in_memory_repo):
        input1 = ""
        input2 = "   "
        input3 = "This title does not exist"
        input4 = 5

        book_ids1 = browse_services.get_book_ids_by_title(input1, in_memory_repo)
        book_ids2 = browse_services.get_book_ids_by_title(input2, in_memory_repo)
        book_ids3 = browse_services.get_book_ids_by_title(input3, in_memory_repo)
        book_ids4 = browse_services.get_book_ids_by_title(input4, in_memory_repo)

        assert book_ids1 == book_ids2 == book_ids3 == book_ids4

    def test_get_book_ids_by_author(self, in_memory_repo):
        input1 = "Joe Kelly"
        input2 = "joe k"
        input3 = "Joe ke"
        input4 = "  joe KelLy "

        book_ids1 = browse_services.get_book_ids_by_author(input1, in_memory_repo)
        book_ids2 = browse_services.get_book_ids_by_author(input2, in_memory_repo)
        book_ids3 = browse_services.get_book_ids_by_author(input3, in_memory_repo)
        book_ids4 = browse_services.get_book_ids_by_author(input4, in_memory_repo)

        assert book_ids1 == book_ids2 == book_ids3 == book_ids4

    def test_get_book_ids_by_author_invalid_input(self, in_memory_repo):
        input1 = "Joe33 Kelly"
        input2 = ""
        input3 = "        "
        input4 = True

        book_ids1 = browse_services.get_book_ids_by_author(input1, in_memory_repo)
        book_ids2 = browse_services.get_book_ids_by_author(input2, in_memory_repo)
        book_ids3 = browse_services.get_book_ids_by_author(input3, in_memory_repo)
        book_ids4 = browse_services.get_book_ids_by_author(input4, in_memory_repo)

        assert book_ids1 == book_ids2 == book_ids3 == book_ids4

    def test_get_book_ids_by_publisher(self, in_memory_repo):
        input1 = "Createspace"
        input2 = "createspace"
        input3 = "crea"
        input4 = "  CreaTeSpacE "

        book_ids1 = browse_services.get_book_ids_by_publisher(input1, in_memory_repo)
        book_ids2 = browse_services.get_book_ids_by_publisher(input2, in_memory_repo)
        book_ids3 = browse_services.get_book_ids_by_publisher(input3, in_memory_repo)
        book_ids4 = browse_services.get_book_ids_by_publisher(input4, in_memory_repo)

        assert book_ids1 == book_ids2 == book_ids3 == book_ids4

    def test_get_book_ids_by_publisher_invalid_input(self, in_memory_repo):
        input1 = "Creat   espace"
        input2 = 23.0
        input3 = " "
        input4 = ""

        book_ids1 = browse_services.get_book_ids_by_publisher(input1, in_memory_repo)
        book_ids2 = browse_services.get_book_ids_by_publisher(input2, in_memory_repo)
        book_ids3 = browse_services.get_book_ids_by_publisher(input3, in_memory_repo)
        book_ids4 = browse_services.get_book_ids_by_publisher(input4, in_memory_repo)

        assert book_ids1 == book_ids2 == book_ids3 == book_ids4

    def test_get_book_ids_by_year(self, in_memory_repo):
        # Must be a full match
        input1 = 2006
        input2 = 2013
        input3 = 2000

        book_ids1 = browse_services.get_book_ids_by_year(input1, in_memory_repo)
        book_ids2 = browse_services.get_book_ids_by_year(input2, in_memory_repo)
        book_ids3 = browse_services.get_book_ids_by_year(input3, in_memory_repo)

        assert len(book_ids1) == 2
        assert len(book_ids2) == 1
        assert len(book_ids3) == 0

    def test_get_book_ids_by_year_invalid_input(self, in_memory_repo):
        input1 = "2006"
        input2 = True

        book_ids1 = browse_services.get_book_ids_by_year(input1, in_memory_repo)
        book_ids2 = browse_services.get_book_ids_by_year(input2, in_memory_repo)

        assert len(book_ids1) == 0
        assert len(book_ids2) == 0

    def test_sort_books(self, in_memory_repo):
        # Book 1: 35452242, 'Bounty Hunter 4/3: My Life in Combat from Marine Scout Sniper to MARSOC',
        # 1 5 star review, publication year unknown
        # Book 2: 12413392, 'Washington B.C (Ben 10 Comic Book)', 1 3 star review and 1 2 star review,
        # year = 2005
        # Book 3: 16201706, 'Little Bigfoot Goes to Town', no reviews, year = 2012
        book_ids = [35452242, 12413392, 16201706]

        sorted_books = browse_services.sort_books(book_ids, 'ascending', in_memory_repo)
        assert sorted_books[0]['id'] == 12413392
        assert sorted_books[1]['id'] == 16201706
        assert sorted_books[2]['id'] == 35452242  # None is always at the end

        sorted_books = browse_services.sort_books(book_ids, 'descending', in_memory_repo)
        assert sorted_books[0]['id'] == 16201706
        assert sorted_books[1]['id'] == 12413392
        assert sorted_books[2]['id'] == 35452242  # None is always at the end

        sorted_books = browse_services.sort_books(book_ids, 'best_reviewed', in_memory_repo)
        assert sorted_books[0]['id'] == 35452242
        assert sorted_books[1]['id'] == 12413392
        assert sorted_books[2]['id'] == 16201706

        sorted_books = browse_services.sort_books(book_ids, 'most_reviewed', in_memory_repo)
        assert sorted_books[0]['id'] == 12413392
        assert sorted_books[1]['id'] == 35452242
        assert sorted_books[2]['id'] == 16201706

        # All remaining cases will sort alphabetically
        sorted_books = browse_services.sort_books(book_ids, 'alphabetical', in_memory_repo)
        assert sorted_books[0]['id'] == 35452242
        assert sorted_books[1]['id'] == 16201706
        assert sorted_books[2]['id'] == 12413392

        sorted_books = browse_services.sort_books(book_ids, 3, in_memory_repo)
        assert sorted_books[0]['id'] == 35452242
        assert sorted_books[1]['id'] == 16201706
        assert sorted_books[2]['id'] == 12413392

        sorted_books = browse_services.sort_books(book_ids, 'unknown', in_memory_repo)
        assert sorted_books[0]['id'] == 35452242
        assert sorted_books[1]['id'] == 16201706
        assert sorted_books[2]['id'] == 12413392
