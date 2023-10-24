import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

######################
# ROUTES
######################
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
def get_drinks():
    # obtain and format drinks
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": formatted_drinks
        }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drink_detail():
    # obtain and format drinks
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": formatted_drinks
        }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink():
    drink_data = request.get_json()
    title = drink_data.get("title", None)
    recipe = drink_data.get("recipe", None)

    # can't be empty
    if title is None or recipe is None:
        abort(400)

    # uniqueness of titles
    all_titles = [drink.title for drink in Drink.query.all()]
    if title in all_titles:
        abort(400)

    # format the recipe correctly
    recipe = json.dumps(recipe)
    if recipe[0] != "[":
        recipe = f"[{recipe}"
    if recipe[-1] != "]":
        recipe = f"{recipe}]"


    new_drink = Drink(title=title, recipe=recipe)
    new_drink.insert()

    return jsonify({
        "success": True,
        "drinks": [new_drink.long()]
        }), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    update_data = request.get_json()

    if "title" in update_data:
        drink.title = update_data["title"]

    if "recipe" in update_data:
        recipe = json.dumps(update_data["recipe"])
        if recipe[0] != "[":
            recipe = f"[{recipe}"
        if recipe[-1] != "]":
            recipe = f"{recipe}]"
        drink.recipe = recipe

    drink.update()

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
        }), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        "success": True,
        "delete": drink_id
        }), 200

######################
# Error Handling
######################
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error_request(e):
    return jsonify({
        "success": False,
        "error": e.status_code,
        "message": e.error
        }), e.status_code

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(401)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(403)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "incorrect permissions"
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422




if __name__ == "__main__":
    app.debug = True
    app.run()
