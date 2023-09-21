from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from models import setup_db, Plant

def create_app(test_config=None):


    app = Flask(__name__, instance_relative_config=True)
    db = setup_db(app)
    migrate = Migrate(app, db)

    # first key in resources specifices what resources we are talking about
    # the inner key specifices what origins from the client can acces those resources at that URI
    #CORS(app, resources={r"*/api/*": {origins: "*"}})
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # enables CORS on a given route
    @cross_origin
    @app.route('/')
    def hello():
        return jsonify({'message':'HELLO WORLD'})


    return app