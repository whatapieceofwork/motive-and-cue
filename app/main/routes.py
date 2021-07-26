from app.main.forms import EditProfileAdminForm, EditProfileForm
from app.main.crud import get_user, get_user_by_username
from app.main.errors import page_not_found
from bs4 import BeautifulSoup
from datetime import datetime
from flask import abort, flash, redirect, render_template, session, url_for, render_template_string
from . import main
from ..decorators import admin_required, permission_required
from .. import db
from ..models import User, Role
from flask_login import current_user, login_required

@main.route("/")
@main.route("/index/")
def index():
    from motiveandcue import send_email
    # send_email("motiveandcue@gmail.com", "Test", "testemail")

    return render_template("index.html",
                            current_time=datetime.utcnow())
 

@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def profile_edit():
    """Display form to edit user profile page."""

    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about = form.about.data
        db.session.add(current_user._get_current_object())
        db.session.commit()

        flash("Your profile has been successfully updated.", "success")
        return redirect(url_for(".profile", username=current_user.username))

    form.name.data = current_user.name
    form.about.data = current_user.about

    title="Edit Profile"
    return render_template("profile_edit.html", form=form, title=title)


@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def profile_edit_admin(id):
    """Display form for administrator to edit user profile page."""

    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.name = form.name.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.about = form.about.data
        db.session.add(user)
        db.session.commit()

        flash("The profile has been successfully updated.", "success")
        return redirect(url_for(".profile", username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.name.data = user.name
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.about.data = user.about

    title = "Edit User Profile"
    return render_template("profile_edit.html", form=form, user=user)


@main.route("/user/<username>")
def profile(username):
    """Given a username in the URL, display user profile page or return 404."""

    user = get_user_by_username(username)
    if not user:
        abort(404)

    title = user.username
    return render_template("profile.html", user=user, title=title)


@main.route("/about")
def about():
    """Display the About page."""

    title = "About"
    return render_template("about.html")


#  REMOVE BEFORE LAUNCH!!
@main.route("/reboot")
def test_reboot():
    """A wonderfully dangerous route to dump and rebuild the database for testing."""

    from app.main.seed import make_admin

    db.session.commit() # closes existing database connections to prevent issues when dropping tables
    db.drop_all()
    db.create_all()
    make_admin()
    
    flash("Good job, you successfully broke everything!", "success")

    return redirect("/index/")

#  REMOVE BEFORE LAUNCH!!
@main.route("/refresh")
def test_refresh():
    """A much less dangerous route to update tables."""

    db.create_all()
    flash("Tables re-created.", "success")

    return redirect("/index/")