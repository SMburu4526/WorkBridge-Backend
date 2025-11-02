from app.extensions import db
from app.models import User, Job, Application
from app import create_app

def seed_data():
    app = create_app()
    with app.app_context():

        db.drop_all()
        db.create_all()


        admin = User(
            role='Admin',
            email='admin@workbridge.com',
            name='Admin User',
            skills='Leadership, Management',
            experience='5 years as HR Manager'
        )
        admin.set_password('admin123')

        employer1 = User(
            role='Employer',
            email='employer1@company.com',
            name='TechCorp Ltd',
            skills='Hiring, Team Management',
            experience='10 years running TechCorp'
        )
        employer1.set_password('employer123')

        employer2 = User(
            role='Employer',
            email='employer2@company.com',
            name='HealthPlus Inc',
            skills='Healthcare Recruitment',
            experience='8 years running HealthPlus'
        )
        employer2.set_password('employer123')

        jobseeker1 = User(
            role='JobSeeker',
            email='seeker1@email.com',
            name='Alice Johnson',
            skills='Python, Flask, SQL',
            experience='2 years as a backend developer'
        )
        jobseeker1.set_password('password123')

        jobseeker2 = User(
            role='JobSeeker',
            email='seeker2@email.com',
            name='Brian Smith',
            skills='React, Tailwind, UI Design',
            experience='3 years as frontend developer'
        )
        jobseeker2.set_password('password123')

        db.session.add_all([admin, employer1, employer2, jobseeker1, jobseeker2])
        db.session.commit()


        job1 = Job(
            title='Backend Developer',
            description='Develop RESTful APIs using Flask and PostgreSQL.',
            location='Nairobi, Kenya',
            salary=120000,
            job_type='Full-time',
            employer_id=employer1.id
        )

        job2 = Job(
            title='Frontend Developer',
            description='Build responsive React apps with Tailwind CSS.',
            location='Mombasa, Kenya',
            salary=110000,
            job_type='Remote',
            employer_id=employer2.id
        )

        job3 = Job(
            title='UI/UX Designer',
            description='Design modern, user-friendly interfaces for mobile and web apps.',
            location='Nakuru, Kenya',
            salary=90000,
            job_type='Part-time',
            employer_id=employer2.id
        )

        db.session.add_all([job1, job2, job3])
        db.session.commit()


        application1 = Application(
            job_id=job1.id,
            user_id=jobseeker1.id,
            status='pending'
        )

        application2 = Application(
            job_id=job2.id,
            user_id=jobseeker2.id,
            status='pending'
        )

        application3 = Application(
            job_id=job3.id,
            user_id=jobseeker1.id,
            status='pending'
        )

        db.session.add_all([application1, application2, application3])
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
