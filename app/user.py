from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.auth import login_required
from app.database import EventDetails, EventRating
from app.main import db

user = Blueprint('user', __name__)

@user.route('/user', methods=['GET'])
@login_required
def main():
    events_data = EventDetails.query.all()
    # only for testing to see if user inputs for ratings are actually being stored in the database:
    events_ratings = EventRating.query.all()
    return render_template('user_main.html', events_data=events_data, events_ratings = events_ratings)

@user.route('/submit_rating', methods=['POST'])
def submit_rating():
    # Get the user's username (assuming they are logged in)
    #TODO: add user info to rating if need be
    # user_username = 

    event_id = request.form.get('event_id')
    rating = request.form.get('rating')

    if event_id and rating: #and user_username 
        # Check if the user has already rated this event, and update the rating if they have
        # existing_rating = EventRating.query.filter_by(event_id=event_id).first()
        # if existing_rating:
        #     existing_rating.rating = rating
        # else:
        # Create a new rating record
        event_rating = EventRating(event_id=event_id, rating=rating)
        db.session.add(event_rating)
        
        db.session.commit()

        flash('Rating submitted successfully', 'success')
    else:
        flash('Failed to submit rating. Please try again.', 'error')
    
    return redirect(url_for('user.main'))
