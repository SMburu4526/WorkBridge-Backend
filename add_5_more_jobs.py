from models import db, Job
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():

    new_jobs = [
        Job(title='Cloud Architect', description='Design and implement cloud infrastructure solutions', location='Denver, CO', salary=165000, job_type='full-time', employer_id=1),
        Job(title='QA Engineer', description='Develop automated testing frameworks and ensure quality', location='Portland, OR', salary=105000, job_type='full-time', employer_id=1),
        Job(title='Technical Writer', description='Create documentation for APIs and developer tools', location='Remote', salary=95000, job_type='full-time', employer_id=1),
        Job(title='Sales Engineer', description='Support technical sales and customer implementations', location='Chicago, IL', salary=120000, job_type='full-time', employer_id=1),
        Job(title='Site Reliability Engineer', description='Maintain system reliability and performance monitoring', location='Atlanta, GA', salary=155000, job_type='full-time', employer_id=1),
    ]
    
    db.session.add_all(new_jobs)
    db.session.commit()
    
    print(f"Now have {Job.query.count()} total jobs")
    print("All jobs available:")