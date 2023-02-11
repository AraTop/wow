from flask import Flask, request , jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

movies_ns = api.namespace("movies")

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating= fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int(dump_only=True)

movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()

@movies_ns.route("")
class MoviesView(Resource):
    def get(self):
        movies = db.session.query(Movie).all()
        return movies_schema.dump(movies), 200

@movies_ns.route("/<uid>")
class MovieView(Resource):
    def get(self,uid):
        movie = db.session.query(Movie).filter(Movie.id == uid).one()
        return movie_schema.dump(movie), 200

@movies_ns.route("/") 
class MovieDirector(Resource):
    def get(self):
        uid = request.args.get("director_id")
        movie = db.session.query(Movie).filter(Movie.director_id == int(uid)).one()
        return movie_schema.dump(movie), 200

@movies_ns.route("/")
class MovieGenre(Resource):
    def get(self):
        uid = request.args.get("genre_id")
        movie = db.session.query(Movie).filter(Movie.genre_id == int(uid)).one()
        return movie_schema.dump(movie), 200

if __name__ == '__main__':
    app.run(debug=True)