import os
from os import environ as env
from dotenv import load_dotenv, dotenv_values
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

load_dotenv()

USER = env["DB_USER"]
PASSWORD = env["DB_PASS"]
HOST = env["DB_HOST"]
NAME = env["DB_NAME_TEST"]

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = database_path = "postgresql://{}:{}@{}/{}".format(
                    USER, PASSWORD, HOST, NAME)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "what is 2+2?",
                             "answer": "4",
                             "category": 1,
                             "difficulty": 1}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    

    def tearDown(self):
        """Executed after reach test"""
        pass

    # test to get categories via endpoint /categories
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(data["total_categories"])

    def test_404_sent_request_to_invalid_page(self):
        response = self.client().get('/categories/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # test to get questions endpoints /questions and /questions?page=<n>
    # where <n> is an int
    def test_get_paginated_questions_default(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["current_category"], None)
        self.assertTrue(data["categories"])

    def test_get_paginated_questions_page2(self):
        response = self.client().get('/questions?page=2')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["current_category"], None)
        self.assertTrue(data["categories"])

    def test_404_sent_request_beyond_valid_page(self):
        response = self.client().get('/questions?page=100000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # test to delete a question via the endpoint /questions/<int:question_id>
    def test_delete_question(self):
        # create the question that will be deleted
        question = Question(question='test',
                            answer='test',
                            category=4,
                            difficulty=4)
        question.insert()
        test_id = question.id

        response = self.client().delete(f"/questions/{test_id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted"])
        self.assertTrue(data["total_questions"])

    def test_404_delete_invalid_question(self):
        response = self.client().delete("/questions/100000")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # test to create a new question via the endpoints /questions
    def test_post_new_question(self):
        response = self.client().post("/questions", json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["current_category"], 
            self.new_question["category"])

    def test_422_failed_to_post_new_question(self):
        response = self.client().post('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "cannot process")

    # test search functionality
    def test_search_with_results(self):
        response = self.client().post('/questions', json={"searchTerm": "What"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_search_without_results(self):
        response = self.client().post('/questions', json={"searchTerm": "Zqpw"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["total_questions"], 0)

    # test question by category functionality
    def test_get_questions_by_category(self):
        response = self.client().get("/categories/1/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])

    def test_400_invalid_category(self):
        response = self.client().get("/categories/80/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    # test the /quizzes endpoint for
    def test_play_quiz_all_categories(self):
        response = self.client().post('/quizzes', json={"quiz_category": {"id": 0},
            "previous_questions": []})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_play_quiz_one_category(self):
        response = self.client().post('/quizzes', json={"quiz_category": {"id": 3},
            "previous_questions": []})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_play_quiz_previous_questions(self):
        response = self.client().post('/quizzes', json={"quiz_category": {"id": 0},
            "previous_questions": [5, 11, 13, 16, 22]})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_422_no_category(self):
        response = self.client().post('/quizzes', json={"previous_questions": []})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "cannot process")

    def test_422_no_previous_questions(self):
        response = self.client().post('/quizzes', json={"quiz_category": {"id": 0}})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "cannot process")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()