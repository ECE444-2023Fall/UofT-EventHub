from flask import Blueprint, render_template, flash, url_for, redirect
from flask_login import login_required, current_user
import logging

from app.main import db
from app.auth import user_required
from app.forms import UserDetailsForm, UserRegisterForm
from app.database import UserDetails

account = Blueprint("account", __name__)

@login_required
@user_required
@account.route("/account/show", methods=["GET", "POST"])
def show_user_details():
    # Get the form
    form = UserDetailsForm()

    # Fetch username
    current_username = current_user.get_id()

    # Get user details from database
    user_details = UserDetails.query.filter_by(username=current_username).first()

    # Generate a form with prefilled information
    if request.method == 'GET':
        form.firstname = user_details.firstname
        form.lastname = user_details.lastname
        form.year = user_details.year
        form.course_type = user_details.course_type
        form.department = user_details.department
        form.campus = user_details.campus
        form.email = user_details.email

    # Upon submission update the database
    if form.validate_on_submit():
        logging.info("Updating the user details")

        # Update user's current details
        current_user_details = UserDetails.query.filter_by(username=current_username).first()
        current_user_details.firstname=form.firstname.data
        current_user_details.lastname=form.lastname.data
        current_user_details.year=form.year.data
        current_user_details.course_type=form.course_type.data
        current_user_details.department=form.department.data
        current_user_details.campus=form.campus.data
        current_user_details.email=form.email.data

        # Update the flash message
        flash("Your details have been successfully updated!", "info")

        # Save the updates
        db.session.commit()

        return render_template("my_account.html", form=form)
    
    return render_template("my_account.html", form=form)


@login_required
@user_required
@account.route("/account/add", methods=["GET", "POST"])
def add_user_details():
    # Get the form
    form = UserRegisterForm()

    # Fetch username
    current_username = current_user.get_id()

    if form.validate_on_submit():
        # Register the new user details
        new_user_details = UserDetails(
            username=current_username,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            year=form.year.data,
            course_type=form.course_type.data,
            department=form.department.data,
            campus=form.campus.data,
            email=form.email.data,
        )

        db.session.add(new_user_details)
        db.session.commit()

        flash("Your details have been saved. You can always modify them from the 'My Account' tab", "info")
        return redirect(url_for("user.main"))

    return render_template("user_register.html", form=form)

