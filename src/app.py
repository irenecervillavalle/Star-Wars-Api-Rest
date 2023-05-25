"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, FavoritePlanet, FavoritePeople
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_hello():

    users_all = User.query.all()
    users_all = list(map(lambda x: x.serialize(), users_all))

    return jsonify(users_all), 200

# Get All People
@app.route('/people', methods=['GET'])
def get_people():

    all_people = People.query.all()
    all_people = list(map(lambda x: x.serialize(), all_people))

    response_body = {
        "msg": "Get all people"
    }

    return jsonify(all_people), 200


##Get All Favorite User
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    # Asegúrate de que el usuario exista.
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    favorite_planets = [favorite_planet.serialize() for favorite_planet in user.favorite_planets]
    favorite_people = [favorite_people.serialize() for favorite_people in user.favorite_people]

    return jsonify({
        'favorite_planets': favorite_planets,
        'favorite_people': favorite_people,
    }), 200
    

# Get One People By id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    print(people_id)
    people = People.query.get(people_id)
    if people is None:
        raise APIException("People noy found", status_code=404)

    return jsonify(people.serialize()), 200


# Get All Planets
@app.route('/planets', methods=['GET'])
def get_planets():

    all_planets = Planets.query.all()
    all_planets = list(map(lambda x: x.serialize(), all_planets))

    return jsonify(all_planets), 200

# Get One Planets By id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planets.query.get(planet_id)
    if planet is None:
        raise APIException("Planet noy found", status_code=404)

    return jsonify(planet.serialize()), 200

## Delete Planet Favorite
@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    # Asegúrate de que el planeta exista.
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'message': 'Planet not found'}), 404

    # Asegúrate de que el usuario exista.
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Comprueba si el usuario ya ha agregado este planeta como favorito.
    favorite = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        return jsonify({'message': 'Planet already added as favorite'}), 400

    # Crea una nueva relación de favorito y guárdala en la base de datos.
    new_favorite = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201


## Add People Favorite
@app.route('/favorite/user/<int:user_id>/people/<int:people_id>', methods=['POST'])
def add_favorite_people(user_id, people_id):
    # Asegúrate de que el planeta exista.
    people = People.query.get(people_id)
    if not people:
        return jsonify({'message': 'People not found'}), 404

    # Asegúrate de que el usuario exista.
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Comprueba si el usuario ya ha agregado esta persona como favorito.
    favorite = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite:
        return jsonify({'message': 'People already added as favorite'}), 400

    # Crea una nueva relación de favorito y guárdala en la base de datos.
    new_favorite = FavoritePeople(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201    


## Delete Planet Favorite
@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    # Asegúrate de que el planeta exista.
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'message': 'Planet not found'}), 404

    # Aquí debes validar el usuario actual. Estoy asumiendo que tienes un método para obtener el usuario actual.
    # Por ejemplo, puede que necesites algo como esto:
    # current_user = get_current_user()
    # Si no tienes un método así, necesitarás implementarlo.

    # Encuentra la entrada favorita en la base de datos.
    favorite = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({'message': 'Favorite not found'}), 404

    # Elimina la entrada de la base de datos.
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'message': 'Favorite Planet deleted'}), 200


## Delete People Favorite
@app.route('/favorite/user/<int:user_id>/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(user_id, people_id):
    # Asegúrate de que el planeta exista.
    people = People.query.get(people_id)
    if not people:
        return jsonify({'message': 'Planet not found'}), 404

    # Aquí debes validar el usuario actual. Estoy asumiendo que tienes un método para obtener el usuario actual.
    # Por ejemplo, puede que necesites algo como esto:
    # current_user = get_current_user()
    # Si no tienes un método así, necesitarás implementarlo.

    # Encuentra la entrada favorita en la base de datos.
    favorite = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({'message': 'Favorite not found'}), 404

    # Elimina la entrada de la base de datos.
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'message': 'Favorite People deleted'}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
