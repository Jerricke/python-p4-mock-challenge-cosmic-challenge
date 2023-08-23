#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Index(Resource):
    def get(self):
        return ""


api.add_resource(Index, "/")


class ScientistAll(Resource):
    def get(self):
        scientists = [s.to_dict(rules=("-missions",)) for s in Scientist.query.all()]
        return make_response(jsonify(scientists), 200)

    def post(self):
        data = request.get_json()
        if data["name"] and data["field_of_study"]:
            newScientist = Scientist(
                name=data["name"], field_of_study=data["field_of_study"]
            )
            db.session.add(newScientist)
            db.session.commit()

            return make_response(jsonify(newScientist.to_dict()), 201)
        else:
            return make_response({"errors": ["validation errors"]}, 403)


api.add_resource(ScientistAll, "/scientists")


class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            return make_response(jsonify(scientist.to_dict()), 200)
        else:
            return make_response({"error": "404 Scientist not found"}, 404)

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            data = request.get_json()
            try:
                if data["name"]:
                    setattr(scientist, "name", data["name"])
                if data["field_of_study"]:
                    setattr(scientist, "field_of_study", data["field_of_study"])
                db.session.add(scientist)
                db.session.commit()
                return make_response(
                    {"Message": "Scientist has been updated succesfully"}, 202
                )
            except:
                return make_response({"errors": ["validation errors"]}, 403)
        else:
            return make_response({"error": "404 Scientist not found"}, 404)

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return make_response("", 204)
        else:
            return make_response({"error": "404 Scientist not found"}, 404)


api.add_resource(ScientistById, "/scientists/<int:id>")


class PlanetAll(Resource):
    def get(self):
        planets = [p.to_dict(rules=("-missions",)) for p in Planet.query.all()]
        return make_response(jsonify(planets), 200)


api.add_resource(PlanetAll, "/planets")


class MissionAll(Resource):
    def post(self):
        data = request.get_json()
        if data["name"] and data["scientist_id"] and data["planet_id"]:
            newMission = Mission(
                name=data["name"],
                scientist_id=data["scientist_id"],
                planet_id=data["planet_id"],
            )
            db.session.add(newMission)
            db.session.commit()
            return make_response(jsonify(newMission.to_dict()), 201)
        else:
            return make_response({"errors": ["validation errors"]}, 403)


api.add_resource(MissionAll, "/missions")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
