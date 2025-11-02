from flask import Blueprint, request, jsonify
from ..models import db, User
from .auth import token_required, role_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods=['PATCH'])
@token_required
@role_required(['JobSeeker'])
def update_user(current_user, user_id):
    if current_user.id != user_id:
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    user = User.query.get_or_404(user_id)

    # Update allowed fields
    if 'name' in data:
        user.name = data['name']
    if 'skills' in data:
        user.skills = data['skills']
    if 'experience' in data:
        user.experience = data['experience']

    db.session.commit()
    return jsonify({'message': 'User updated successfully', 'user': user.to_dict()}), 200
