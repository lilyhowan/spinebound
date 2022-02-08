from typing import Iterable

from library.adapters.repository import AbstractRepository
from library.domain.model import make_review, Book, Review, User


class NonExistentBookException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def get_book_by_id(book_id: int, repo: AbstractRepository):
    book = repo.get_book(book_id)

    if book is None:
        raise NonExistentBookException

    return book_to_dict(book)


def add_or_remove_book_from_favourites(book_id: int, user_name: str, repo: AbstractRepository):
    user = repo.get_user(user_name)
    book = repo.get_book(book_id)
    if user is not None and book is not None:
        repo.update_favourites(user, book)


def check_if_book_in_favourites(book_id: int, user_name: str, repo: AbstractRepository):
    user = repo.get_user(user_name)
    book = repo.get_book(book_id)
    if user is not None and book is not None:
        if book in user.favourites:
            return True
    return False


def get_reviews_for_book(book_id: int, repo: AbstractRepository):
    book = repo.get_book(book_id)

    if book is None:
        raise NonExistentBookException

    return reviews_to_dict(book.reviews)


def add_review(book_id: int, review_text: str, rating: int, user_name: str, repo: AbstractRepository):
    # Check that the book exists
    book = repo.get_book(book_id)
    if book is None:
        raise NonExistentBookException

    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException

    # Create review
    review = make_review(user, book, review_text, rating)

    # Update the repository
    repo.add_review(review)


def calculate_rating_stats(book_id: int, repo: AbstractRepository):
    book = repo.get_book(book_id)
    if book is None:
        raise NonExistentBookException

    ratings = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    count = 0

    for review in book.reviews:
        ratings[review.rating] += 1
        count += 1

    if count < 1:
        return {'average': 0, 'stars': 0}

    avg_rating = round((1 * ratings[1] + 2 * ratings[2] + 3 * ratings[3] + 4 * ratings[4] + 5 * ratings[5]) / count, 1)

    if avg_rating >= 4.5:
        stars = 5
    elif 4.5 > avg_rating >= 3.5:
        stars = 4
    elif 3.5 > avg_rating >= 2.5:
        stars = 3
    elif 2.5 > avg_rating >= 1.5:
        stars = 2
    elif 1.5 > avg_rating >= 0.5:
        stars = 1
    else:
        stars = 0

    return {'average': avg_rating, 'stars': stars}


# ============================================
# Functions to convert model entities to dicts
# ============================================

def book_to_dict(book: Book):
    authors = []
    for author in book.authors:
        authors.append((author.unique_id, author.full_name))

    book_dict = {
        'id': book.book_id,
        'title': book.title,
        'description': book.description,
        'publisher': book.publisher.name,
        'authors': authors,
        'release_year': book.release_year,
        'ebook': book.ebook,
        'num_pages': book.num_pages,
        'image_url': book.image_url,
        'reviews': reviews_to_dict(book.reviews)
    }
    return book_dict


def review_to_dict(review: Review):
    review_dict = {
        'user_name': review.user.user_name,
        'book_id': review.book.book_id,
        'review_text': review.review_text,
        'rating': review.rating,
        'timestamp': review.timestamp.strftime('%b %d %Y')
    }
    return review_dict


def reviews_to_dict(reviews: Iterable[Review]):
    review_list = []
    for review in reviews:
        review_list.append(review_to_dict(review))
    return review_list
