import pytest

from flask import session


def test_register(client):
    # Check that we retrieve the register page
    response_code = client.get('/authentication/register').status_code
    assert response_code == 200

    # Check that we can register a user successfully, supplying a valid user name and password
    response = client.post(
        '/authentication/register',
        data={'user_name': 'gmichael', 'password': 'CarelessWhisper1984'}
    )
    assert response.headers['Location'] == 'http://localhost/authentication/login'


@pytest.mark.parametrize(('user_name', 'password', 'message'), (
        ('', '', b'User name is required'),
        ('cj', '', b'User name must be at least 3 characters'),
        ('test', '', b'Password is required'),
        ('test', 'test', b'Password must be at least 8 characters, and contain an upper case letter,\
            a lower case letter and a digit'),
        ('fmercury', 'Test#6^0', b'This user name is already taken - please supply another'),
))
def test_register_with_invalid_input(client, user_name, password, message):
    # Check that attempting to register with invalid combinations of user name and password generate appropriate error
    # messages
    response = client.post(
        '/authentication/register',
        data={'user_name': user_name, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    # Check that we can retrieve the login page
    status_code = client.get('/authentication/login').status_code
    assert status_code == 200

    # Check that a successful login generates a redirect to the homepage
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    # Check that a session has been created for the logged-in user
    with client:
        client.get('/')
        assert session['user_name'] == 'thorke'


def test_logout(client, auth):
    # Login a user
    auth.login()

    with client:
        # Check that logging out clears the user's session
        auth.logout()
        assert 'user_id' not in session


def test_index(client):
    # Check that we can retrieve the home page
    response = client.get('/')
    assert response.status_code == 200
    assert b'Spinebound' in response.data


def test_book(client):
    book_id = 18355356
    # Check that we can retrieve the book page
    response = client.get('/book?book_id=18355356')
    assert b'An Historical Introduction to American Education' in response.data

    # Check that the book page displays an error if a book_id is not provided
    response = client.get('/book')
    assert b"We're sorry, but this book could not be found" in response.data


def test_login_required_to_review(client):
    response = client.post('/review')
    assert response.headers['Location'] == 'http://localhost/authentication/login'


def test_review(client, auth):
    # Login a user
    auth.login()

    # Check that we can retrieve the review page
    response = client.get('/review?book_id=18355356')

    response = client.post(
        '/review?book_id=18355356',
        data={'review_text': 'Review', 'rating': 4}
    )
    assert response.headers['Location'] == 'http://localhost/book?book_id=18355356'

    # Check that the review page displays an error if a book_id is not provided
    response = client.get('/review')
    assert b"We're sorry, but this book could not be found" in response.data


@pytest.mark.parametrize(('review', 'messages'), (
        ('F**k this book', (b'Your review must not contain profanity')),
        ('Boo', (b'Your review must be at least 4 characters')),
        ('ass', (b'Your review must be at least 4 characters', b'Your review must not contain profanity')),
))
def test_review_with_invalid_input(client, auth, review, messages):
    # Login a user
    auth.login()

    # Attempt to review a book
    response = client.post(
        '/review?book_id=18355356',
        data={'review_text': review, 'rating': 2}
    )
    # Check that supplying invalid comment text generates appropriate error messages
    for message in messages:
        assert message in response.data


def test_browse(client):
    # Check that we can retrieve the browse page
    response = client.get('/browse/')
    assert response.status_code == 200

    # Check that without providing any search or sort query parameters the page includes the first book
    # (alphabetically) in the dataset and does not include books beyond the books per page limit (12)
    assert b"An Historical Introduction to American Education" in response.data
    assert b'XVI (XVI, #1)' not in response.data


def test_browse_with_books_per_page(client):
    # Check that we can retrieve the browse page
    response = client.get('/browse/?books_per_page=24')
    assert response.status_code == 200
    assert b"An Historical Introduction to American Education" in response.data
    assert b'XVI (XVI, #1)' in response.data


def test_book_with_reviews(client):
    # Check that we can retrieve the book page
    response = client.get('/book?book_id=12413392')
    assert response.status_code == 200

    # Check that all reviews for specified book are included on the page
    assert b'Washington B.C (Ben 10 Comic Book)' in response.data
    assert b'This is a review' in response.data


def test_login_required_for_bookshelf(client):
    book_id = 18355356
    response = client.post('/bookshelf/')
    assert response.headers['Location'] == 'http://localhost/authentication/login'


def test_bookshelf(client, auth):
    # Login a user
    auth.login()

    # Check that we can retrieve the review page
    response = client.get('/bookshelf/')
    assert response.status_code == 200
