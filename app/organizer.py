from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.main import db # db is for database
from app.database import EventDetails, EventBanner, Credentials
from app.auth import organizer_required

organizer = Blueprint("organizer", __name__)


@organizer.route("/organizer", methods=["GET"])
@login_required
@organizer_required
def main():
    my_events_data = (
        db.session.query(EventDetails)
        .join(Credentials)
        .filter(EventDetails.organizer == current_user.username)
    )
    return render_template("organizer_main.html", my_events_data=my_events_data)


@organizer.route("/organizer/create_event", methods=["GET", "POST"])
@login_required
@organizer_required
def create_event():
    form = EventCreateForm()

    if form.validate_on_submit():
        # Add the event details
        new_event = EventDetails(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data.lower(),
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
        db.session.add(new_event)
        db.session.commit()

        # Add the event details to the index for elastic search
        add_event_to_index(new_event)

        # Add the banner information for the newly created event
        banner_file = form.banner_image.data
        filename = "event_banner_" + str(new_event.id) + ".png"

        # Save the banner in static/event-assets
        banner_file.save(
            os.path.join(current_app.root_path, "static", "event-assets", filename)
        )

        # Store the path to the banner EventBanner
        event_graphic = EventBanner(event_id=new_event.id, image=filename)

        db.session.add(event_graphic)
        db.session.commit()

        new_organizer_event_relation = OrganizerEventDetails(
            event_id=new_event.id, organizer_username=current_user.username
        )
        db.session.add(new_organizer_event_relation)
        db.session.commit()

        return redirect(url_for("organizer.main"))

    organizer = current_user

    return render_template("create_event.html", form=form)

#Adds it to the "index" which we use for searching events
def add_event_to_index(new_event):
    event_detail = {
        "id": new_event.id,
        "name": new_event.name,
        "description": new_event.description,
        "category": new_event.category,
        "venue": new_event.venue,
        "additional_info": new_event.additional_info,
    }

    logging.info("The event dict for indexing:", event_detail)
    es.index(index="events", document=event_detail)
    es.indices.refresh(index="events")
    logging.info(es.cat.count(index="events", format="json"))
