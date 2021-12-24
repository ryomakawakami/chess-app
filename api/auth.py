from flask import request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required)
from flask_restx import Namespace, Resource, fields
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, Stats

auth_ns = Namespace('auth', description='A namespace for authentication.')

signup_model = auth_ns.model('Signup', {
    'username': fields.String(),
    'email': fields.String(),
    'password': fields.String()
})

login_model = auth_ns.model('Login', {
    'username': fields.String(),
    'password': fields.String()
})

@auth_ns.route('/signup')
class Signup(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        data = request.get_json()

        username = data.get('username')
        db_user = User.query.filter_by(username=username).first()
        if db_user is not None:
            return {
                'message': f'User with name {username} already exists.'
            }

        user = User(
            username=username,
            email=data.get('email'),
            password=generate_password_hash(data.get('password'))
        )
        user.save()

        stats = Stats(username=username)
        stats.save()

        return {
            'message': 'User created successfully.'
        }, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        db_user = User.query.filter_by(username=username).first()
        if db_user and check_password_hash(db_user.password, password):
            access_token = create_access_token(identity=db_user.username)
            refresh_token = create_refresh_token(identity=db_user.username)

            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 201

@auth_ns.route('/refresh')
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {
            'access_token': access_token
        }, 201
