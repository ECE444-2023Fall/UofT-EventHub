from flask import (
    Blueprint,
    Response,
    render_template,
    send_from_directory,
    flash,
    current_app,
    request,
    redirect,
    url_for,
    abort,
)
from flask_login import login_required, current_user
from datetime import datetime
import logging
import os.path
import os

from app.main import db # db is for database
from app.globals import Role, USE_SIMPLE_SEARCH
from app.auth import organizer_required, user_required
from app.database import Credentials, EventRegistration, EventDetails, EventRating
from app.forms import EventCreateForm
from app.analytics import get_user_analytics, get_avg_rating

if not USE_SIMPLE_SEARCH:
    from app.main import es # es is for elasticsearch

events = Blueprint("events", __name__)


@events.route("/events/<int:id>", methods=["GET"])
@login_required
def show_event(id):
    logging.info("Loading webpage for event ID: %d", id)

    # Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        logging.error(
            "Integrity Error: The event ID passed to show_event has no valid entry in the database"
        )
        abort(404, description = {
            "type": "event_not_found",
            "caller": "show_event",
            "message": "Can not show the event since the event does not exist"
        })

    # Check if the user registered for the event
    is_registered = EventRegistration.query.filter_by(attendee_username=current_user.get_id(), event_id=id).first()

    #Check for past event. Users will only be able to rate if this is met. 
    is_past_event = past_event(id)
    logging.info("is it a past event: %s",is_past_event)

    #get existing user rating
    prev_rating = previous_rating(attendee_username=current_user.get_id(), event_id=id)
    logging.info("Prev Rating: %s", prev_rating)

    event_dict = event.__dict__
    
    # Fix: Need to pass event ID as a string
    str_id = str(event_dict["id"])
    event_dict["id"] = str_id

    # Get the day of the event
    logging.info("The start date of the event is: %s - %s - %s", event_dict["start_date"].weekday(), event_dict["start_date"].month, event_dict["start_date"].day)

    # Get image for event
    logging.info("Retreived event image: %s", event.image)

    if is_registered is not None:
        if not is_past_event:
            flash("You are registered for the event!", category="primary")
            return render_template("event.html", 
            event=event_dict, 
            is_registered=True, 
            is_past_event = is_past_event, 
            prev_rating=prev_rating, 
            event_dayofweek=event_dict["start_date"].weekday(), 
            event_day=event_dict["start_date"].day,
            event_month=event_dict["start_date"].strftime("%B"),)
        else:
            flash("This is a past event!", category="primary")
            return render_template("event.html", 
            event=event_dict, 
            is_registered=True, 
            is_past_event = is_past_event, 
            prev_rating=prev_rating,
            event_dayofweek=event_dict["start_date"].weekday(), 
            event_day=event_dict["start_date"].day,
            event_month=event_dict["start_date"].strftime("%B"),)
    else:
        if is_past_event:
            flash("This is a past event!", category="primary")
        return render_template("event.html", 
        event=event_dict, 
        is_registered=False, 
        is_past_event = is_past_event, 
        prev_rating=prev_rating,
        event_dayofweek=event_dict["start_date"].weekday(), 
        event_day=event_dict["start_date"].day,
        event_month=event_dict["start_date"].strftime("%B"),)


@events.route("/events/admin/<int:id>", methods=["GET"])
@login_required
@organizer_required
def show_event_admin(id):
    logging.info("Loading admin webpage for event ID: %d", id)

    # Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        logging.error(
            "Integrity Error: The event ID passed to show_event_admin has no valid entry in the database"
        )
        abort(404, description = {
            "type": "event_not_found",
            "caller": "show_event_admin",
            "message": "Can not show the event since the event does not exist"
        })

    # Get some analytics data for this event
    registered_users = EventRegistration.query.filter_by(event_id=id).all()
    num_of_registrations = len(registered_users)

    user_analytic_charts = get_user_analytics(event_id=id)

    avg_rating = get_avg_rating(event_id=id)

    # Fix: Need to pass event ID as a string
    event_dict = event.__dict__
    str_id = str(event_dict["id"])
    event_dict["id"] = str_id

    # Get image for event
    logging.info("Retreived event image: %s", event.image)

    return render_template("event_admin.html",
                           event=event_dict,
                           num_of_registrations=num_of_registrations, 
                           user_analytic_charts=user_analytic_charts,
                           avg_rating=avg_rating)

