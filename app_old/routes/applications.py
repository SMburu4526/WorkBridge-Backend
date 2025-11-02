from flask import Blueprint, request, jsonify
from ..models import db, Application, Job
from .auth import token_required, role_required

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/<int:job_id>/apply', methods=['POST'])
@token_required
@role_required(['JobSeeker'])
def apply_for_job(current_user, job_id):
    job = Job.query.get_or_404(job_id)
    # Check if already applied
    existing_app = Application.query.filter_by(user_id=current_user.id, job_id=job_id).first()
    if existing_app:
        return jsonify({'message': 'Already applied for this job'}), 400

    application = Application(job_id=job_id, user_id=current_user.id)
    db.session.add(application)
    db.session.commit()
    return jsonify({'message': 'Application submitted successfully', 'application': application.to_dict()}), 201

@applications_bp.route('', methods=['GET'])
@token_required
@role_required(['JobSeeker'])
def get_user_applications(current_user):
    applications = Application.query.filter_by(user_id=current_user.id).all()
    return jsonify({'applications': [app.to_dict() for app in applications]}), 200

@applications_bp.route('/<int:app_id>', methods=['PATCH'])
@token_required
@role_required(['Employer'])
def update_application_status(current_user, app_id):
    application = Application.query.get_or_404(app_id)
    job = Job.query.get(application.job_id)
    if job.employer_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    if 'status' not in data or data['status'] not in ['pending', 'accepted', 'rejected']:
        return jsonify({'message': 'Invalid status'}), 400

    application.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Application status updated', 'application': application.to_dict()}), 200
