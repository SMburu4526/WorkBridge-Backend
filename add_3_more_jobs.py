from models import db, Job
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():

    new_jobs = [
        Job(title='Security Engineer', description='Implement security protocols and conduct vulnerability assessments', location='Washington, DC', salary=145000, job_type='full-time', employer_id=1),
        Job(title='Machine Learning Engineer', description='Deploy ML models and optimize algorithms at scale', location='Palo Alto, CA', salary=170000, job_type='full-time', employer_id=1),
        Job(title='Frontend Developer', description='Create responsive web interfaces using React and TypeScript', location='Miami, FL', salary=115000, job_type='full-time', employer_id=1),
    ]
    
    db.session.add_all(new_jobs)
    db.session.commit()
    
    print(f"Now have {Job.query.count()} total jobs:")
    for job in Job.query.all():
        print(f"- {job.title} in {job.location} (${job.salary:,})")