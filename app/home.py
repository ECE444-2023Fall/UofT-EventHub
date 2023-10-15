from flask import Blueprint, render_template

home = Blueprint('home', __name__)

@home.route('/user', methods=['GET'])
def user_main():
    return render_template('user_main.html')

@home.route('/organizer', methods=['GET'])
def organizer_main():
    return render_template('organizer_main.html')