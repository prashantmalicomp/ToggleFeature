

from flask import Flask, request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from app.models import User
from app.models import db
from app.users.serde import UserSchema

users_blueprint = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@users_blueprint.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return UserSchema(many=True).jsonify(users), 200

@users_blueprint.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}, 404
    return UserSchema().jsonify(user), 200


# Define API endpoints within the Blueprint
@users_blueprint.route('/users', methods=['POST'])
def create_user():
    try:
        data = UserSchema().load(request.json)
        user = User(**data)
        db.session.add(user)
        db.session.commit()
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    except IntegrityError as err:
        return jsonify({'error': str(err.orig)}), 400
    except Exception as err:
        return jsonify({'error': str(err)}), 400

    return UserSchema().jsonify(user), 201


