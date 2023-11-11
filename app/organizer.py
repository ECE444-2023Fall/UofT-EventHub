from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import logging

from app.main import db # db is for database
from app.database import EventDetails, Credentials, UserDetails, EventRegistration, EventRating
from app.auth import organizer_required

organizer = Blueprint("organizer", __name__)


@organizer.route("/organizer", methods=["GET"])
@login_required
@organizer_required
def main():
    my_events_data = get_my_events_from_database()
    my_avg_rating = get_avg_rating_from_database()

    return render_template("organizer_main.html", my_events_data=my_events_data, my_avg_rating=my_avg_rating)

def get_my_events_from_database():
    events_data = (
        db.session.query(EventDetails)
        .join(Credentials)
        .filter(EventDetails.organizer == current_user.username)
        .all()
    )

    # Make a dict for event details
    dict_of_events_details = {}
    for row in events_data:
        event_detail = {}

        # TODO: Ideally we should only be passing information that is required by the user_main.html
        for column in row.__table__.columns:
            event_detail[column.name] = str(getattr(row, column.name))

        dict_of_events_details[row.id] = event_detail

    return dict_of_events_details

def get_avg_rating_from_database():
    user_rating = (
        db.session.query(func.avg(EventRating.rating).label('avg_rating'))
        .join(EventDetails)
        .filter(EventDetails.organizer == current_user.username)
        .first()
    )

    if not hasattr(user_rating, 'avg_rating'):
        logging.warn("Query does not have an attribute names avg_rating")
        return -1
    avg_rating = getattr(user_rating, 'avg_rating')
    if avg_rating is None:
        return -1
    return avg_rating

def get_user_analytics(event_id):
    # Define a function that generates an analytic chart
    # This function takes in an analytic column as an input (ie. Department), and
    # returns a pie chart (with a title and legend)
    # NOTE: If the function does not find any analytics data then it returns None
    def get_analytic_chart_given_column(event_id, user_detail_column, title):
        analytics_data = (
            db.session.query(user_detail_column, func.count(UserDetails.username).label('order_count'))
            .join(EventRegistration, UserDetails.username == EventRegistration.attendee_username)
            .filter(EventRegistration.event_id == event_id)
            .group_by(user_detail_column)
            .all()
        )

        # No analytics data found
        if len(analytics_data) == 0:
            logging.info(f"Column ({title}) has no analytics data")
            return None

        logging.info(f"Analytics for {title}: {analytics_data}")

        # Create a matplotlib plot
        plt.figure(figsize=(8, 8))
        keys = [elem[0] for elem in analytics_data]
        values = [elem[1] for elem in analytics_data]
        colors = plt.cm.Paired(range(len(keys)))
        wedges, _ = plt.pie(values, autopct=None, startangle=90, colors=colors)
        plt.title(f"{title} Distribution")

        plt.legend(wedges, keys, title=f'{title} Categories', loc='upper center', bbox_to_anchor=(1, 1))
        plt.axis('equal')

        # Save the chart to a BytesIO object
        chart_image = BytesIO()
        plt.savefig(chart_image, format='png', bbox_inches='tight')
        chart_image.seek(0)

        # Encode the image to base64 for embedding in HTML
        chart_image_base64 = base64.b64encode(chart_image.read()).decode('utf-8')
        return chart_image_base64
    
    analytics_charts = []

    # Define the different interested analytics
    titles = ["Years", "Campus", "Department", "Course Type"]
    columns = [UserDetails.year, UserDetails.campus, UserDetails.department, UserDetails.course_type]
    for title, column in zip(titles, columns):
        chart = get_analytic_chart_given_column(event_id, column, title)
        if chart is None:
            continue
        analytics_charts.append(chart)
    
    return analytics_charts