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

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(username=username, role=role, name=full_name, phone=phone)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Account created!', 'email': username}), 201

@auth_bp.route('/login', methods=['POST'])
@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'job_seeker')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Demo mode for testing - accepts demo@test.com and employer@test.com
    if email in ['demo@test.com', 'employer@test.com'] and password == 'demo123':
        demo_role = 'employer' if email == 'employer@test.com' else 'job_seeker'
        demo_user = User.query.filter_by(username=email, role=demo_role).first()
        if not demo_user:
            demo_user = User(username=email, role=demo_role, name=f'Demo {demo_role.title()}')
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
        
        access_token = create_access_token(identity=demo_user.username, additional_claims={'role': demo_user.role, 'user_id': demo_user.id})
        return jsonify({
            'access_token': access_token, 
            'role': demo_user.role,
            'user': {
                'id': demo_user.id,
                'username': demo_user.username,
                'role': demo_user.role,
                'name': demo_user.name
            }
        }), 200
    
    # Regular user validation
    user = User.query.filter_by(username=email, role=role).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
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


@jobs_bp.route('/jobs', methods=['GET'])
@jobs_bp.route('/api/jobs', methods=['GET'])
@jobs_bp.route('/jobseekers/jobs', methods=['GET'])
def get_jobs_jobseekers():
    return get_jobs()

@jobs_bp.route('/jobseekers/jobs/<int:job_id>/apply', methods=['POST'])
@jwt_required()
def apply_job_jobseekers(job_id):
    user = get_current_user()
    if user.role != 'job_seeker':
        return jsonify({'error': 'Access denied'}), 403
    
    existing = Application.query.filter_by(job_id=job_id, user_id=user.id).first()
    if existing:
        return jsonify({'error': 'Already applied to this job'}), 400
    
    application = Application(job_id=job_id, user_id=user.id)
    db.session.add(application)
    db.session.commit()
    return jsonify({'message': 'Applied!'}), 201


@jobs_bp.route('/jobs', methods=['GET'])
@jobs_bp.route('/api/jobs', methods=['GET'])
def get_jobs():
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 6)), 50)
    
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

@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job_details(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify({
        'id': job.id,
        'title': job.title,
        'description': job.description,
        'location': job.location,
        'salary': job.salary,
        'job_type': job.job_type,
        'employer_id': job.employer_id
    })

@jobs_bp.route('/jobs', methods=['POST'])
@jwt_required()
def create_job():
    data = request.get_json()
    user = get_current_user()
    
    job = Job(
        title=data.get('title'),
        description=data.get('description'),
        location=data.get('location'),
        salary=float(data.get('salary', 0)),
        job_type=data.get('job_type', 'full-time'),
        employer_id=user.id
    )
    
    db.session.add(job)
    db.session.commit()
    
    return jsonify({'message': 'Job posted successfully!', 'job_id': job.id}), 201

@jobs_bp.route('/employer/jobs', methods=['GET'])
def get_employer_jobs():
    employer_id = 1
    jobs = Job.query.filter_by(employer_id=employer_id).all()
    
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
            'employer_name': ['Microsoft', 'Google', 'Apple', 'Netflix', 'Meta'][(job.employer_id - 1) % 5],
            'created_at': '2024-01-01T00:00:00'
        })
    
    return jsonify(result), 200

