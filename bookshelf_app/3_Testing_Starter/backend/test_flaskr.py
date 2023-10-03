import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Book


class BookTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_book = {"title": "Anansi Boys", "author": "Neil Gaiman", "rating": 5}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_books(self):
        response = self.client().get('/books')
        data = json.loads(response.data)

        # get the correct status code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # make sure that it returns the total books and that there is a length
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))

    def test_404_sent_requesting_beyond_valid_page(self):
        response = self.client().get('/books?page=100000', json={'rating': 1})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_update_book_rating(self):
        response = self.client().patch('/books/5', json={'rating': 1})
        data = json.loads(response.data)

        # check the rating is now 1
        book = Book.query.filter(Book.id == 5).one_or_none()
        self.assertEqual(book.rating, 1)

        # check that we get the correct response and returned data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_400_for_failed_update(self):
        # not including a json body
        response = self.client().patch('/books/5')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "bad request")

    def test_delete_book(self):
        response = self.client().delete('/books/1')
        data = json.loads(response.data)

        # get the book from the database and make sure it doesn't exist
        book = Book.query.filter(Book.id == 1).one_or_none()
        self.assertEqual(book, None)

        # get the correct response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)
        self.assertTrue(data['books'])
        self.assertTrue(data['total_books'])

    def test_422_if_book_does_not_exist(self):
        response = self.client().delete('/books/1000000')
        data = json.loads(response.data)

        # get the correct response
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_new_book(self):
        response = self.client().post('/books', json = self.new_book)
        data = json.loads(response.data)

        # make sure the book exists
        book = Book.query.filter(Book.id == data['created']).one_or_none()
        self.assertEqual(book.id, data['created'])

        # get the correct response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['books'])
        self.assertTrue(data['total_books'])

    def test_405_if_book_creation_not_allowed(self):
        response = self.client().post('/books/45', json = self.new_book)
        data = json.loads(response.data)

        # get the correct response
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')


# @TODO: Write at least two tests for each endpoint - one each for success and error behavior.
#        You can feel free to write additional tests for nuanced functionality,
#        Such as adding a book without a rating, etc.
#        Since there are four routes currently, you should have at least eight tests.
# Optional: Update the book information in setUp to make the test database your own!


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