@events.route("/events/create_event", methods=["GET", "POST"])
@login_required
@organizer_required
def create_event():
    form = EventCreateForm()

    if form.validate_on_submit():
        # Add the event details
        new_event = EventDetails(
            name=form.name.data,
            short_description=form.short_description.data,
            long_description=form.long_description.data,
            category=form.category.data.lower(),
            organizer=current_user.username,
            is_online=form.is_online.data,
            venue=form.venue.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            max_capacity=form.max_capacity.data,
            current_capacity=0,
            ticket_price=form.ticket_price.data,
            redirect_link=form.redirect_link.data,
            additional_info=form.additional_info.data,
        )

        banner_file = form.banner_image.data

        # If an image is not supplied save a place holder
        if "FileStorage: ''" in str(banner_file):
            logging.info("Adding a default image")
            new_event.image = "placeholder.png"
        else:
            logging.info("The image supplied is: %s", banner_file)
            
            # Add the banner information for the newly created event
            # Get number of events
            num_of_events = len(EventDetails.query.all())
            # The new event id will always be one more than the current num of events
            new_event_id = num_of_events + 1
            # Give the file name according to new event id
            filename = "event_banner_" + str(new_event_id) + ".png"
            new_event.image = filename

            # Save the banner in static/event-assets
            banner_file.save(
                os.path.join(current_app.root_path, "static", "event-assets", filename)
            )

        db.session.add(new_event)
        db.session.commit()

        if not USE_SIMPLE_SEARCH:
            add_event_to_index(new_event)

        return redirect(url_for("events.show_event_admin", id=new_event.id))

    return render_template("create_event.html", form=form)


@events.route("/events/edit_event/<int:id>", methods=["GET", "POST"])
@login_required
@organizer_required
def edit_event(id):
    logging.info("Loading edit event webpage for event ID: %d", id)

    # Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        logging.error(
            "Integrity Error: The event ID passed to show_event_admin has no valid entry in the database"
        )
        abort(404, description = {
            "type": "event_not_found",
            "caller": "edit_event",
            "message": "Can not edit the event since the event does not exist"
        })

    # Recreate the Event Form with the default values set
    event_create_form_default = {}
    for field_name, default_value in event.__dict__.items():
        if not hasattr(EventCreateForm, field_name):
            logging.info(f"Form doesn't have attribute: {field_name}")
            continue
        # NOTE: Since we are decapitilizing the category data on form submition,
        # we must perform the opposite operation here
        if field_name == "category":
            default_value = default_value.capitalize()
        event_create_form_default[field_name] = default_value
    logging.info(f"Default Values: {event_create_form_default}")

    form = EventCreateForm(**event_create_form_default)

    if form.validate_on_submit():
        logging.info(f"Edited Event Entries: {form.name.data}, {form.category.data}")
        # Add the event details
        event.name = form.name.data
        event.short_description = form.short_description.data
        event.long_description = form.long_description.data
        event.category = form.category.data.lower()
        event.is_online = form.is_online.data
        event.venue = form.venue.data
        event.start_date = form.start_date.data
        event.end_date = form.end_date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        # TODO: Add a check to prevent the max capacity from being set to below the current capacity
        event.max_capacity = form.max_capacity.data
        event.ticket_price = form.ticket_price.data
        event.redirect_link = form.redirect_link.data
        event.additional_info = form.additional_info.data

        # TODO: Update the event details to the index for elastic search

        # Add the banner details for the newly edited event
        banner_file = form.banner_image.data
        if "FileStorage: ''" not in str(banner_file):
            logging.info("The image supplied is: %s", banner_file)
            
            # Add the banner information for the newly created event
            filename = "event_banner_" + str(id) + ".png"
            event.image = filename

            # Save the banner in static/event-assets
            banner_file.save(
                os.path.join(current_app.root_path, "static", "event-assets", filename)
            )
            
        db.session.commit()

        return redirect(url_for("events.show_event_admin", id=event.id))

    return render_template("create_event.html", form=form)


