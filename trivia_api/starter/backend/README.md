# Backend - Full Stack Trivia API 

### Installing Dependencies for the Backend

1. **Python 3.9** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

If using Windows run the following instead:
```bash
psql.exe trivia < trivia.psql
```

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment. Make sure that the server has started, as well.

To run the server, execute:

```bash
FLASK_APP=flaskr FLASK_ENV=development FLASK_DEBUG=true flask run
```

## API Documentation

### Getting Started

#### Base URL

This app is still in development and can only be run locally. It can be accessed at http://localhost:5000

#### API Keys/Authentication

N/A

### Errors

Errors return a JSON object in the response, as well as the error status code. Handlers have been made for errors 400, 404, 405, 422, and 500. The JSON object returned is in the following format (using 400 as an example)

```
{
    "success": False,
    "error": 400,
    "message": "bad request"
}
```

The messages for the others are as follows:
* 404: resource not found
* 405: method now allowed
* 422: cannot process
* 500: internal server error

### Endpoints

#### GET /categories

* Returns a JSON object that contains
    * all categories
    * the total number of categories in a dictionary where the key-value pair is category_id: category string
    * a success message
* Sample: curl http://localhost:5000/categories -X GET
```
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "success": true,
    "total_categories": 6
}
```

#### GET /categories/\<int:category_id\>/questions

* Returns a JSON object that contains 
    * the a dictionary containing information about the current category
    * the questions in a given category as a list of formatted questions. The questions are paginated for a max of 10 per page
    * a success message
    * the total number of questions being returned 
* Sample: curl http://localhost:5000/categories/1/questions -X GET
```
{
    "current_category": {
        "id": 1,
        "type": "Science"
    },
    "questions": [
        {
            "answer": "4",
            "category": 1,
            "difficulty": 1,
            "id": 1,
            "question": "What is 2+2?"
        },
        {
            "answer": "An unconfined aquifier",
            "category": 1,
            "difficulty": 3,
            "id": 2
            "question": "Is it easier to recharge a confined or an unconfined aquifer?"
        }

    ],
    "success": true,
    "total_questions": 2
}
```
A formatted question is a dictionary with the following format:
```
{
    "answer": str,
    "category": int,
    "difficulty": int,
    "id": int,
    "question": str
}
```

#### GET /questions

* Returns a JSON object that contains
    * all categories
    * the current category as null because one has not yet been chosen
    * all questions as a list of formatted questions. The questions are paginated for a max of 10 per page
    * a success message
    * the total number of questions being returned
* Sample: curl http://localhost:5000/questions -X GET
```
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": null,
    "questions": [
        {
            "answer": "4",
            "category": 1,
            "difficulty": 1,
            "id": 1,
            "question": "What is 2+2?"
        },
        {
            "answer": "Mac Dre",
            "category": 2,
            "difficulty": 2,
            "id": 2,
            "question": "Who wrote the song "Thizzle Dance"?
        }
    ],
    "success": true,
    "total_questions": 2
}
```
A formatted question is a dictionary with the following format:
```
{
    "answer": str,
    "category": int,
    "difficulty": int,
    "id": int,
    "question": str
}
```
#### POST /questions

* POST requests to this endpoint has two functionalities. The first is to search for questions and the other is to create a new question.

##### Search

* The JSON object that is passed via POST to this endpoint must contain the key "searchTerm" with a related search term string.
* Returns a JSON object that contains
    * a list of formatted questions that contain the search term string. The search is case-insensitive. The questions are paginated for a max of 10 per page
    * a success message
    * the total number of questions being returned
* Sample: curl http://localhost:5000/questions -X POST -H 'Content-Type: application/json' -d '{"searchTerm": "Thizzle"}'
```
{
    "questions": [
        {
            "answer": "Mac Dre",
            "category": 2,
            "difficulty": 2,
            "id": 2,
            "question": "Who wrote the song "Thizzle Dance"?
        }
    ],
    "success": true,
    "total_questions": 1
}
```
A formatted question is a dictionary with the following format:
```
{
    "answer": str,
    "category": int,
    "difficulty": int,
    "id": int,
    "question": str
}
```
#### DELETE /questions/\<int:question_id\>

#### POST /quizzes



## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql 
python test_flaskr.py
```
If using Windows the third line should instead be
```
psql.exe trivia_test < trivia.psql
```