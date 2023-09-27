from flask import Flask, jsonify, request, abort
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

    @app.route('/plants', methods=["GET", "POST"])
    def get_plants():
        page = request.args.get('page', 1, type=int)
        start = (page  - 1) * 10
        end = start + 10
        plants = Plant.query.all()
        formatted_plants = [plant.format() for plant in plants]


        return jsonify({"success": True,
                        "plants": formatted_plants[start:end],
                        "total_plants": len(formatted_plants)})

    @app.route('/plants/<int:plant_id>')
    def get_specific_plant(plant_id):
        plant = Plant.query.filter(Plant.id==plant_id).one_or_none()

        # if the item is not found return 404 not found error
        if plant is None:
            abort(404)

        else:
            return jsonify({
                "success": True,
                "plant": plant.format()
                })


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0")
