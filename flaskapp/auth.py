from flask import Blueprint, json, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from .database.models.user import User, WhiteListToken
from .database.models import db
import jwt
import datetime
from flaskapp import app
import re

auth = Blueprint('auth', __name__)


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        data = jwt.decode(token,  app.config.get(
            "SECRET_KEY"), algorithms='HS256')

        try:
            current_user: User = User.query.filter_by(id=data['sub']).first()
            is_white_listed_token = current_user.decode_auth_token(token)

            if is_white_listed_token == 'Token is not in whitelistedToken table':
                return jsonify({"message": "Token is not whitelisted"}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return func(current_user, *args, **kwargs)
    return decorated


# @auth.route('/hello', methods=['POST', 'GET'])
# def hello():
#     return {"message": "hello"}


@auth.route('/register', methods=['POST'])
def register():
    # get post data
    data = request.get_json()
    # check if user already exists
    user = User.query.filter_by(username=data.get('email')).first()
    if not user:
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{12,}$"
        password = data['password']

        pattern = re.compile(reg)
        match = re.search(pattern, password)

        if not match:
            return make_response({"message": "password should have uppercase, lowercase, digit and special character"}), 401
        try:
            hashed_password = generate_password_hash(
                data['password'], method='sha256')
            user = User(
                username=data['username'],
                password=hashed_password
            )
            # insert user
            db.session.add(user)
            db.session.commit()
            # generte the auth token
            auth_token = user.encode_auth_token(user.id)
            responseObject = {
                'message': 'Registration Completed',
                'access_token': auth_token
            }
            return make_response(jsonify(responseObject)), 201
        except Exception as e:
            print("the error is: ", e)
            message = ""
            if str(e).find('duplicate'):
                message = 'Unique key constraint invalidated'
            else:
                message = "maybe not respecting table rules? working on errors..."
            print(message)
            responseObject = {
                'message': message
            }
            return make_response(jsonify(responseObject)), 401
    else:
        responseObject = {
            'message': 'Some error occured'
        }
        return make_response(jsonify(responseObject)), 202


@auth.route('/login', methods=['POST'])
def login():
    # auth data
    auth = request.get_json()
    username = auth['username']
    password = auth['password']

    try:

        user: User = User.query.filter_by(
            username=username
        ).first()
        if user and check_password_hash(
            user.password, password=password
        ):
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                responseObject = {
                    'message': 'Succesfully logged in.',
                    'access_token': auth_token
                }
                return make_response(jsonify(responseObject)), 200
        else:
            responseObject = {
                'message': 'User does not exist'
            }
            return make_response(jsonify(responseObject)), 404
    except Exception as e:
        print(e)
        responseObject = {
            "message": "Woor just happened"
        }
        return make_response(jsonify(responseObject)), 500


@auth.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    auth_token = request.headers['x-access-token']
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            try:
                # also have to remove the whitelisted token from database
                WhiteListToken.query.filter_by(token=auth_token).delete()
                db.session.commit()
                responseObject = {
                    'message': 'Logging out'
                }
                return make_response(jsonify(responseObject)), 200
            except Exception as e:
                responseObject = {
                    'message': e
                }
                return make_response(jsonify(responseObject)), 400
        else:
            responseObject = {
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
    else:
        responseObject = {
            'message': 'non valid auth token'
        }

        return make_response(jsonify(responseObject)), 403


@auth.route('/secure', methods=['GET'])
@token_required
def secure(current_user):
    return jsonify({"message": "Success"})

# supersecret needs to be enviorment variable