@events.route("/events/delete_event/<int:id>", methods=["POST"])
@login_required
@organizer_required
def delete_event(id):
    logging.info("Loading edit event webpage for event ID: %d", id)

    # Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        logging.error(
            "Integrity Error: The event ID passed to show_event_admin has no valid entry in the database"
        )
        abort(404, description = {
            "type": "event_not_found",
            "caller": "delete_event",
            "message": "Can not delete the event since the event does not exist"
        })

    if event.organizer != current_user.username:
        logging.info(f"Current Organizer ({current_user.username} doesn't match the event creator {event.organizer})")
        abort(401, description = {
            "type": "unauthorized_organizer",
            "caller": "delete_event",
            "message": "You are not authorized to delete this event"
        })

    db.session.delete(event)
    db.session.commit()

    return redirect(url_for("organizer.main"))


@events.route("/events/send_file/<filename>")
@events.route("/events/register/send_file/<filename>")
@login_required
def send_file(filename):
    """
    This function is used to fetch event banner images for event.html pages"
    """

    return send_from_directory(current_app.config["GRAPHIC_DIRECTORY"], filename)


@events.route("/events/register/<int:event_id>", methods=["GET", "POST"])
@login_required
def register_for_event(event_id):
    """
    Description: Responsible for registering the user for an event.
                 Upon succesfull registration it re-renders the template

    Returns:
        0: On successful registration
        1: If the event ID is invalid
        2: If the username is invalid
        3: If username is valid but the role is organizer
        4: If the user is already registered for the event
        401 error: If the event is a past event
    """
    
    # Check for valid event ID
    if event_id is None:
        logging.info("Cannot register user with an event ID: None")
        return ("1")

    logging.info("EVENT ID: %s", event_id)
    logging.info("USERNAME: %s", current_user.get_id())

    # Check for valid username
    user = Credentials.query.filter_by(username=current_user.get_id()).first()
    is_past_event = past_event(event_id)
    if not user:
        logging.warning("Cannot register user with an invalid username")
        return ("2")

    # We should also check if a username corresponds to a user and not an organizer
    if user.role != Role.USER.value:
        logging.warning("Cannot register an organizer")
        return ("3")
    
    #Check for past event is also needed and has been implemented on
    #the event.html page where the register button is disabled once an event is over.
    if is_past_event:
        logging.warning("Cannot register to a past event!")
        abort(401, description = {
                "type": "user_unauthorized",
                "caller": "events.register_for_event",
                "message": "Event is a past event"
            })

    # TODO: Check if event has enough seats left

    # Check if the user is already registered
    is_registered = EventRegistration.query.filter_by(attendee_username=current_user.get_id(), event_id=event_id).first()
    if is_registered:
        logging.info("Cancelling user's registration")

        # Delete the registration
        EventRegistration.query.filter_by(attendee_username=current_user.get_id(), event_id=event_id).delete()
        db.session.commit()

        flash("Cancelled registration for the event!", category="primary")
        event = EventDetails.query.filter_by(id=event_id).first()

        return redirect(url_for('events.show_event', id=event_id))

    # Register the user
    new_registration = EventRegistration(
        attendee_username=current_user.get_id(),
        event_id=event_id,
    )

    db.session.add(new_registration)
    db.session.commit()

    event = EventDetails.query.filter_by(id=event_id).first()
    return redirect(url_for('events.show_event', id=event_id))

