from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seeky.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    """User model for storing user information."""
    
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password: str = db.Column(db.String(120), nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    """Job model for storing job information."""
    
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(100), nullable=False)
    company: str = db.Column(db.String(100), nullable=False)
    location: str = db.Column(db.String(100), nullable=False)
    description: str = db.Column(db.Text, nullable=False)
    salary: str = db.Column(db.String(50))
    posted_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Application(db.Model):
    """Application model for storing job applications."""
    
    id: int = db.Column(db.Integer, primary_key=True)
    job_id: int = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status: str = db.Column(db.String(20), default='pending')
    applied_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/api/register', methods=['POST'])
def register() -> tuple:
    """
    Register a new user.
    
    Returns:
        tuple: JSON response and HTTP status code
    """
    data: dict = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    new_user: User = User(
        username=data['username'],
        email=data['email'],
        password=data['password']  # In production, hash the password
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login() -> tuple:
    """
    Authenticate a user.
    
    Returns:
        tuple: JSON response and HTTP status code
    """
    data: dict = request.get_json()
    user: User = User.query.filter_by(email=data['email']).first()
    
    if user and user.password == data['password']:  # In production, verify hashed password
        return jsonify({'message': 'Login successful'}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/jobs', methods=['GET'])
def get_jobs() -> tuple:
    """
    Get all jobs.
    
    Returns:
        tuple: JSON response and HTTP status code
    """
    jobs: list = Job.query.all()
    return jsonify([{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'description': job.description,
        'salary': job.salary,
        'posted_at': job.posted_at.isoformat()
    } for job in jobs]), 200

@app.route('/api/jobs', methods=['POST'])
def create_job() -> tuple:
    """
    Create a new job posting.
    
    Returns:
        tuple: JSON response and HTTP status code
    """
    data: dict = request.get_json()
    new_job: Job = Job(
        title=data['title'],
        company=data['company'],
        location=data['location'],
        description=data['description'],
        salary=data.get('salary'),
        user_id=data['user_id']
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    return jsonify({'message': 'Job created successfully'}), 201

@app.route('/api/applications', methods=['POST'])
def apply_job() -> tuple:
    """
    Apply for a job.
    
    Returns:
        tuple: JSON response and HTTP status code
    """
    data: dict = request.get_json()
    new_application: Application = Application(
        job_id=data['job_id'],
        user_id=data['user_id']
    )
    
    db.session.add(new_application)
    db.session.commit()
    
    return jsonify({'message': 'Application submitted successfully'}), 201

@app.route('/api/applications/<int:user_id>', methods=['GET'])
def get_user_applications(user_id: int) -> tuple:
    """
    Get all applications for a specific user.
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        tuple: JSON response and HTTP status code
    """
    applications: list = Application.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': app.id,
        'job_id': app.job_id,
        'status': app.status,
        'applied_at': app.applied_at.isoformat()
    } for app in applications]), 200

if __name__ == '__main__':
    app.run(debug=True) 