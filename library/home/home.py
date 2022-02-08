from flask import Blueprint, render_template

import library.adapters.repository as repo

# Configure blueprint
home_blueprint = Blueprint(
    'home_bp', __name__)


@home_blueprint.route('/', methods=['GET'])
def home():
    return render_template(
        'home/home.html'

    )