def add_event_to_index(new_event):
    event_detail = {
        "id": new_event.id,
        "name": new_event.name,
        "short_description": new_event.short_description,
        "category": new_event.category,
        "venue": new_event.venue,
        "additional_info": new_event.additional_info,
    }

    logging.info("The event dict for indexing:", event_detail)
    es.index(index="events", document=event_detail)
    es.indices.refresh(index="events")
    logging.info(es.cat.count(index="events", format="json"))


def past_event(event_id):
    #Here we check to see if the event is a past event or not.
    #Only if it is a past event will users be able to add a rating for it
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    event_detail = EventDetails.query.filter_by(id=event_id).first()
    logging.info("Current Date: ", current_date, " Current time: ", current_time)
    if event_detail.start_date < current_date:
        return True
    elif (event_detail.start_date == current_date and event_detail.start_time < current_time):
        return True
    else:
        return False


def previous_rating(attendee_username, event_id):
    #This function returns 0 if no previous rating
    #Else, it returns the value of the previous rating (1-5)

    prev_rating = EventRating.query.filter_by(attendee_username=attendee_username, event_id=event_id).first()
    if prev_rating is None:
        return 0
    else:
        logging.info("Existing Rating: ", prev_rating)
        return prev_rating.rating


@events.route("/events/submit_rating/<int:event_id>", methods=["GET", "POST"])
def submit_rating(event_id):
    # Check if the user registered for the event
    is_registered = EventRegistration.query.filter_by(attendee_username=current_user.get_id(), event_id=event_id).first()
    is_past_event = past_event(event_id)
    if (is_past_event == False or is_registered is None):
        abort(401, description = {
                "type": "user_unauthorized",
                "caller": "events.submit_rating",
                "message": "Event is either not a past event or user is not registered to the event"
            })
    # Get the user's username (assuming they are logged in)
    attendee_username = current_user.get_id()
    event_id = request.form.get('event_id')
    rating = request.form.get('rating')

    if event_id and rating and attendee_username: 
        # Check if the user has already rated this event, and update the rating if they have
        existing_rating = EventRating.query.filter_by(attendee_username=attendee_username, event_id=event_id).first()
        if existing_rating is not None:
            existing_rating.rating = rating
            db.session.commit()
            logging.info("Here is the updated rating: ", existing_rating)
            flash('Rating Updated successfully!', 'warning')
        else:
            # Create a new rating record
            new_rating = EventRating(attendee_username=attendee_username ,event_id=event_id, rating=rating)
            logging.info("Here is the new submitted rating: ", new_rating)
            db.session.add(new_rating)
            
            db.session.commit()

            flash('Rating submitted successfully!', 'warning')
    else:
        flash('Failed to submit rating. Please try again.', 'danger')
        
    return redirect(url_for('events.show_event', id=event_id))


@events.route("/events/<int:id>/calendar_invite", methods=["GET"])
@login_required
@user_required
def create_ical_event(id):
    # Get the event details from the database
    event = EventDetails.query.filter_by(id=id).first()
    if event:
        # Check if the user has registered for the event
        is_registered = EventRegistration.query.filter_by(attendee_username=current_user.get_id(), event_id=id).first()
        if is_registered is None:
            logging.error("The user has not registered to be able to view the calendar invite")
            abort(404, description = {
                "type": "user_not_registered",
                "caller": "create_ical_event",
                "message": "Can not add the event to calendar since the user is not registered"
            })

        ical_data = event.to_ical_event()

        # Modifying the filename to include the event name
        filename = f"{event.name.replace(' ', '_')}_event.ics"

        response = Response(ical_data, content_type='text/calendar')
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'

        logging.info("Returning the event invite to the registered user")
        return response
    else:
        logging.error("The event ID passed to has no valid entry in the database")
        abort(404, description = {
            "type": "event_not_found",
            "caller": "create_ical_event",
            "message": "Can not add the event to calendar since the event does not exist"
        })
