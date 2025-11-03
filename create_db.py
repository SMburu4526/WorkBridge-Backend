from models import db, User, Job, Application
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    

    employer = User(username='employer1', role='employer', name='John Employer')
    employer.set_password('password123')
    
    seeker = User(username='seeker1', role='job_seeker', name='Jane Seeker')
    seeker.set_password('password123')
    
    db.session.add_all([employer, seeker])
    db.session.commit()
    

    jobs = [
        Job(title='Software Engineer', description='Develop web applications', location='New York', salary=80000, job_type='full-time', employer_id=employer.id),
        Job(title='Data Analyst', description='Analyze business data', location='San Francisco', salary=70000, job_type='full-time', employer_id=employer.id),
        Job(title='UI Designer', description='Design user interfaces', location='Remote', salary=60000, job_type='part-time', employer_id=employer.id)
    ]
    
    db.session.add_all(jobs)
    db.session.commit()
    
    print("Database created successfully!")
    print("Demo users:")
    print("- employer1 / password123 (employer)")
    print("- seeker1 / password123 (job_seeker)")