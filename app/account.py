from flask import Blueprint, request, render_template, flash, url_for, redirect
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

    # Generate a form with prefilled information
    user_details = UserDetails.query.filter_by(username=current_username).first()

    if request.method == 'GET':
        try:
            form.firstname.data = user_details.firstname
            form.lastname.data = user_details.lastname
            form.year.data = user_details.year
            form.course_type.data = user_details.course_type
            form.department.data = user_details.department
            form.campus.data = user_details.campus
            form.email.data = user_details.email
            logging.info("Rendering details form for %s", form.firstname.data)
        except:
            logging.warning("The user provided has not provided personal details yet")

        return render_template("my_account.html", form=form)

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
        flash("Your details have been successfully updated!", category="primary")

        # Save the updates
        db.session.commit()

        return render_template("my_account.html", form=form)
    
    logging.warning("func: show_user_details; We should never reach here as both GET and POST request are handled above")
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

        flash("Your details have been saved. You can always modify them from the 'My Account' section", category="primary")
        return redirect(url_for("user.main"))

    return render_template("user_register.html", form=form)

