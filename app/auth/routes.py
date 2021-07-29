from app import db
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from . import auth
from .forms import LoginForm, RegistrationForm, RequestPasswordResetForm, ResetPasswordForm
from ..models import User
from werkzeug.security import generate_password_hash


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Display login form; log user in or return error."""

    form = LoginForm()
    title = "Log In"

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(f"**********IN LOGIN. USER: {user}")
        print(f"**********VERIFIED PASSWORD? {user.verify_password(form.password.data)}")

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get("next")

            print(f"**********CURRENT USER: {current_user}")

            if next is None or not next.startswith("/"):
               next = url_for("main.index")

            return redirect(next)

        flash("Invalid username or password. Please try again or register an account.", "warning")

    return render_template("auth/login.html", form=form, title=title)


@auth.route("/logout")
@login_required
def logout():
    """Log out user, redirect to index."""

    logout_user()
    flash("You have been successfully logged out. Thanks for visiting!", "primary")

    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register new user."""

    from motiveandcue import send_email

    title = "Register"
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password_hash=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()

        token = user.generate_token()
        send_email(user.email, "Confirm Your Account", "auth/email/confirm", user=user, token=token)

        flash("A confirmation link has been emailed to you. Please confirm your account.", "primary")
        return redirect(url_for("main.index"))

    return render_template("auth/register.html", form=form, title=title)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    """Confirm user account from confirmation email link."""

    if current_user.confirmed:
        flash("This account is already confirmed. You're all set!", "primary")
        return redirect(url_for("main.index"))

    if current_user.confirm_account_token(token):
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")

    else:
        print(token)
        flash("This confirmation link is invalid or has expired.", "error")

    return redirect(url_for("main.index"))


@auth.route("/request_password_reset", methods=["GET", "POST"])
def reset_password_request():
    """Display form to request a password reset link."""

    from motiveandcue import send_email
    form = RequestPasswordResetForm()
    title = "Reset Password"

    if current_user.is_authenticated:
        flash("You're currently logged in. Your password can be changed on the My Account page.", "message")
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()

        if user:
            token = user.generate_token()
            send_email(user.email, "Reset Your Password", "auth/email/reset", user=user, token=token)
            flash("Please check your email for instructions on how to reset your password.", "message")

        else:
            flash("No user registered with that email address.", "error")
        return redirect(url_for("main.index"))

    return render_template("auth/password_request.html", form=form, title=title)


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password."""

    user = User.confirm_reset_token(self=User, token=token)
    form = ResetPasswordForm()
    title = "Reset Password"

    if not user:
        flash("This password reset link is invalid or expired.", "error")
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()

        flash("Your new password has been set.", "success")
        return redirect(url_for("main.index"))
        
    return render_template("auth/password_reset.html", form=form, title=title)


@auth.route("/my_account")
def account_page():
    """Displays user's account page."""

    title = "My Account"
        
    return render_template("auth/account.html", title=title)