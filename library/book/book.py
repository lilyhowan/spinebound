from better_profanity import profanity
from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, RadioField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError, Optional, InputRequired

import library.adapters.repository as repo
import library.book.services as services

from library.authentication.authentication import login_required

# Configure blueprint
book_blueprint = Blueprint(
    'book_bp', __name__)


@book_blueprint.route('/book', methods=['GET', 'POST'])
def book():
    form = FavouriteForm()
    is_favourite = False
    reviews = []
    book_id = request.args.get('book_id')
    next_page_url = None
    prev_page_url = None

    # book_id is a string in the request, but is stored as an int in the domain model
    if book_id is None or len(book_id.strip()) == 0 or not book_id.isnumeric():
        book_id = None
    else:
        book_id = int(request.args.get('book_id'))

    if 'user_name' in session.keys():
        user_name = session['user_name']
    else:
        user_name = None

    if form.validate_on_submit():
        # On valid POST, add book to user's favourites
        if user_name is not None:
            # If book is in favourites it will be removed, otherwise it will be added
            services.add_or_remove_book_from_favourites(book_id, user_name, repo.repo_instance)
        else:
            return redirect(url_for('authentication_bp.login'))

    try:
        # Initialise variables
        reviews_per_page = 10
        is_favourite = services.check_if_book_in_favourites(book_id, user_name, repo.repo_instance)  # For btn display
        count = request.args.get('count')

        if count is None:
            # Initialise cursor at beginning
            count = 0
        else:
            count = int(count)

        # Get book and reviews to display
        book = services.get_book_by_id(book_id, repo.repo_instance)
        reviews = book['reviews'][count:count + reviews_per_page]
        stats = services.calculate_rating_stats(int(book_id), repo.repo_instance)

        # Creating forward/back buttons for reviews
        if count > 0:
            # There are preceding pages, so generate URL for the 'back' navigation button
            prev_page_url = url_for('book_bp.book',
                                    book_id=book_id,
                                    count=count - reviews_per_page)

        if count + reviews_per_page < len(book['reviews']):
            # There are further pages, so generate URL for the 'next' button
            next_page_url = url_for('book_bp.book',
                                    book_id=book_id,
                                    count=count + reviews_per_page)

    except services.NonExistentBookException:
        # If book does not exist, the HTML page will display an error message
        book = None
        stats = None

    return render_template(
        'book/book.html',
        book=book,
        reviews=reviews,
        stats=stats,
        is_favourite=is_favourite,
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
        form=form
    )


@book_blueprint.route('/review', methods=['GET', 'POST'])
@login_required
def review():
    form = ReviewForm()
    user_name = session['user_name']
    # book_id is a string in the request, but is stored as an int in the domain model
    if request.args.get('book_id') is None or len(request.args.get('book_id').strip()) == 0:
        book_id = None
    else:
        book_id = int(request.args.get('book_id'))

    if form.validate_on_submit():
        # Successful POST, i.e. the review has passed data validation
        # Use the service layer to store the new review
        services.add_review(book_id, form.review_text.data, int(form.rating.data), user_name, repo.repo_instance)
        return redirect(url_for('book_bp.book', book_id=book_id))


    try:
        book = services.get_book_by_id(book_id, repo.repo_instance)
    except services.NonExistentBookException:
        # If book does not exist, the HTML page will display an error message
        book = None

    return render_template(
        'book/review.html',
        book=book,
        form=form
    )


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class FavouriteForm(FlaskForm):
    favourite = SubmitField('favorite')


class ReviewForm(FlaskForm):
    review_text = TextAreaField('Review', validators=[DataRequired(),
                                                      Length(min=4, message='Your review must be at least 4 characters.'),
                                                      ProfanityFree(message='Your review must not contain profanity.')])
    rating = RadioField(choices=[5, 4, 3, 2, 1],
                        validators=[InputRequired(message='A rating is required.')])
    submit = SubmitField()
