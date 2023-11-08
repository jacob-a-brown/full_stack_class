
import os
from os import environ as env
from dotenv import load_dotenv, dotenv_values
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import sys

from app import create_app
from models import db, setup_db, Actor, Movie

load_dotenv()

TEST_DATABASE_URL = env['TEST_DATABASE_URL']

JWT_CASTING_ASSISTANT = env['JWT_CASTING_ASSISTANT']
JWT_CASTING_DIRECTOR = env['JWT_CASTING_DIRECTOR']
JWT_EXECUTIVE_PRODUCER = env['JWT_EXECUTIVE_PRODUCER']

class CapstoneTestCase(unittest.TestCase):
    """
    This class represents the capstone test case
    """

    def setUp(self):
        """
        Define the test variables and initalize the app
        """
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = TEST_DATABASE_URL
        

        self.new_actor = {
            "name": "mister",
            "age": 3,
            "gender": "non-binary"
        }

        self.new_movie = {
            "title": "mister is a bad dog",
            "release_date": "2023-11-01"
        }



        # binds the app to the current context
        with self.app.app_context():
            self.db = db
            setup_db(self.app, self.database_path)

            # drop and create all tables
            self.db.drop_all()
            self.db.create_all()

        # create initial rows
        self.actor = Actor(name = "miso",
                           age = 5,
                           gender = "male")
        self.actor.insert()

        self.movie = Movie(title = "good cat",
                           release_date = "2018-08-09")
        self.movie.insert()

        self.casting_assistant = {
            "Authorization": f"Bearer {JWT_CASTING_ASSISTANT}"
        }

        self.casting_director = {
            "Authorization": f"Bearer {JWT_CASTING_DIRECTOR}"
        }

        self.executive_producer = {
            "Authorization": f"Bearer {JWT_EXECUTIVE_PRODUCER}"
        }

    def tearDown(self):
        """
        Executed after each test
        """
        # drop and create all tables
        self.db.drop_all()
        self.db.create_all()

        # create initial rows
        self.actor = Actor(name = "miso",
                           age = 5,
                           gender = "male")
        self.actor.insert()

        self.movie = Movie(title = "good cat",
                           release_date = "2018-08-09")
        self.movie.insert()

    ################
    # test /actors endpoinr=ts
    ################

    def test_get_all_actors(self):
        response = self.client().get('/actors',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["actors"], [self.actor.format()])
        self.assertEqual(data["num_actors"], 1)

    def test_404_bad_actors_endpoint(self):
        response = self.client().get('/actorz',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_get_specific_actor(self):
        response = self.client().get('/actors/1',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["actor"], self.actor.format())

    def test_404_cannot_get_actor_incorrect_id(self):
        response = self.client().get('/actors/1000000',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_delete_actor(self):
        response = self.client().delete('/actors/1',
            headers = self.casting_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted"])

    def test_422_cannot_delete_actor_incorrect_id(self):
        response = self.client().delete('/actors/100000',
            headers = self.casting_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_create_actor(self):
        response = self.client().post('/actors',
            json = self.new_actor,
            headers = self.casting_director)
        data = json.loads(response.data)
        mister = Actor.query.filter(Actor.name == 'mister').first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["actor"], mister.format())
        self.db.session.close()

    def test_400_cannot_create_actor_missing_data(self):
        bad_actor_data = {
            "name": "bad actor",
            "age": 99
        }
        response = self.client().post('/actors',
            json = bad_actor_data,
            headers = self.casting_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)

    def test_422_cannot_create_actor_bad_data_type(self):
        bad_actor_data = {
            "name": "bad actor",
            "age": "ten",
            "gender": "who cares"
        }
        response = self.client().post('/actors',
            json = bad_actor_data,
            headers = self.casting_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_update_actor(self):
        update_data = {
            "name": "chance"
        }
        response = self.client().patch('/actors/1',
            json = update_data,
            headers = self.casting_director)
        data = json.loads(response.data)

        chance = Actor.query.filter(Actor.name == 'chance').first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["actor"], chance.format())
        self.db.session.close()

    def test_404_cannot_update_actor_bad_id(self):
        update_data = {
            "name": "chance"
        }
        response = self.client().patch('/actors/10000',
            json = update_data,
            headers = self.casting_director)
        data = json.loads(response.data)        

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    ################
    # test /movies endpoints
    ################

    def test_get_all_movies(self):
        response = self.client().get('/movies',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movies"], [self.movie.format()])
        self.assertEqual(data["num_movies"], 1)

    def test_404_bad_movies_endpoint(self):
        response = self.client().get('/moviez',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_get_specific_movie(self):
        response = self.client().get('/movies/1',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movie"], self.movie.format())

    def test_404_cannot_get_movie_incorrect_id(self):
        response = self.client().get('/movies/1000000',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_delete_movie(self):
        response = self.client().delete('/movies/1',
            headers = self.executive_producer)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted"])

    def test_422_cannot_delete_movie_incorrect_id(self):
        response = self.client().delete('/movies/100000',
            headers = self.executive_producer)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_create_movie(self):
        response = self.client().post('/movies',
            json = self.new_movie,
            headers = self.executive_producer)
        data = json.loads(response.data)
        bad_dog_movie = Movie.query.filter\
            (Movie.title == 'mister is a bad dog').first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movie"], bad_dog_movie.format())
        self.db.session.close()

    def test_400_cannot_create_movie_missing_data(self):
        bad_movie_data = {
            "title": "mister is a bad dog"
        }
        response = self.client().post('/movies',
            json = bad_movie_data,
            headers = self.executive_producer)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)

    def test_422_cannot_create_movie_bad_data_type(self):
        bad_movie_data = {
            "title": "mister is a bad dog",
            "release_date": 12345678
        }
        response = self.client().post('/movies',
            json = bad_movie_data,
            headers = self.executive_producer)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_update_movie(self):
        update_data = {
            "title": "mister is a good dog"
        }
        response = self.client().patch('/movies/1',
            json = update_data,
            headers = self.executive_producer)
        data = json.loads(response.data)

        good_dog_movie = Movie.query.\
            filter(Movie.title == 'mister is a good dog').first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movie"], good_dog_movie.format())
        self.db.session.close()

    def test_404_cannot_update_movie_bad_id(self):
        update_data = {
            "name": "chance"
        }
        response = self.client().patch('/movies/10000',
            json = update_data,
            headers = self.executive_producer)
        data = json.loads(response.data)        

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)


    ################
    # RBAC fail tests. missing permission for each endpoint
    # the succesful endpoint tests determine that the correct roles work
    ################

    #####
    #401 tests - missing auth
    #####

    def test_401_missing_auth_header_get_actors(self):
        response = self.client().get('/actors')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_401_missing_auth_header_get_specific_actor(self):
        response = self.client().get('/actors/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_401_missing_auth_header_delete_actors(self):
        response = self.client().delete('/actors/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_401_missing_auth_header_create_actor(self):
        response = self.client().post('/actors',
            json = self.new_actor)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_401_missing_auth_header_update_actor(self):
        response = self.client().patch('/actors/1',
            json = self.new_actor)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)


    def test_401_missing_auth_header_get_movies(self):
        response = self.client().get('/movies')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_401_missing_auth_header_get_specific_movie(self):
        response = self.client().get('/movies/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_401_missing_auth_header_delete_movies(self):
        response = self.client().delete('/movies/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_401_missing_auth_header_create_movie(self):
        response = self.client().post('/movies',
            json = self.new_actor)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_401_missing_auth_header_update_movie(self):
        response = self.client().patch('/movies/1',
            json = self.new_actor)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["success"], False)

    #####
    # 403 tests - wrong permissions
    # not testing get methods as that is the most basic with the casting
    # assistant
    #####

    def test_403_missing_auth_header_delete_actors(self):
        response = self.client().delete('/actors/1',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["success"], False)

    def test_403_missing_auth_header_create_actor(self):
        response = self.client().post('/actors',
            json = self.new_actor,
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["success"], False)

    def test_403_missing_auth_header_update_actor(self):
        response = self.client().patch('/actors/1',
            json = self.new_actor,
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["success"], False)

    def test_403_missing_auth_header_delete_movies(self):
        response = self.client().delete('/movies/1',
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["success"], False)

    def test_403_missing_auth_header_create_movie(self):
        response = self.client().post('/movies',
            json = self.new_actor,
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["success"], False)

    def test_403_missing_auth_header_update_movie(self):
        response = self.client().patch('/movies/1',
            json = self.new_actor,
            headers = self.casting_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["success"], False)



if __name__ == "__main__":
    unittest.main()