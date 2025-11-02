from models import db, Job
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    Job.query.delete()
    
    jobs = [
        Job(title='Senior Software Engineer', description='Build scalable web applications using React and Node.js', location='Seattle, WA', salary=150000, job_type='full-time', employer_id=1),
        Job(title='Product Manager', description='Lead product strategy and roadmap for enterprise software', location='San Francisco, CA', salary=140000, job_type='full-time', employer_id=2),
        Job(title='Data Scientist', description='Analyze large datasets and build machine learning models', location='New York, NY', salary=160000, job_type='full-time', employer_id=3),
        Job(title='UX Designer', description='Design intuitive user experiences for mobile and web applications', location='Austin, TX', salary=110000, job_type='full-time', employer_id=4),
        Job(title='DevOps Engineer', description='Manage cloud infrastructure and deployment pipelines', location='Remote', salary=130000, job_type='full-time', employer_id=5),
        Job(title='Mobile Developer', description='Develop native iOS and Android applications', location='Los Angeles, CA', salary=125000, job_type='full-time', employer_id=1),
        Job(title='Backend Engineer', description='Design and implement REST APIs and microservices', location='Boston, MA', salary=135000, job_type='full-time', employer_id=2),
    ]
    
    db.session.add_all(jobs)
    db.session.commit()
    
    print("Reset to 7 unique jobs:")
    for job in Job.query.all():
        print(f"- {job.title} in {job.location} (${job.salary:,})")