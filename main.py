from enum import unique
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import query
from wtforms import StringField, SubmitField
from wtforms.fields.core import FloatField, IntegerField
from wtforms.validators import DataRequired
import requests
from pprint import pprint


API_KEY = "089dc0726eb00c1537cb3c254c992ca6"

app = Flask(__name__)
app.config.update(
    SECRET_KEY="8BYkEfBA6O6donzWlSihBXox7C0sKR6b",
    SQLALCHEMY_DATABASE_URI="sqlite:///movies.db",
)
db = SQLAlchemy(app)
Bootstrap(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


class UpdateForm(FlaskForm):
    new_rating = FloatField("Your Rating out of 10", validators=[DataRequired()])
    new_review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Submit")


db.create_all()


class AddForm(FlaskForm):
    new_movie = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


def find_movie(movie_title):
    parameters = {
        "api_key": API_KEY,
        "query": movie_title,
    }
    response = requests.get(
        url="https://api.themoviedb.org/3/search/movie", params=parameters
    )
    return response.json()["results"]


def get_new_movie(movie_id):
    response = requests.get(
        url=f"https://api.themoviedb.org/3/movie/{movie_id}",
        params={"api_key": API_KEY},
    )
    return response.json()


# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    rank = len(all_movies)
    for movie in all_movies:
        movie.ranking = rank
        db.session.commit() # This shit it's bugged
        rank -= 1
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = UpdateForm()
    movie_to_update = Movie.query.get(request.args.get("id"))
    if form.validate_on_submit():
        movie_to_update.rating = form.new_rating.data
        movie_to_update.review = form.new_review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, movie=movie_to_update.title)


@app.route("/delete")
def delete():
    movie_to_delete = Movie.query.get(request.args.get("id"))
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        search_result = find_movie(form.new_movie.data)
        return render_template("select.html", movies=search_result)
    return render_template("add.html", form=form)


@app.route("/get-movie")
def get_movie():
    movie_id = int(request.args.get("id"))
    movie = get_new_movie(movie_id)
    new_movie = Movie(
        title=movie["title"],
        year=movie["release_date"].split("-")[0],
        description=movie["overview"],
        img_url=f'https://image.tmdb.org/t/p/w500{movie["poster_path"]}',
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("edit", id=new_movie.id))


if __name__ == "__main__":
    app.run(debug=True)
