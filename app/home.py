from flask import Blueprint, render_template
from auth import login_required

home = Blueprint('home', __name__)

@home.route('/user', methods=['GET'])
@login_required
def user_main():
    return render_template('user_main.html')

@home.route('/organizer', methods=['GET'])
@login_required
def organizer_main():
    return render_template('organizer_main.html')