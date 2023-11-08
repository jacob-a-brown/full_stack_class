import os
from os import environ as env
from sqlalchemy import Column, create_engine
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import json
from dotenv import load_dotenv, dotenv_values

# load environment variables from .env file
load_dotenv(override=True)
DATABASE_URL = env['DATABASE_URL']

db = SQLAlchemy()

def setup_db(app, database_path=DATABASE_URL):
    """
    Binds a flask application and a SQLAlchemy service
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

class Movie(db.Model):
    __tablename__ = 'movies'

    id = Column(db.Integer, primary_key = True)
    title = Column(db.String)
    release_date = Column(db.Date)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def __repr__(self):
        return f"<Movie {self.title}>"

    def format(self):
        return {
            "id": self.id,
            "title": self.title,
            "release_date": self.release_date.strftime('%Y-%m-%d')
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Actor(db.Model):
    __tablename__ = "actors"

    id = Column(db.Integer, primary_key = True)
    name = Column(db.String)
    age = Column(db.Integer)
    gender = Column(db.String)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def __repr__(self):
        return f"<Actor {self.name}>"

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


    def delete(self):
        db.session.delete(self)
        db.session.commit()