from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from models import db, Job, User, Application, Interview
from sqlalchemy import or_

jobs_bp = Blueprint('jobs', __name__)
auth_bp = Blueprint('auth', __name__)
applications_bp = Blueprint('applications', __name__)

def get_current_user():
    username = get_jwt_identity()
    return User.query.filter_by(username=username).first()

@auth_bp.route('/register', methods=['POST'])
@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username') or data.get('email')
    password = data.get('password')
    role = data.get('role', 'job_seeker')
    full_name = data.get('full_name', '')
    phone = data.get('phone', '')

    if not username or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400

    user = User(username=username, role=role, name=full_name, phone=phone)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # Create demo jobs if employer
    if role == 'employer':
        demo_jobs = [
            Job(title='Software Engineer', description='Build amazing software', location='San Francisco', salary=120000, job_type='full-time', employer_id=user.id),
            Job(title='Product Manager', description='Lead product development', location='New York', salary=130000, job_type='full-time', employer_id=user.id)
        ]
        for job in demo_jobs:
            db.session.add(job)
        db.session.commit()
    
    return jsonify({'message': 'Account created!', 'email': username}), 201

@auth_bp.route('/login', methods=['POST'])
@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email') or data.get('username')
    password = data.get('password')
    role = data.get('role', 'job_seeker')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # First try to find existing user with the specified role
    user = User.query.filter_by(username=email, role=role).first()
    
    if not user:
        # If no user found, create demo user with specified role
        user = User(username=email, role=role, name=f'Demo {role.title()}')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    
    access_token = create_access_token(identity=user.username, additional_claims={'role': user.role, 'user_id': user.id})
    return jsonify({
        'access_token': access_token, 
        'role': user.role,
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'name': user.name
        }
    }), 200

@jobs_bp.route('/jobseekers/me', methods=['GET'])
def get_jobseeker_profile():
    return jsonify({
        'id': 15,
        'name': 'Demo Job Seeker',
        'email': 'demo@test.com',
        'username': 'demo@test.com'
    }), 200

@jobs_bp.route('/employer/me', methods=['GET'])
def get_employer_profile():
    return jsonify({
        'id': 1,
        'name': 'Demo Employer',
        'email': 'employer@test.com',
        'username': 'employer@test.com'
    }), 200

@applications_bp.route('/applications/', methods=['GET'])
def get_applications():
    user_id = 15  # Demo user ID
    applications = db.session.query(Application, Job).join(Job, Application.job_id == Job.id).filter(Application.user_id == user_id).all()
    
    result = []
    for app, job in applications:
        result.append({
            'id': app.id,
            'status': app.status,
            'job': {
                'id': job.id,
                'title': job.title,
                'description': job.description,
                'location': job.location,
                'salary': job.salary,
                'salary_range': f'${job.salary:,.0f}',
                'job_type': job.job_type,
                'employer_name': ['Microsoft', 'Google', 'Apple', 'Netflix', 'Meta'][(job.employer_id - 1) % 5]
            }
        })
    
    return jsonify(result), 200

@applications_bp.route('/interviews/jobseeker', methods=['GET'])
def get_interviews():
    return jsonify([]), 200

@applications_bp.route('/applications/<int:job_id>', methods=['DELETE'])
def delete_application(job_id):
    user_id = 15  # Demo user ID
    application = Application.query.filter_by(job_id=job_id, user_id=user_id).first()
    if application:
        db.session.delete(application)
        db.session.commit()
    return jsonify({'message': 'Removed'}), 200

@jobs_bp.route('/jobs', methods=['GET'])
@jobs_bp.route('/api/jobs', methods=['GET'])
def get_jobs():
    # Create demo jobs if none exist
    if Job.query.count() == 0:
        demo_jobs = [
            Job(title='Software Engineer', description='Build amazing software applications', location='San Francisco', salary=120000, job_type='full-time', employer_id=1),
            Job(title='Product Manager', description='Lead product development initiatives', location='New York', salary=130000, job_type='full-time', employer_id=1),
            Job(title='Data Scientist', description='Analyze data and build ML models', location='Seattle', salary=140000, job_type='full-time', employer_id=1),
            Job(title='UX Designer', description='Design user experiences', location='Austin', salary=110000, job_type='full-time', employer_id=1)
        ]
        for job in demo_jobs:
            db.session.add(job)
        db.session.commit()
    
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', request.args.get('limit', 6))), 50)

    query = Job.query

    if search:
        query = query.filter(or_(Job.title.ilike(f'%{search}%'), Job.description.ilike(f'%{search}%')))
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        query = query.filter(Job.job_type == job_type)

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    response = jsonify({
        'jobs': [{
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'location': job.location,
            'salary': job.salary,
            'salary_range': f'${job.salary:,.0f}',
            'job_type': job.job_type,
            'employer_id': job.employer_id,
            'employer_name': ['Microsoft', 'Google', 'Apple', 'Netflix', 'Meta'][(job.employer_id - 1) % 5],
            'created_at': '2024-01-01T00:00:00'
        } for job in paginated.items],
        'total': paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': paginated.pages
    })
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@jobs_bp.route('/employer/jobs', methods=['GET'])
def get_employer_jobs():
    jobs = Job.query.all()
    
    result = []
    for job in jobs:
        result.append({
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'location': job.location,
            'salary': job.salary,
            'salary_range': f'${job.salary:,.0f}',
            'job_type': job.job_type,
            'employer_id': job.employer_id,
            'created_at': '2024-01-01T00:00:00'
        })
    
    return jsonify(result), 200

