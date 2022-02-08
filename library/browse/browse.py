from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, ValidationError, Optional, NumberRange

import library.adapters.repository as repo
import library.browse.services as services

# Configure blueprint
from library.authentication.authentication import login_required

browse_blueprint = Blueprint(
    'browse_bp', __name__)


@browse_blueprint.route('/browse/', methods=['GET', 'POST'])
def browse():
    search_form = SearchForm()
    sort_form = SortForm()

    # Read query parameters
    count = request.args.get('count')
    sort_by = request.args.get('sort_by')
    books_per_page = request.args.get('books_per_page')

    if books_per_page != '12' and books_per_page != '18' and books_per_page != '24':
        books_per_page = '12'  # Default books per page

    if count is None:
        # Initialise cursor at beginning
        count = 0
    else:
        count = int(count)

    if request.method == 'GET':
        sort_form.sort_by.data = sort_by
        sort_form.books_per_page.data = books_per_page  # Must be a string

    # Must check if data exists and then validate rather than calling form.validate_on_submit()
    # in order to differentiate between the two forms
    if sort_form.sort_submit.data and sort_form.validate():
        return redirect(url_for('browse_bp.browse',
                                sort_by=sort_form.sort_by.data,
                                books_per_page=sort_form.books_per_page.data))

    # If successful POST, redirect to search result page
    if search_form.search_submit.data and search_form.validate():
        return redirect(url_for('browse_bp.search_result',
                                location='browse',
                                sort_by=sort_by,
                                books_per_page=books_per_page,
                                title=search_form.title.data,
                                author=search_form.author.data,
                                publisher=search_form.publisher.data,
                                year=search_form.year.data))

    books_per_page = int(books_per_page)
    book_ids = services.get_book_ids(repo.repo_instance)

    # Sort and retrieve books (default = alphabetical)
    matching_books = services.sort_books(book_ids, sort_by, repo.repo_instance)
    books = matching_books[count:count + books_per_page]  # Books to display

    next_page_url = None
    prev_page_url = None

    if count > 0:
        # There are preceding pages, so generate URL for the 'back' navigation button
        prev_page_url = url_for('browse_bp.browse',
                                sort_by=sort_by,
                                books_per_page=books_per_page,
                                count=count - books_per_page)

    if count + books_per_page < len(book_ids):
        # There are further pages, so generate URL for the 'next' button
        next_page_url = url_for('browse_bp.browse',
                                sort_by=sort_by,
                                books_per_page=books_per_page,
                                count=count + books_per_page)

    return render_template(
        'browse/browse.html',
        books=books,
        page_title='Browse',
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
        search_form=search_form,
        sort_form=sort_form
    )


@browse_blueprint.route('/bookshelf/', methods=['GET', 'POST'])
@login_required
def bookshelf():
    search_form = SearchForm()
    sort_form = SortForm()

    user_name = session['user_name']

    # Read query parameters
    count = request.args.get('count')
    sort_by = request.args.get('sort_by')
    books_per_page = request.args.get('books_per_page')

    if books_per_page != '12' and books_per_page != '18' and books_per_page != '24':
        books_per_page = '12'  # Default books per page

    if count is None:
        # Initialise cursor at beginning
        count = 0
    else:
        count = int(count)

    if request.method == 'GET':
        sort_form.sort_by.data = sort_by
        sort_form.books_per_page.data = books_per_page  # Must be a string

    # Must check if data exists and then validate rather than calling form.validate_on_submit()
    # in order to differentiate between the two forms
    if sort_form.sort_submit.data and sort_form.validate():
        return redirect(url_for('browse_bp.bookshelf',
                                sort_by=sort_form.sort_by.data,
                                books_per_page=sort_form.books_per_page.data))

    # If successful POST, redirect to search result page
    if search_form.search_submit.data and search_form.validate():
        return redirect(url_for('browse_bp.search_result',
                                location='bookshelf',
                                sort_by=sort_by,
                                books_per_page=books_per_page,
                                title=search_form.title.data,
                                author=search_form.author.data,
                                publisher=search_form.publisher.data,
                                year=search_form.year.data))

    books_per_page = int(books_per_page)
    # Get user's favourite books
    book_ids = services.get_favourite_book_ids(user_name, repo.repo_instance)

    # Sort and retrieve books (default = alphabetical)
    matching_books = services.sort_books(book_ids, sort_by, repo.repo_instance)
    books = matching_books[count:count + books_per_page]  # Books to display

    next_page_url = None
    prev_page_url = None

    if count > 0:
        # There are preceding pages, so generate URL for the 'back' navigation button
        prev_page_url = url_for('browse_bp.bookshelf',
                                sort_by=sort_by,
                                books_per_page=books_per_page,
                                count=count - books_per_page)

    if count + books_per_page < len(book_ids):
        # There are further pages, so generate URL for the 'next' button
        next_page_url = url_for('browse_bp.bookshelf',
                                sort_by=sort_by,
                                books_per_page=books_per_page,
                                count=count + books_per_page)

    return render_template(
        'browse/browse.html',
        books=books,
        page_title='My Books',
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
        search_form=search_form,
        sort_form=sort_form
    )


