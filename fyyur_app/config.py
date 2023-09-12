import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# password. file hidden by .gitignore
from some_info import password

# Enable debug mode.
DEBUG = True

# Connect to the database
# TODO IMPLEMENT DATABASE URL <-- DONE
SQLALCHEMY_DATABASE_URI = f'postgresql://brown:{password}@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False