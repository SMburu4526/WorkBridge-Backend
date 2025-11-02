from models import db, Job, User
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():

    new_jobs = [
        Job(title='Senior Software Engineer', description='Build scalable cloud applications using React and Node.js', location='Seattle, WA', salary=150000, job_type='full-time', employer_id=1),
        Job(title='Product Manager', description='Lead product strategy for Microsoft Teams', location='Redmond, WA', salary=140000, job_type='full-time', employer_id=1),
        Job(title='Data Scientist', description='Analyze user behavior and build ML models', location='San Francisco, CA', salary=160000, job_type='full-time', employer_id=1),
        Job(title='Frontend Developer', description='Create beautiful user interfaces with React', location='Austin, TX', salary=120000, job_type='full-time', employer_id=1),
        Job(title='DevOps Engineer', description='Manage cloud infrastructure and CI/CD pipelines', location='Remote', salary=130000, job_type='full-time', employer_id=1),
        Job(title='Mobile Developer', description='Build iOS and Android applications', location='Cupertino, CA', salary=145000, job_type='full-time', employer_id=1),
        Job(title='Backend Engineer', description='Design and implement REST APIs', location='Mountain View, CA', salary=155000, job_type='full-time', employer_id=1),
        Job(title='UX Designer', description='Design user experiences for web and mobile', location='New York, NY', salary=110000, job_type='full-time', employer_id=1),
        Job(title='Security Engineer', description='Implement security measures and conduct audits', location='Washington, DC', salary=165000, job_type='full-time', employer_id=1),
        Job(title='Machine Learning Engineer', description='Deploy ML models at scale', location='Palo Alto, CA', salary=170000, job_type='full-time', employer_id=1),
    ]
    
    db.session.add_all(new_jobs)
    db.session.commit()
    
    print("Added 10 new jobs successfully!")
    print("Jobs now available:")
    for job in Job.query.all():
        print(f"- {job.title} at {job.location} (${job.salary:,})")