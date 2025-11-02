from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
import jwt
import datetime
from ..models import db, User
from functools import wraps
import os

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(" ")[1]  # Bearer token
            data = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'message': 'Access denied!'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password', 'name', 'role')):
        return jsonify({'message': 'Missing required fields'}), 400

    if data['role'] not in ['Admin', 'Employer', 'JobSeeker']:
        return jsonify({'message': 'Invalid role'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(
        email=data['email'],
        name=data['name'],
        role=data['role'],
        skills=data.get('skills'),
        experience=data.get('experience')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, os.getenv('JWT_SECRET_KEY'), algorithm="HS256")

    return jsonify({'token': token, 'user': user.to_dict()}), 200
