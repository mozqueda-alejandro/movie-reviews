import pandas as pd


class Repository:
    def __init__(self, **kwargs):
        self.db = kwargs["db"]
        self.conn_psycopg = kwargs["conn_psycopg"]
        self.cursor = self.conn_psycopg.cursor()
        self.conn_psycopg.autocommit = True

    def check_user_exists(self, username: str) -> bool:
        self.cursor.execute(f"SELECT * FROM custom_user WHERE username='{username}'")
        user = self.cursor.fetchone()
        print(user)
        return user is not None

    def add_custom_user(self, username: str, email: str, phone_number: str, password: str) -> None:
        sql_script = f"INSERT INTO custom_user (username, email, phone_number, password) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(sql_script, (username, email, phone_number, password))
        return None

    def get_popular_movies(self):
        from app.models import Movie
        popular_movies = self.db.session.scalars(self.db.select(Movie).
                                                 where(Movie.vote_count > 1000).
                                                 order_by(Movie.vote_average.desc()).
                                                 limit(10)).all()
        return popular_movies

    def get_blockbuster_movies(self):
        from app.models import Movie
        blockbuster_movies = self.db.session.scalars(self.db.select(Movie).
                                                     where(Movie.revenue > 100000000).
                                                     order_by(Movie.revenue.desc()).
                                                     limit(10)).all()
        return blockbuster_movies

    def get_movie_ids(self):
        sql_script = "SELECT id FROM movie"
        self.cursor.execute(sql_script)
        movie_tuples = self.cursor.fetchall()
        movie_ids = [movie_tuple[0] for movie_tuple in movie_tuples if len(movie_tuple) == 1]
        return movie_ids

    def store_images(self, movie_id: int, poster_path: str, backdrop_path: str) -> None:
        sql_script = f"UPDATE movie SET poster_path='{poster_path}', backdrop_path='{backdrop_path}' WHERE id={movie_id}"
        self.cursor.execute(sql_script)
