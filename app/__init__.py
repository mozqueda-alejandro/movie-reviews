import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from app.Repository import Repository
from config import Config

app = Flask(__name__)

load_dotenv()
# In the form: postgresql://username:password@host:port/database_name
database_url = os.getenv("database_url")
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("database_url")

db = SQLAlchemy(app)
login = LoginManager(app)

from app import routes, models  # Do NOT move to top of file

if __name__ == '__main__':
    app.run(debug=True)