@browse_blueprint.route('/<location>/search_result', methods=['GET', 'POST'])
def search_result(location: str):
    search_form = SearchForm()
    sort_form = SortForm()

    if 'user_name' in session:
        user_name = session['user_name']
    else:
        user_name = None

        # Get page title
    if location == 'bookshelf':
        page_title = 'My Books'
    else:
        page_title = 'Browse'

    # Read query parameters
    title = request.args.get('title')
    author = request.args.get('author')
    publisher = request.args.get('publisher')
    year = request.args.get('year')
    count = request.args.get('count')
    sort_by = request.args.get('sort_by')
    books_per_page = request.args.get('books_per_page')

    if books_per_page != '12' and books_per_page != '18' and books_per_page != '24':
        books_per_page = '12'  # Default books per page

    # If GET, populate form with previous search values
    if request.method == 'GET':
        search_form.title.data = title
        search_form.author.data = author
        search_form.publisher.data = publisher
        search_form.year.data = year
        sort_form.sort_by.data = sort_by
        sort_form.books_per_page.data = books_per_page  # Must be a string

    # Must check if data exists and then validate rather than calling form.validate_on_submit()
    # in order to differentiate between the two forms
    if sort_form.sort_submit.data and sort_form.validate():
        return redirect(url_for('browse_bp.search_result',
                                location=location,
                                sort_by=sort_form.sort_by.data,
                                books_per_page=sort_form.books_per_page.data,
                                title=title,
                                author=author,
                                publisher=publisher,
                                year=year))

    # If successful POST, redirect to search result page
    if search_form.search_submit.data and search_form.validate():
        return redirect(url_for('browse_bp.search_result',
                                location=location,
                                sort_by=sort_by,
                                books_per_page=books_per_page,
                                title=search_form.title.data,
                                author=search_form.author.data,
                                publisher=search_form.publisher.data,
                                year=search_form.year.data))

    books_per_page = int(books_per_page)

    # Initialise lists
    book_ids = []
    title_book_ids = []
    author_book_ids = []
    publisher_book_ids = []
    year_book_ids = []

    # Retrieve book ids for books which contain the queries
    # This can be a partial match, i.e. publisher query "Mar" will return "Marvel"
    # Empty string is not included
    if title is not None:
        title_book_ids = services.get_book_ids_by_title(title, repo.repo_instance)

    if author is not None:
        author_book_ids = services.get_book_ids_by_author(author, repo.repo_instance)

    if publisher is not None:
        publisher_book_ids = services.get_book_ids_by_publisher(publisher, repo.repo_instance)

    if year is not None:
        if year.isnumeric():
            year = int(year)
            year_book_ids = services.get_book_ids_by_year(year, repo.repo_instance)
        else:
            year = None

    favourite_book_ids = services.get_favourite_book_ids(user_name, repo.repo_instance)

    # Only add book_id to list if it matches all queries
    search_list = max(title_book_ids, author_book_ids, publisher_book_ids, year_book_ids, key=len)
    for book_id in search_list:
        if ((book_id in title_book_ids or title is None)
                and (book_id in author_book_ids or author is None)
                and (book_id in publisher_book_ids or publisher is None)
                and (book_id in year_book_ids or year is None)
                and (book_id in favourite_book_ids or location == 'browse')):
            book_ids.append(book_id)

    if count is None:
        # Initialise cursor at beginning
        count = 0
    else:
        count = int(count)

    # Retrieve the batch of books to display - duplicates are removed inside the function
    # books = services.get_books_by_id(book_ids[count: count + books_per_page], repo.repo_instance)
    # Sort and retrieve books (default = alphabetical)
    matching_books = services.sort_books(book_ids, sort_by, repo.repo_instance)
    books = matching_books[count:count + books_per_page]  # Books to display

    next_page_url = None
    prev_page_url = None

    if count > 0:
        # There are preceding pages, so generate URL for the 'back' navigation button
        prev_page_url = url_for('browse_bp.search_result',
                                location=location,
                                sort_by=sort_by,
                                books_per_page=books_per_page,
                                title=title,
                                author=author,
                                publisher=publisher,
                                year=year,
                                count=count - books_per_page)

    if count + books_per_page < len(book_ids):
        # There are further pages, so generate URL for the 'next' button
        next_page_url = url_for('browse_bp.search_result',
                                location=location,
                                sort_by=sort_by,
                                books_per_page=books_per_page,
                                title=title,
                                author=author,
                                publisher=publisher,
                                year=year,
                                count=count + books_per_page)

    return render_template(
        'browse/browse.html',
        books=books,
        page_title=page_title,
        search=True,
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
        search_form=search_form,
        sort_form=sort_form
    )


class SortForm(FlaskForm):
    sort_by = SelectField('sort_by', choices=[('alphabetical', 'Alphabetical'),
                                              ('ascending', 'Date (Ascending)'),
                                              ('descending', 'Date (Descending)'),
                                              ('best_reviewed', 'Best Reviewed'),
                                              ('most_reviewed', 'Most Reviewed')])
    books_per_page = SelectField('books_per_page', choices=[12, 18, 24])
    sort_submit = SubmitField('search')


# Filter will strip input if not empty, otherwise will set it to None
class SearchForm(FlaskForm):
    title = StringField('Title', filters=[lambda x: None if x is None or x.strip() == "" else x.strip()])
    author = StringField('Author', filters=[lambda x: None if x is None or x.strip() == "" else x.strip()])
    publisher = StringField('Publisher', filters=[lambda x: None if x is None or x.strip() == "" else x.strip()])
    year = IntegerField('Year', validators=[Optional()])
    search_submit = SubmitField('Search')
