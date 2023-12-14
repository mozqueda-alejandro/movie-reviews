from app import db
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(user_id):
    return CustomUser.query.get(int(user_id))


class Movie(db.Model):
    __tablename__ = "movie"

    budget = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    imdb_id = db.Column(db.String(10), nullable=False)
    original_language = db.Column(db.String(2), nullable=False)
    overview = db.Column(db.String(512), nullable=False)
    popularity = db.Column(db.Float, nullable=False)
    poster_path = db.Column(db.String(64), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    revenue = db.Column(db.Integer, nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    vote_average = db.Column(db.Float, nullable=False)
    vote_count = db.Column(db.Integer, nullable=False)

    # One-to-one
    link = db.relationship("Link", back_populates="movie", uselist=False, lazy=True)

    # One-to-many
    custom_users = db.relationship("Rating", back_populates="movie", lazy=True)
    genres = db.relationship("MovieGenre", back_populates="movie", lazy=True)
    countries = db.relationship("MovieCountry", back_populates="movie", lazy=True)

    def __repr__(self):
        return f"Movie('{self.title}', '{self.release_date}')"


# LINK MODEL
class Link(db.Model):
    __tablename__ = "link"

    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), primary_key=True)
    imdb_id = db.Column(db.Integer, nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=False)

    movie = db.relationship("Movie", back_populates="link", lazy=True)


# USER MODEL
class CustomUser(UserMixin, db.Model):
    __tablename__ = "custom_user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    phone_number = db.Column(db.String(16), nullable=True)
    password = db.Column(db.String(255), nullable=False)

    movies = db.relationship("Rating", back_populates="custom_user")

    def get_id(self):
        return self.id

    def __repr__(self):
        return f"CustomUser('{self.username}', '{self.email}', '{self.phone_number}')"


# RATING MODEL
class Rating(db.Model):
    __tablename__ = "rating"

    id = db.Column(db.Integer, primary_key=True)
    custom_user_id = db.Column(db.Integer, db.ForeignKey("custom_user.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    datetime = db.Column(db.TIMESTAMP(timezone=False), nullable=False)

    custom_user = db.relationship("CustomUser", back_populates="movies")
    movie = db.relationship("Movie", back_populates="custom_users")


# GENRE MODEL
class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)

    movies = db.relationship("MovieGenre", back_populates="genre")


# MOVIE_GENRE MODEL
class MovieGenre(db.Model):
    __tablename__ = "movie_genre"

    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), primary_key=True)

    movie = db.relationship("Movie", back_populates="genres")
    genre = db.relationship("Genre", back_populates="movies")


# COUNTRY MODEL
class Country(db.Model):
    __tablename__ = "country"

    id = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(32), nullable=False)

    movies = db.relationship("MovieCountry", back_populates="country")


# MOVIE_COUNTRY MODEL
class MovieCountry(db.Model):
    __tablename__ = "movie_country"

    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"), primary_key=True)

    movie = db.relationship("Movie", back_populates="countries")
    country = db.relationship("Country", back_populates="movies")
