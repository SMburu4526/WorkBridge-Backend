from flask import Blueprint, request, jsonify
from ..models import db, Job, User
from .auth import token_required, role_required
from math import ceil
jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/api', methods=['GET'])
def get_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    jobs = Job.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'jobs': [job.to_dict() for job in jobs.items],
        'total': jobs.total,
        'pages': jobs.pages,
        'current_page': jobs.page
    }), 200

@jobs_bp.route('', methods=['POST'])
@token_required
@role_required(['Employer'])
def create_job(current_user):
    data = request.get_json()
    required_fields = ['title', 'description', 'location', 'salary', 'job_type']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    if not isinstance(data['salary'], (int, float)) or data['salary'] <= 0:
        return jsonify({'message': 'Salary must be a positive number'}), 400

    job = Job(
        title=data['title'],
        description=data['description'],
        location=data['location'],
        salary=data['salary'],
        job_type=data['job_type'],
        employer_id=current_user.id
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({'message': 'Job created successfully', 'job': job.to_dict()}), 201

@jobs_bp.route('/<int:job_id>', methods=['PATCH'])
@token_required
@role_required(['Employer'])
def update_job(current_user, job_id):
    job = Job.query.get_or_404(job_id)
    if job.employer_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    if 'salary' in data and (not isinstance(data['salary'], (int, float)) or data['salary'] <= 0):
        return jsonify({'message': 'Salary must be a positive number'}), 400

    job.title = data.get('title', job.title)
    job.description = data.get('description', job.description)
    job.location = data.get('location', job.location)
    job.salary = data.get('salary', job.salary)
    job.job_type = data.get('job_type', job.job_type)
    db.session.commit()
    return jsonify({'message': 'Job updated successfully', 'job': job.to_dict()}), 200

@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@token_required
@role_required(['Employer'])
def delete_job(current_user, job_id):
    job = Job.query.get_or_404(job_id)
    if job.employer_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403

    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job deleted successfully'}), 200
