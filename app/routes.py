import os
import re

import psycopg2
from flask import render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
import requests

from app import app, db, Repository
from app.forms import *
from app.models import *

login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    repository = Repository(conn_psycopg=psycopg2.connect(os.getenv("database_url")), db=db)
    # print(repository.get_popular_movies())
    # print("admoz: ", repository.check_user_exists("admoz"))
    # print("admin: ", repository.check_user_exists("admin"))
    # repository.add_custom_user("admoz", "as", "12345", "pep")
    # print("admoz: ", repository.check_user_exists("admoz"))

    # for movie_id in repository.get_movie_ids():
    #     url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    #
    #     headers = {
    #         "accept": "application/json",
    #         "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1NGRlOWVlZDQ4NDU2NzM5MjIxMDVjMjdlMjA0NDlmNyIsInN1YiI6IjY1NzU1NzQ2YzYwMDZkMDBlNWQzYWQzMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lXWNlidWaLPjBwOXh77eToqHq776PAQZfSBz8HO1nHU"
    #     }
    #
    #     response = requests.get(url, headers=headers)
    #     if response.status_code == 200:
    #         metadata = response.json()
    #         poster_path = metadata.get("poster_path", "N/A")
    #         backdrop_path = metadata.get("backdrop_path", "N/A")
    #
    #         repository.store_images(movie_id, poster_path, backdrop_path)
    #     else:
    #         print(f"Error: {response.status_code}")


# Used as part of the flask_login code.
@login_manager.user_loader
def load_user(user_id):
    return CustomUser.query.get(int(user_id))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/catalog')
def catalog():
    popular_movies = repository.get_popular_movies()
    blockbuster_movies = repository.get_blockbuster_movies()

    return render_template("catalog.html",
                           popular_movies=popular_movies,
                           blockbuster_movies=blockbuster_movies)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    form_username = form.username.data
    form_email = form.email.data
    form_phone_number = form.phone_number.data
    form_password = form.password.data

    if form.validate_on_submit():
        errors = []
        if repository.check_user_exists(form_username):
            errors.append("Username already exists.")
        if not is_valid_email(form_email):
            errors.append("Invalid email address.")
        if len(form_phone_number) != 0:
            if not is_valid_phone_number(form_phone_number):
                errors.append("Invalid phone number.")
        if len(errors) != 0:
            for error in errors:
                flash(error, "error")
            return redirect(url_for('register'))

        repository.add_custom_user(form_username, form_email, form_phone_number, form_password)
        flash("You have successfully registered. Please log in ", "success")

    return render_template("register.html", title="Register", form=form)


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    match = re.match(pattern, email)
    return match is not None


def is_valid_phone_number(phone_number):
    pattern = re.compile(r'^\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$')
    match = pattern.match(phone_number)
    return bool(match)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    form_username = form.username.data
    form_password = form.password.data

    if form.validate_on_submit():
        user = CustomUser.query.filter_by(username=form_username).first()
        if user is None:
            flash("No user found with that username. If you don't have an account, please register.")
            return redirect(url_for('login'))

        password = user.password
        if password != form_password:
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user)
        session.permanent = True
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Redirects unauthorized users to the login page.
@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('login'))
