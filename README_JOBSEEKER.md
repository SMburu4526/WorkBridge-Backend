WorkBridge Job Seeker Features

Quick Start

1. Setup Database:
   python create_db.py

2. Run Server:
   python app.py

3. Test API:
   python test_api.py

4. Demo Frontend:
   Open demo.html in browser

Demo Credentials
- Job Seeker: seeker1 / password123
- Employer: employer1 / password123

API Endpoints

Authentication
- POST /api/login - Login user
- POST /api/register - Register new user

Jobs
- GET /api/jobs - List jobs with search/filters
- GET /api/jobs/{id} - Get job details

Applications
- POST /api/applications - Apply for job
- GET /api/applications/my-applications - Track applications

Profile
- GET /api/profile - Get user profile
- POST /api/profile - Update profile

Features Implemented

1. Job Listings Page - Search, filter, pagination
2. Job Details Page - Full job information
3. Apply Button - One-click job applications
4. Application Tracker - View application status
5. Profile Management - Edit personal information

Search & Filters
- Text search in title/description
- Location filter
- Job type filter (full-time, part-time)
- Pagination support

Database Schema
- User - Authentication and profile data
- Job - Job postings
- Application - Job applications with status

All features are working and tested!