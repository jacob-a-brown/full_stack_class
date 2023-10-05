import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_results(display_items, request, interval):
  """
  Paginate and format the results

  Args:
    display_items (list): the items to be paginated
    request (request): the request item from the endpoint
    interval (int): the number of items to be displayed per page

  Returns:
    list: the formatted and paginated results for a given page
  """
  # default to page 1 if "page" is not a key provided to the request
  page = request.args.get("page", 1, type=int)
  
  # start and end index
  start = (page - 1) * interval
  end = start + interval

  # collect, format, and return results
  paginated_results = display_items[start:end]
  formatted_paginated_results = [pr.format() for pr in paginated_results]
  return formatted_paginated_results

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add(
      "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
      "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    return response

  @app.route("/categories", methods=["GET"])
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    
    # change the categories to a dictionary of id: type to cooperate with
    # the front end
    formatted_categories_dict = {}
    for category in categories:
      formatted_categories_dict[category.id] = category.type

    if len(formatted_categories_dict) == 0:
      abort(404)

    return jsonify({
      "success": True,
      "categories": formatted_categories_dict,
      "total_categories": len(formatted_categories_dict)
      })

  @app.route('/categories/<int:category_id>/questions', methods=["GET"])
  def get_questions_by_category(category_id):
    current_category = Category.query.filter(
      Category.id == category_id).one_or_none()

    if current_category is None:
      abort(400) 

    current_category = current_category.format()

    questions = Question.query.filter(Question.category == category_id).all()
    paginated_questions = paginate_results(questions,
                                           request,
                                           QUESTIONS_PER_PAGE)

    return jsonify({
      "success": True,
      "questions": paginated_questions,
      "total_questions": len(paginated_questions),
      "current_category": current_category
      })

  @app.route("/questions", methods=["GET"])
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_results(questions, request, QUESTIONS_PER_PAGE)

    categories = Category.query.order_by(Category.id).all()
    # change the categories to a dictionary of id: type to cooperate with
    # the front end
    formatted_categories_dict = {}
    for category in categories:
      formatted_categories_dict[category.id] = category.type

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      "success": True,
      "questions": current_questions,
      "total_questions": len(questions),
      "current_category": None,
      "categories": formatted_categories_dict
      })

  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question is None:
      abort(404)

    question.delete()

    return jsonify({
      "success": True,
      "deleted": question_id,
      "total_questions": len(Question.query.all())
      })

  @app.route("/questions", methods=["POST"])
  def search_create_question():
    body = request.get_json()

    if body is None:
      abort(422)

    # the key search is used to determine if a search is to be performed
    # defaults to None 
    search = body.get("searchTerm", None)

    if search is not None:
      # search for a question
      questions = Question.query.filter(Question.question.ilike(
        f'%{search}%')).all()
      paginated_questions = paginate_results(questions,
                                             request,
                                             QUESTIONS_PER_PAGE)

      return jsonify({
        "success": True,
        "questions": paginated_questions,
        "total_questions": len(paginated_questions)
        })

    else:
      # create new question
      question = body.get("question", None)
      answer = body.get("answer", None)
      category = body.get("category", None)
      difficulty = body.get("difficulty", None)


      new_question = Question(question=question,
                              answer=answer,
                              category=category,
                              difficulty=difficulty)

      new_question.insert()

      all_questions = Question.query.order_by(Question.id).all()
      paginated_questions = paginate_results(all_questions,
                                             request,
                                             QUESTIONS_PER_PAGE)

      return jsonify({
        "success": True,
        "questions": paginated_questions,
        "total_questions": len(paginated_questions),
        "current_category": category
        })


  @app.route('/quizzes', methods=["POST"])
  def play_quiz():
    body = request.get_json()

    if 'quiz_category' not in body.keys() \
    or 'previous_questions' not in body.keys():
      abort(422)

    quiz_category = body.get("quiz_category")
    previous_questions = body.get("previous_questions", [])    

    if quiz_category["id"] == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter(
        Question.category == quiz_category["id"]).all()

    # set question to None to force an end if there are no questions left
    if len(questions) == len(previous_questions):
     return jsonify({
        "success": True,
        "question": None
        })

    # get random question
    while True:
      question = random.choice(questions)
      if question.id not in previous_questions:
        break


    return jsonify({
    "success": True,
    "question": question.format()
    })

  ################
  # error handlers
  ################

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
    }), 405


  @app.errorhandler(422)
  def cannot_process(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "cannot process"
      }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
      }), 500

  return app

    