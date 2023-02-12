import json
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
genres_ns = api.namespace("genres")
directors_ns = api.namespace("directors")

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

class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating= fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int(dump_only=True)

directors_schema = DirectorSchema(many=True)
director_chema = DirectorSchema()

genres_schema = GenreSchema(many=True)
genre_chema = GenreSchema()

movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()

@movies_ns.route("")
class MoviesView(Resource):
    def get(self):
        movies = db.session.query(Movie).all()
        if movies:
            try:
                return movies_schema.dump(movies), 200
            except Exception as s:
                return str(s), 404
        else:
            return "В таблице пусто",

    def post(self):
        data_user = json.loads(request.data)
        if data_user:
            try:
                output = Movie(**data_user)
                db.session.add(output)
                db.session.commit()
                return "", 201
            except Exception as s:
                return str(s), 404
        else:
            return "не ведены данные", 404

@movies_ns.route("/<uid>")
class MovieView(Resource):
    def get(self, uid):
        movie = Movie.query.get(uid)
        if movie:
            try:
                return movie_schema.dump(movie), 200
            except Exception as s:
                return str(s), 404
        else: 
            return "Данного id не существует , либо список пуст", 404

    def delete(self, uid):
        movie = Movie.query.get(uid)
        if movie:
            try:
                db.session.delete(movie)
                db.session.commit()
                return "", 201
            except Exception as s:
                return str(s), 404
        else: 
            return "Данного id не существует , либо список пуст", 404
         
    
    def put(self, uid):
        data_new = json.loads(request.data)
        data_old = Movie.query.get(uid)

        if data_new and data_old:
            try:
                data_old.title = data_new["title"]
                data_old.description = data_new["description"]
                data_old.trailer = data_new["trailer"]
                data_old.year = data_new["year"]
                data_old.rating = data_new["rating"]
                data_old.genre_id = data_new["genre_id"]
                data_old.director_id = data_new["director_id"]
        
                db.session.add(data_old)
                db.session.commit()
                return "" , 201 
            
            except Exception as s :
                return str(s) , 404
        else:
            return f"Нет такого фильма по этому id ----> {uid}, либо не ведены данные",404

    def patch(self, uid):
        data_new = json.loads(request.data)
        data_old = Movie.query.get(uid)

        if data_new and data_old:
            try:
                data_old.title = data_new["title"]

                db.session.add(data_old)
                db.session.commit()
                return "", 201
            except Exception as s:
                return str(s), 404
        else:
            return f"Нет такого фильма по этому id ----> {uid}, либо не ведены данные",404

@movies_ns.route("/") 
class MovieDirector(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")

        if director_id and genre_id:
            try:
                movie = db.session.query(Movie).filter(Movie.director_id == int(director_id), Movie.genre_id == int(genre_id)).one()
                return movie_schema.dump(movie), 200
            except Exception as s:
                return str(s), 404
        else:
            return f"Отсуствует один из них (director_id = {director_id}, genre_id = {genre_id})",404
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
@genres_ns.route("/")
class Genres(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        if genres:
            try:
                return genres_schema.dump(genres), 200
            except Exception as s:
                return str(s), 404
        else:
            return "В таблице пусто"

    def post(self):
        data = json.loads(request.data)
        if data:
            try:
                output = Genre(**data)
                db.session.add(output)
                db.session.commit()
                return "", 201
            except Exception as s:
                return str(s), 404
        else: 
            return "Не ведены данные",404

@genres_ns.route("/<uid>")
class GenresAll(Resource):
    def delete(self,uid):
        genre = Genre.query.get(uid)
        if genre:
            try:
                db.session.delete(genre)
                db.session.commit()
                return "", 204
            except Exception as s:
                return str(s), 404
        else: 
            return "Данного id не существует , либо список пуст", 404

    def get(self,uid):
        genre = Genre.query.get(uid)
        if genre:
            try:
                return genre_chema.dump(genre), 200
            except Exception as s:
                return str(s), 404
        else: 
            return "Данного id не существует , либо список пуст", 404

    def put(self,uid):
        data_new = json.loads(request.data)
        data_old = Genre.query.get(uid)

        if data_new and data_old:
            try:
                data_old.name = data_new["name"]
                db.session.add(data_old)
                db.session.commit()
                return "", 201
            except Exception as s:
                return str(s), 404
        else:
            return f"Нет такого фильма по этому id ----> {uid}, либо не ведены данные",404

    def patch(self,uid):
        data_new = json.loads(request.data)
        data_old = Genre.query.get(uid)

        if data_new and data_old:
            try:
                data_old.name = data_new["name"]
                db.session.add(data_old)
                db.session.commit()
                return "", 201
            except Exception as s:
                return str(s), 404
        else:
            return f"Нет такого фильма по этому id ----> {uid}, либо не ведены данные",404
#----------------------------------------------------------------------------------------------------------------------------------------------------------
@directors_ns.route("/")
class directors(Resource):
    def get(self):
        directors = db.session.query(Genre).all()
        if directors:
            try:
                return directors_schema.dump(directors), 200
            except Exception as s:
                return str(s), 404
        else:
            return "В таблице пусто"

    def post(self):
        data = json.loads(request.data)
        if data:
            try:
                output = Director(**data)
                db.session.add(output)
                db.session.commit()
                return "", 201
            except Exception as s:
                return str(s), 404
        else: 
            return "Не ведены данные",404

@directors_ns.route("/<uid>")
class directorsAll(Resource):
    def delete(self,uid):
        director = Director.query.get(uid)
        if director:
            try:
                db.session.delete(director)
                db.session.commit()
                return "", 204
            except Exception as s:
                return str(s), 404
        else: 
            return "Данного id не существует , либо список пуст", 404

    def get(self,uid):
        director = Director.query.get(uid)
        if director:
            try:
                return director_chema.dump(director), 200
            except Exception as s:
                return str(s), 404
        else: 
            return "Данного id не существует , либо список пуст", 404

    def put(self,uid):
        data_new = json.loads(request.data)
        data_old = Director.query.get(uid)

        if data_new and data_old:
            try:
                data_old.name = data_new["name"]
                db.session.add(data_old)
                db.session.commit()
                return "", 201
            except Exception as s:
                return str(s), 404
        else:
            return f"Нет такого фильма по этому id ----> {uid}, либо не ведены данные", 404

    def patch(self,uid):
        data_new = json.loads(request.data)
        data_old = Director.query.get(uid)

        if data_new and data_old:
            try:
                data_old.name = data_new["name"]
                db.session.add(data_old)
                db.session.commit()
                return "", 201
            except Exception as s:
                return str(s), 404
        else:
            return f"Нет такого фильма по этому id ----> {uid}, либо не ведены данные", 404

if __name__ == '__main__':
    app.run(debug=True)
