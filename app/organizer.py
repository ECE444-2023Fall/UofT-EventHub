from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from forms import EventCreateForm

from main import db
from database import EventDetails, OrganizerEventDetails

organizer = Blueprint('organizer', __name__)

@organizer.route('/organizer', methods=['GET'])
@login_required
def main():
    my_events_data = db.session.query(EventDetails).join(OrganizerEventDetails).filter(OrganizerEventDetails.organizer_username == current_user.username)
    return render_template('organizer_main.html', my_events_data=my_events_data)

@organizer.route('/organizer/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventCreateForm()

    if form.validate_on_submit():
        # Currently I am not passing the banner information. 
        # This will be possible after the creation of the EventGraphicsBucket database 
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

        new_organizer_event_relation = OrganizerEventDetails(event_id=new_event.id, organizer_username=current_user.username)
        db.session.add(new_organizer_event_relation)
        db.session.commit()

        return redirect(url_for('organizer.main'))

    organizer = current_user
    print(organizer)

    return render_template('create_event.html', form=form)