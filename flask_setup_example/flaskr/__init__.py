from flask import Flask, jsonify
from pathlib import Path

def create_app(test_config=None):
    # instance_relative_config=True tells the app that configuration files
    # are in the same directory
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapp(
        # in general SECRET_KEY should *actually* be secret
        SECRET_KEY='dev',
        DATABASE=Path(app.instance_path, 'flaskr.sqlite'))

    if test_config is None:
        #load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)

    @app.route('/')
    def hello():
        return jsonify({'message': 'HELLO WORLD'})

    @app.route('/smiley')
    def smiley():
        return ':)'

    return app