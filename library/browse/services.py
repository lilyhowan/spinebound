from typing import Iterable

from library.adapters.repository import AbstractRepository
from library.domain.model import Book, Review
from library.book.services import calculate_rating_stats


class NonExistentBookException(Exception):
    pass


def get_books_by_id(id_list, repo: AbstractRepository):
    # Convert list -> set -> list to remove duplicates
    print(id_list)
    id_list = list(set(id_list))
    return books_to_dict(repo.get_books(id_list))


def get_book_ids(repo: AbstractRepository):
    return repo.get_all_book_ids()


def get_favourite_book_ids(user_name: str, repo: AbstractRepository):
    user = repo.get_user(user_name)
    if user is None:
        return []
    print([book.book_id for book in user.favourites])
    return [book.book_id for book in user.favourites]


def get_book_ids_by_title(title_string: str, repo: AbstractRepository):
    return repo.partial_search_books_by_title(title_string)


def get_book_ids_by_author(author_string: str, repo: AbstractRepository):
    matching_book_ids = []
    matching_authors = repo.partial_search_authors(author_string)
    return repo.get_book_ids_by_multiple_authors(matching_authors)


def get_book_ids_by_publisher(publisher_string: str, repo: AbstractRepository):
    matching_book_ids = []
    matching_publishers = repo.partial_search_publishers(publisher_string)
    return repo.get_book_ids_by_multiple_publishers(matching_publishers)


def get_book_ids_by_year(year_input: int, repo: AbstractRepository):
    return repo.get_book_ids_by_year(year_input)


# Takes list of book ids as input, then fetches the Book objects and sorts them according to sort_by
def sort_books(book_ids, sort_by: str, repo: AbstractRepository):
    books = get_books_by_id(book_ids, repo)

    if sort_by == 'ascending':
        return sorted(books, key=lambda x: (x['release_year'] is None, x['release_year']))
    elif sort_by == 'descending':
        return sorted(books, key=lambda x: (x['release_year'] is not None, x['release_year']), reverse=True)
    elif sort_by == 'best_reviewed':
        return sorted(books, key=lambda x: calculate_rating_stats(x['id'], repo)['average'], reverse=True)
    elif sort_by == 'most_reviewed':
        return sorted(books, key=lambda x: len(x['reviews']), reverse=True)
    else:
        # Sort by title (alphabetical) by default
        return sorted(books, key=lambda x: x['title'])


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


def books_to_dict(books: Iterable[Book]):
    return [book_to_dict(book) for book in books]


def review_to_dict(review: Review):
    review_dict = {
        'user_name': review.user.user_name,
        'book_id': review.book.book_id,
        'review_text': review.review_text,
        'rating': review.rating,
        'timestamp': review.timestamp
    }
    return review_dict


def reviews_to_dict(reviews: Iterable[Review]):
    review_list = []
    for review in reviews:
        review_list.append(review_to_dict(review))
    return review_list
