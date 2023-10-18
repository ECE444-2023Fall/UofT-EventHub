from flask import Blueprint, render_template, request, flash, redirect, url_for, Flask, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, LoginManager
from forms import LoginForm, RegForm, EventCreateForm

from main import db
from database import Credentials, EventDetails

organizer = Blueprint('organizer', __name__)

@organizer.route('/organizer', methods=['GET'])
@login_required
def main():
    my_events_data = EventDetails.query.all()
    # result = session.query(Credentials, EventDetails).join(User, User.id == Order.user_id).all()
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

        return redirect(url_for('main'))

    return render_template('create_event.html', form=form)