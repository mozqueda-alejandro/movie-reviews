import os
import pandas as pd
import psycopg2 as psycopg

from datetime import datetime, date

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine


def import_csv_to_dataframe(csv_file_path, header_mapping=None):
    try:
        if header_mapping is None:
            return pd.read_csv(csv_file_path)

        df = pd.read_csv(csv_file_path)
        csv_headers = df.iloc[0].tolist() if not df.empty else []
        missing_headers = [header for header in header_mapping.keys() if header not in csv_headers]

        if missing_headers:
            raise ValueError(f"Headers not found in the CSV file: {missing_headers}")

        df = df[header_mapping.keys()]
        df.rename(columns=header_mapping, inplace=True)

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

    return df


def run():
    load_dotenv()
    # In the form: postgresql://username:password@localhost:port/database_name
    database_url = os.getenv("database_url")
    db = create_engine(database_url)
    conn_sqlalchemy = db.connect()

    # Example usage:
    csv_file_path = "data/movies_metadata.csv"
    header_mapping = {"budget": "budget",
                      "id": "id",
                      "imdb_id": "imdb_id",
                      "original_language": "original_language",
                      "overview": "overview",
                      "popularity": "popularity",
                      "poster_path": "poster_path",
                      "release_date": "release_date",
                      "revenue": "revenue",
                      "runtime": "runtime",
                      "title": "title",
                      "vote_average": "vote_average",
                      "vote_count": "vote_count"}

    # Call the function
    data_frame = import_csv_to_dataframe(csv_file_path, header_mapping)

    # Display the DataFrame
    print(data_frame.head())


