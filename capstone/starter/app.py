import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, setup_db, Movie, Actor


app = Flask(__name__)
setup_db(app)
migrate = Migrate(app, db)
CORS(app)

@app.route('/am_i_healthy', methods = ['GET'])
def test_health():
    """
    Used to test if the app runs and is healthy
    """
    return "You are healthy"

################
# /actors endpoints
################

@app.route('/actors', methods = ["GET"])
def get_all_actors():
    actors = Actor.query.order_by(Actor.id).all()

    if len(actors) == 0:
        abort(404)

    formatted_actors = [actor.format() for actor in actors]

    return jsonify({
        "success": True,
        "actors": formatted_actors,
        "num_actors": len(formatted_actors)
        })

@app.route('/actors/<actor_id>', methods = ["GET"])
def get_specific_actor(actor_id):
    actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

    if actor is None:
        abort(404)

    return jsonify({
        "success": True,
        "actor": actor.format()
        })

@app.route('/actors/<actor_id>', methods = ["DELETE"])
def delete_actor(actor_id):
    actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

    if actor is None:
        abort(422)

    try:
        actor.delete()
        return jsonify({
            "success": True,
            "deleted": actor_id
            })
    except:
        abort(422)

@app.route('/actors', methods = ["POST"])
def create_actor():
    body = request.get_json()

    name = body.get("name", None)
    age = body.get("age", None)
    gender = body.get("gender", None)

    if name is None or age is None or gender is None:
        abort(400)

    actor = Actor(name = name,
                  age = age,
                  gender = gender)

    try:
        actor.insert()
        return jsonify({
            "success": True,
            "actor": actor.format()
            })
    except Exception as e:
        print(e)
        abort(422)

@app.route('/actors/<actor_id>', methods = ["PATCH"])
def update_actor(actor_id):
    actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
    if actor is None:
        abort(404)

    body = request.get_json()

    name = body.get("name", None)
    age = body.get("age", None)
    gender = body.get("gender", None)

    if name is not None:
        actor.name = name

    if age is not None:
        actor.age = age

    if gender is not None:
        actor.gender = gender

    try:
        actor.update()
        return jsonify({
            "success": True,
            "actor": actor.format()
            })
    except Exception as e:
        print(e)
        abort(422)

################
# /movies endpoints
################

@app.route('/movies', methods = ["GET"])
def get_all_movies():

    movies = Movie.query.order_by(Movie.id).all()

    if len(movies) == 0:
        abort(404)

    formatted_movies = [movie.format() for movie in movies]

    return jsonify({
        "success": True,
        "movies": formatted_movies,
        "num_movies": len(formatted_movies)
        })

@app.route('/movies/<movie_id>', methods = ["GET"])
def get_specific_movie(movie_id):
    movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

    if movie is None:
        abort(404)

    return jsonify({
        "success": True,
        "movie": movie.format()
        }) 

@app.route('/movies/<movie_id>', methods = ["DELETE"])
def delete_movie(actor_id):
    movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

    if movie is None:
        abort(422)

    try:
        movie.delete()
        return jsonify({
            "success": True,
            "deleted": movie_id
            })
    except:
        abort(422)

@app.route('/movies', methods = ["POST"])
def create_movie():
    body = request.get_json()

    title = body.get("title", None)
    release_date = body.get("release_date", None)

    if title is None or release_date is None:
        abort(400)

    movie = Movie(title = title,
                  release_date = release_date)

    try:
        movie.insert()
        return jsonify({
            "success": True,
            "movie": movie.format()
            })
    except Exception as e:
        print(e)
        abort(422)

@app.route('/movies/<movie_id>', methods = ["PATCH"])
def update_movie(movie_id):
    movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
    
    if movie is None:
        abort(404)

    body = request.get_json()

    title = body.get("title", None)
    release_date = body.get("release_date", None)

    if title is not None:
        movie.title = title

    if release_date is not None:
        movie.release_date = release_date

    try:
        movie.update()
        return jsonify({
            "success": True,
            "movie": movie.format()
            })
    except Exception as e:
        print(e)
        abort(422)

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