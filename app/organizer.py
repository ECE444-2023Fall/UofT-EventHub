from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from flask import current_app
import logging
import os

from app.main import db, es # db is for database and es for elastic search
from app.database import EventDetails, OrganizerEventDetails, EventBanner
from app.auth import organizer_required

organizer = Blueprint("organizer", __name__)


@organizer.route("/organizer", methods=["GET"])
@login_required
@organizer_required
def main():
    my_events_data = (
        db.session.query(EventDetails)
        .join(OrganizerEventDetails)
        .filter(OrganizerEventDetails.organizer_username == current_user.username)
    )
    return render_template("organizer_main.html", my_events_data=my_events_data)


@organizer.route("/organizer/create_event", methods=["GET", "POST"])
@login_required
@organizer_required
def create_event():
    form = EventCreateForm()

    if form.validate_on_submit():
        # Add the event details
        new_event = EventDetails(name=form.name.data, 
                                 description=form.description.data,  
                                 type=form.type.data,  
                                 venue=form.venue.data,  
                                 start_date=form.start_date.data,  
                                 end_date=form.end_date.data,  
                                 start_time=form.start_time.data,  
                                 end_time=form.end_time.data,  
                                 link=form.link.data,  
                                 additional_info=form.additional_info.data)
        db.session.add(new_event)
        db.session.commit()

        # Parse through tags and link associated tags
        tags = form.tags.data.split(',')  # Splitting tags by comma
        for tag_name in tags:
            tag_name = tag_name.strip()  # Remove leading & trailing whitespace
            if tag_name:
                # Check if the tag already exists, otherwise create it
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                    db.session.commit()
                new_event.tags.append(tag)  # Associating tag with the event

        # Add the event details to the index for elastic search
        add_event_to_index(new_event)

        # Add the banner information for the newly created event
        banner_file = form.banner_image.data
        filename = "event_banner_" + str(new_event.id) + ".png"

        # Save the banner in assets/event-assets
        banner_file.save(
            os.path.join(current_app.root_path, "assets", "event-assets", filename)
        )

        # Store the path to the banner EventBanner
        event_graphic = EventBanner(event_id=new_event.id, image=filename)

        db.session.add(event_graphic)
        db.session.commit()

        new_organizer_event_relation = OrganizerEventDetails(event_id=new_event.id, organizer_username=current_user.username)
        db.session.add(new_organizer_event_relation)
        db.session.commit()

        return redirect(url_for("organizer.main"))

    organizer = current_user
    print(organizer)

    return render_template("create_event.html", form=form)


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
