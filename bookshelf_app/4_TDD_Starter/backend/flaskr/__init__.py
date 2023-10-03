import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8


def paginate_books(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # @TODO: Create a new endpoint or update a previous endpoint to handle searching for a team in the title
    #        the body argument is called 'search' coming from the frontend.
    #        If you use a different argument, make sure to update it in the frontend code.
    #        The endpoint will need to return success value, a list of books for the search and the number of books with the search term
    #        Response body keys: 'success', 'books' and 'total_books'

    @app.route("/books")
    def retrieve_books():
        selection = Book.query.order_by(Book.id).all()
    
        current_books = paginate_books(request, selection)

        if len(current_books) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "books": current_books,
                "total_books": len(Book.query.all()),
            }
        )


    @app.route("/books/<int:book_id>", methods=["PATCH"])
    def update_book(book_id):

        body = request.get_json()

        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()
            if book is None:
                abort(404)

            if "rating" in body:
                book.rating = int(body.get("rating"))

            book.update()

            return jsonify(
                {
                    "success": True,
                }
            )

        except:
            abort(400)

    @app.route("/books/<int:book_id>", methods=["DELETE"])
    def delete_book(book_id):
        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()

            if book is None:
                abort(404)

            book.delete()
            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": book_id,
                    "books": current_books,
                    "total_books": len(Book.query.all()),
                }
            )

        except:
            abort(422)

    @app.route("/books", methods=["POST"])
    def search_or_create_book():
        body = request.get_json()

        new_title = body.get("title", None)
        new_author = body.get("author", None)
        new_rating = body.get("rating", None)

        # flag for if a search is performed or if a book is being created
        # search means search
        # None means create
        search = body.get('search', None)

        try:
            # search
            if search:
                books = Book.query.filter(Book.title.ilike(f'%{search}%')).order_by(Book.id).all()
                formatted_books = [book.format() for book in books]
                return jsonify(
                        {
                            "success": True,
                            "books": formatted_books,
                            "total_books": len(formatted_books)
                        }
                    )

            #create
            else:
                book = Book(title=new_title, author=new_author, rating=new_rating)
                book.insert()

                selection = Book.query.order_by(Book.id).all()
                current_books = paginate_books(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": book.id,
                        "books": current_books,
                        "total_books": len(Book.query.all())
                    }
                )

        except:
            abort(422)


    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"success": False, "error": 405, "message": "bad request"}), 405

    return app