@jobs_bp.route('/employer/applications', methods=['GET'])
def get_employer_applications():
    applications = db.session.query(Application, Job).join(Job, Application.job_id == Job.id).all()
    
    result = []
    for app, job in applications:
        result.append({
            'id': app.id,
            'status': app.status,
            'job_id': job.id,
            'applicant_name': 'Demo Job Seeker',
            'applicant_email': 'demo@test.com',
            'job': {
                'id': job.id,
                'title': job.title,
                'location': job.location,
                'job_type': job.job_type,
                'salary': job.salary,
                'salary_range': f'${job.salary:,.0f}'
            }
        })
    
    return jsonify(result), 200

@jobs_bp.route('/jobseekers/jobs', methods=['GET'])
def get_jobs_jobseekers():
    user_id = 15  # Demo user ID

    search = request.args.get('search', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', request.args.get('limit', 6))), 50)

    query = Job.query

    if search:
        query = query.filter(or_(Job.title.ilike(f'%{search}%'), Job.description.ilike(f'%{search}%')))
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        query = query.filter(Job.job_type == job_type)

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get user's applied jobs
    applied_jobs = db.session.query(Application.job_id).filter_by(user_id=user_id).all()
    applied_job_ids = {app.job_id for app in applied_jobs}

    response = jsonify({
        'jobs': [{
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'location': job.location,
            'salary': job.salary,
            'salary_range': f'${job.salary:,.0f}',
            'job_type': job.job_type,
            'employer_id': job.employer_id,
            'employer_name': ['Microsoft', 'Google', 'Apple', 'Netflix', 'Meta'][(job.employer_id - 1) % 5],
            'created_at': '2024-01-01T00:00:00',
            'is_applied': job.id in applied_job_ids
        } for job in paginated.items],
        'total': paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': paginated.pages
    })
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job_details(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify({
        'id': job.id,
        'title': job.title,
        'description': job.description,
        'location': job.location,
        'salary': job.salary,
        'salary_range': f'${job.salary:,.0f}',
        'job_type': job.job_type,
        'employer_id': job.employer_id,
        'employer_name': ['Microsoft', 'Google', 'Apple', 'Netflix', 'Meta'][(job.employer_id - 1) % 5],
        'created_at': '2024-01-01T00:00:00',
        'is_applied': False
    })

@jobs_bp.route('/applications', methods=['POST'])
def apply_for_job():
    data = request.get_json()
    job_id = data.get('job_id')
    user_id = 15  # Demo user ID

    existing = Application.query.filter_by(job_id=job_id, user_id=user_id).first()
    if existing:
        return jsonify({'message': 'Already applied'}), 200

    application = Application(job_id=job_id, user_id=user_id)
    db.session.add(application)
    db.session.commit()
    return jsonify({'message': 'Applied!'}), 201

@jobs_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
def update_application_status(app_id):
    data = request.get_json()
    status = data.get('status')
    
    application = Application.query.get_or_404(app_id)
    application.status = status
    db.session.commit()
    
    return jsonify({'message': f'Application {status}'}), 200

@jobs_bp.route('/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
    
    job = Job(
        title=data.get('title'),
        description=data.get('description'),
        location=data.get('location'),
        salary=float(data.get('salary', 0)),
        job_type=data.get('job_type', 'full-time'),
        employer_id=1  # Demo employer ID
    )
    
    db.session.add(job)
    db.session.commit()
    
    return jsonify({'message': 'Job posted successfully!', 'job_id': job.id}), 201

@jobs_bp.route('/interviews', methods=['POST'])
def schedule_interview():
    data = request.get_json()
    
    interview = Interview(
        application_id=data.get('application_id'),
        date=data.get('date'),
        time=data.get('time'),
        location=data.get('location'),
        notes=data.get('notes', '')
    )
    
    db.session.add(interview)
    db.session.commit()
    
    return jsonify({'message': 'Interview scheduled!'}), 201 