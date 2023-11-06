import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from models import setup_db, Movie, Actor


app = Flask(__name__)
db = setup_db(app)
migrate = Migrate(app, db)
CORS(app)


@app.route('/', methods = ['GET'])
def test_health():
    """
    Used to test if the app runs and is healthy
    """
    return "Healthy"

@app.route('/actors', methods = ["GET"])
def get_actors():
    actors = Actor.query.all()




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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)