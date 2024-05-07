import json

import pandas as pd
import psycopg2 as psycopg
import sqlalchemy
from sqlalchemy import create_engine

movie_dtypes = {"budget": int,
                "genres": str,
                "id": int,
                "imdb_id": str,
                "original_language": str,
                "overview": str,
                "popularity": float,
                "poster_path": str,
                "production_countries": str,
                "release_date": str,
                "revenue": "Int64",
                "runtime": "Int64",
                "title": str,
                "vote_average": float,
                "vote_count": "Int64"}


def parse_json(df_movies: pd.DataFrame, conn_sqlalchemy: sqlalchemy.Connection):
    # json in the form: [{"id": 18, "name": "Drama"}]
    # json in the form: [{"iso_3166_1": "US", "name": "United States of America"}]
    try:
        df_movies["genres"] = df_movies["genres"].map(lambda x: x if pd.isnull(x) else x.replace("'", '"'))
        df_movies["production_countries"] = df_movies["production_countries"].map(
            lambda x: x if pd.isnull(x) else x.replace("'", '"'))
        movie_genres, movie_countries = [], []
        genre_dict, country_dict = {}, {}
        for _, row in df_movies.iterrows():
            for genre in json.loads(row["genres"]):
                movie_genres.append((row["id"], genre["id"]))
                if genre["id"] not in genre_dict:
                    genre_dict[genre["id"]] = genre["name"]

            for country in json.loads(row["production_countries"]):
                movie_countries.append((row["id"], country["iso_3166_1"]))
                if country["iso_3166_1"] not in country_dict:
                    country_dict[country["iso_3166_1"]] = country["name"]

        dict_to_list = lambda d: [(key, value) for key, value in d.items()]
        df_genres = pd.DataFrame(dict_to_list(genre_dict), columns=["id", "name"])
        # df_genres.to_sql("genre", conn_sqlalchemy, if_exists="append", index=False)  #######################

        df_countries = pd.DataFrame(dict_to_list(country_dict), columns=["id", "name"])
        # df_countries.to_sql("country", conn_sqlalchemy, if_exists="append", index=False)  #######################

        return movie_genres, movie_countries
    except Exception as e:
        # print(f"Error parsing JSON: {e}")
        pass


def get_movies():
    database_url = "postgresql://postgres:admoz@localhost:5432/movie"
    db = create_engine(database_url)
    conn_sqlalchemy = db.connect()
    psycopg_conn = psycopg.connect(database_url)
    psycopg_conn.autocommit = True
    cursor = psycopg_conn.cursor()

    # Preprocess the CSV file
    infile_path = "C:/Users/admoz/PycharmProjects/MovieProject/app/data/movies_metadata.csv"
    outfile_path = "C:/Users/admoz/PycharmProjects/MovieProject/app/data/movies_metadata_edited.csv"
    # with open(infile_path, 'r', newline='', encoding="utf8") as infile, open(outfile_path, 'w', newline='', encoding="utf8") as outfile:
    #     reader = csv.reader(infile)
    #     writer = csv.writer(outfile)
    #     headers = next(reader)
    #     num_delimiters = len(headers)
    #
    #     writer.writerow(headers)
    #     for row in reader:
    #         if len(row) == num_delimiters:
    #             writer.writerow(row)
    row = pd.Series
    movies = pd.DataFrame()
    try:
        cols = list(movie_dtypes.keys())
        movies = pd.read_csv(outfile_path,
                             usecols=cols,
                             dtype=movie_dtypes)
        movies = movies.dropna()

        zero_columns = ["budget", "revenue", "runtime", "vote_average", "vote_count"]
        movies = movies[(movies[zero_columns] != 0).all(axis=1)]

        #######
        # return pd.DataFrame(movies, columns=["id"])
        #######

        movie_genres_list, movie_countries_list = parse_json(movies, conn_sqlalchemy)
        movie_genres = pd.DataFrame(movie_genres_list, columns=["movie_id", "genre_id"])
        # movie_genres.to_sql("movie_genre", con=conn_sqlalchemy, if_exists="append", index=False)  #######################

        movie_countries = pd.DataFrame(movie_countries_list, columns=["movie_id", "country_id"])
        # movie_countries.to_sql("movie_country", con=conn_sqlalchemy, if_exists="append", index=False)  ###################

        movies = movies.drop(columns=["genres", "production_countries"])
        # df_first_row = pd.DataFrame(movies.iloc[0]).transpose()
        # df_first_row.to_sql("movie", con=conn_sqlalchemy, if_exists="append", index=False)

        # a = len(movies)
        movies1 = movies[~movies.duplicated(subset="id", keep='first')]
        # b = len(movies1)

        sql_movie_script = '''
        INSERT INTO movie (budget, id, imdb_id, original_language, overview, popularity, poster_path, release_date, revenue, runtime, title, vote_average, vote_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''
        # for _, row in movies1.iterrows():  #########################################
        #     cursor.execute(sql_movie_script, (
        #         row["budget"], row["id"], row["imdb_id"], row["original_language"], row["overview"], row["popularity"],
        #         row["poster_path"], row["release_date"], row["revenue"], row["runtime"], row["title"], row["vote_average"],
        #         row["vote_count"]))
        # movies.to_sql("movie", con=conn_sqlalchemy, if_exists="append", index=False)
        movie_ids = pd.DataFrame(movies1["id"])
        movie_ids.rename(columns={"id": "movieId"}, inplace=True)

        links = pd.read_csv("C:/Users/admoz/PycharmProjects/MovieProject/app/data/links.csv",
                            usecols=["movieId", "imdbId", "tmdbId"],
                            dtype={"movieId": int, "imdbId": int, "tmdbId": "Int64"}).merge(
            movie_ids, on="movieId", how="inner")
        link_mapping = {"movieId": "movie_id", "imdbId": "imdb_id", "tmdbId": "tmdb_id"}
        links.rename(columns=link_mapping, inplace=True)
        # links.to_sql("link", con=conn_sqlalchemy, if_exists="append", index=False)

    except Exception as e:
        print(row)
        print(f"Error reading CSV file: {e}")
        return None

    # print(movie_genres.head())
    # print(len(movie_genres))


import requests
# import time
# import re
# import os
#
# downloaded_image_dir = "movie_images"
# def download_poster(title, poster_path):
#
#     imgUrl = 'https://image.tmdb.org/t/p/w185/' + poster_path
#
#     local_filename = re.sub(r'\W+', ' ', title).lower().strip().replace(" ", "-") + '.jpg'
#
#     try:
#         session = requests.Session()
#         r = session.get(imgUrl, stream=True, verify=False)
#         with open(downloaded_image_dir + '/' + local_filename, 'wb') as f:
#             for chunk in r.iter_content(chunk_size=1024):
#                 f.write(chunk)
#     except:
#         print('PROBLEM downloading', title, poster_path, imgUrl)
#
#     time.sleep(0.2)


def run():
    movie_id = 862
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

    headers = {
        "accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        metadata = response.json()
        poster_path = metadata.get("poster_path", None)
        backdrop_path = metadata.get("backdrop_path", None)

        # Print or use the values as needed
        print("Poster path:", poster_path)
        print("Backdrop path:", backdrop_path)
    else:
        print(f"Error: {response.status_code}")


    print(response.text)

    # i = 0
    # if not os.path.exists(downloaded_image_dir):
    #     os.makedirs(downloaded_image_dir)
    # for index, row in get_movies().iterrows():
    #     if i > 2:
    #         break
    #     i += 1
    #     download_poster(str(row['id']))