@jobs_bp.route('/employer/applications', methods=['GET'])
def get_employer_applications():
    employer_id = 1
    applications = db.session.query(Application, Job).join(Job, Application.job_id == Job.id).filter(Job.employer_id == employer_id).order_by(Application.id.desc()).all()
    
    result = []
    for app, job in applications:
        result.append({
            'id': app.id,
            'status': app.status,
            'job_id': job.id,
            'applicant_name': 'Job Seeker',
            'applicant_email': 'jobseeker@example.com',
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

@jobs_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
def update_application_status(app_id):
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['pending', 'accepted', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
    
    application = Application.query.get_or_404(app_id)
    application.status = status
    db.session.commit()
    
    return jsonify({'message': f'Application {status}'}), 200

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

@jobs_bp.route('/interviews/jobseeker', methods=['GET'])
@jwt_required()
def get_jobseeker_interviews():
    user = get_current_user()
    interviews = db.session.query(Interview, Application, Job).join(Application, Interview.application_id == Application.id).join(Job, Application.job_id == Job.id).filter(Application.user_id == user.id).all()
    
    result = []
    for interview, app, job in interviews:
        result.append({
            'id': interview.id,
            'date': interview.date,
            'time': interview.time,
            'location': interview.location,
            'notes': interview.notes,
            'job': {
                'title': job.title,
                'location': job.location,
                'employer_name': ['Microsoft', 'Google', 'Apple', 'Netflix', 'Meta'][(job.employer_id - 1) % 5]
            }
        })
    
    return jsonify(result), 200


@applications_bp.route('/', methods=['POST'])
@jobs_bp.route('/applications', methods=['POST'])
def apply_for_job():
    data = request.get_json()
    job_id = data.get('job_id')
    user_id = 15
    
    existing = Application.query.filter_by(job_id=job_id, user_id=user_id).first()
    if existing:
        return jsonify({'error': 'Already applied'}), 400
    
    application = Application(job_id=job_id, user_id=user_id)
    db.session.add(application)
    db.session.commit()
    return jsonify({'message': 'Applied!'}), 201

@applications_bp.route('/applications/my-applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    user = get_current_user()
    if user.role != 'job_seeker':
        return jsonify({'error': 'Access denied'}), 403
    
    applications = db.session.query(Application, Job).join(Job, Application.job_id == Job.id).filter(Application.user_id == user.id).all()
    
    result = []
    for app, job in applications:
        result.append({
            'id': app.id,
            'status': app.status,
            'job': {
                'id': job.id,
                'title': job.title,
                'location': job.location,
                'job_type': job.job_type,
                'salary': job.salary
            }
        })
    
    return jsonify(result), 200




@jobs_bp.route('/profile', methods=['GET'])
@jobs_bp.route('/jobseekers/me', methods=['GET'])
@jwt_required()
def get_profile():
    user = get_current_user()
    return jsonify({
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'name': user.name,
        'phone': user.phone,
        'location': user.location,
        'skills': user.skills,
        'experience': user.experience,
        'resume_url': user.resume_url
    })

@jobs_bp.route('/profile', methods=['POST', 'PUT'])
@jobs_bp.route('/jobseekers/me', methods=['POST', 'PUT'])
@jwt_required()
def update_profile():
    user = get_current_user()
    data = request.get_json()
    
    user.name = data.get('name', user.name)
    user.phone = data.get('phone', user.phone)
    user.location = data.get('location', user.location)
    user.skills = data.get('skills', user.skills)
    user.experience = data.get('experience', user.experience)
    user.resume_url = data.get('resume_url', user.resume_url)
    
    db.session.commit()
    return jsonify({'message': 'Profile updated'}), 200


@jobs_bp.route('/applications/', methods=['GET'])
def get_applications():
    user_id = 15
    applications = db.session.query(Application, Job).join(Job, Application.job_id == Job.id).filter(Application.user_id == user_id).order_by(Application.id.desc()).all()
    
    result = []
    for app, job in applications:
        result.append({
            'id': app.id,
            'status': app.status,
            'job_id': job.id,
            'job': {
                'id': job.id,
                'title': job.title,
                'location': job.location,
                'job_type': job.job_type,
                'salary': job.salary,
                'salary_range': f'${job.salary:,.0f}',
                'description': job.description,
                'employer_name': ['Microsoft', 'Google', 'Apple', 'Netflix', 'Meta'][(job.employer_id - 1) % 5]
            }
        })
    
    return jsonify(result), 200

@jobs_bp.route('/applications/<int:job_id>', methods=['DELETE'])
def remove_application(job_id):
    user_id = 15
    application = Application.query.filter_by(job_id=job_id, user_id=user_id).first()
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    db.session.delete(application)
    db.session.commit()
    return jsonify({'message': 'Removed'}), 200


