"""
Flask Web Application
AI E-Learning Analytics Platform
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
import pandas as pd
import numpy as np
import json
import os
import sys
import random
from copy import deepcopy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId

BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Frontend'))

# Add src to path
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from src.predict import StudentPredictor

app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, 'templates'),
    static_folder=os.path.join(FRONTEND_DIR, 'static'),
    static_url_path='/static'
)
app.config['SECRET_KEY'] = 'ai-elearning-analytics-2026'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Database configuration (MongoDB)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'elearning_analytics')
MONGO_USERS_COLLECTION = 'users'
MONGO_COURSE_ENROLLMENTS_COLLECTION = 'course_enrollments'

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]

# Global predictor instance
predictor = None


def init_db():
    """Initialize the database"""
    try:
        users = mongo_db[MONGO_USERS_COLLECTION]
        users.create_index('email', unique=True)
        enrollments = mongo_db[MONGO_COURSE_ENROLLMENTS_COLLECTION]
        enrollments.create_index([('user_id', 1), ('course_name', 1)], unique=True)
        print(f"MongoDB initialized/verified at {MONGO_URI}/{MONGO_DB_NAME}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()


def login_required(f):
    """Decorator to protect routes that require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print(f"Access denied to {request.endpoint} - user not logged in")
            return redirect(url_for('login'))
        print(f"Access granted to {request.endpoint} - user_id: {session['user_id']}")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to protect routes that require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print(f"Access denied to {request.endpoint} - user not logged in")
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            print(f"Access denied to {request.endpoint} - user is not admin")
            return render_template('403.html', message="Admin access required"), 403
        
        print(f"Admin access granted to {request.endpoint} - admin_id: {session['user_id']}")
        return f(*args, **kwargs)
    return decorated_function


def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        user = mongo_db[MONGO_USERS_COLLECTION].find_one(
            {'_id': ObjectId(user_id)},
            {'name': 1, 'email': 1}
        )
        if user is None:
            return None
        return (str(user['_id']), user.get('name'), user.get('email'))
    except Exception:
        return None


def initialize_predictor():
    """Initialize the predictor on first request"""
    global predictor
    if predictor is None:
        try:
            predictor = StudentPredictor()
            predictor.load_model()
            predictor.load_scaler()
            print("Predictor initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize predictor: {e}")
            print("Please train the model first by running: python src/train.py")


def load_data():
    """Load processed student data"""
    data_path = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.csv')
    if os.path.exists(data_path):
        return pd.read_csv(data_path)
    else:
        # Fall back to raw data
        raw_path = os.path.join(BASE_DIR, 'data', 'raw', 'student_activity.csv')
        if os.path.exists(raw_path):
            return pd.read_csv(raw_path)
        return None


def load_predictions():
    """Load saved predictions"""
    pred_path = os.path.join(BASE_DIR, 'outputs', 'predictions', 'results.csv')
    if os.path.exists(pred_path):
        return pd.read_csv(pred_path)
    return None


def load_training_summary():
    """Load training summary"""
    summary_path = os.path.join(BASE_DIR, 'outputs', 'training_summary.json')
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            return json.load(f)
    return None


def build_data_preview(df, max_rows=None, max_cols=None):
    """Build a JSON-serializable dataset payload for Data Management tables."""
    if df is None or df.empty:
        return {
            'columns': [],
            'rows': [],
            'total_rows': 0,
            'total_columns': 0
        }

    preview_df = df.copy() if max_rows is None else df.head(max_rows).copy()
    selected_columns = preview_df.columns if max_cols is None else preview_df.columns[:max_cols]
    columns = [str(col) for col in selected_columns]

    rows = []
    for _, row in preview_df[columns].iterrows():
        serialized_row = []
        for value in row.tolist():
            if pd.isna(value):
                serialized_row.append('')
            elif isinstance(value, (pd.Timestamp, datetime)):
                serialized_row.append(value.isoformat())
            elif isinstance(value, np.generic):
                serialized_row.append(value.item())
            else:
                serialized_row.append(value)
        rows.append(serialized_row)

    return {
        'columns': columns,
        'rows': rows,
        'total_rows': int(len(df)),
        'total_columns': int(len(df.columns))
    }


COURSE_CATALOG = {
    'Python Programming': {
        'category': 'General', 'category_key': 'all', 'icon': 'fa-book', 'duration': '6 weeks', 'difficulty': 'Intermediate', 'rating': 4.5, 'reviews': 88,
        'description': 'Build strong Python fundamentals for automation, web apps, analytics, and AI workflows.',
        'instructor': 'Dr. Neha Sethi', 'weekly_hours': '5-7 hours/week', 'certificate': 'Yes',
        'skills': ['Python syntax', 'Functions and OOP', 'File handling', 'Problem solving'],
        'prerequisites': ['Basic computer literacy', 'No prior coding required'],
        'modules': ['Python basics', 'Control flow and functions', 'Object-oriented programming', 'Mini automation projects'],
        'outcomes': ['Write clean Python programs', 'Build foundational projects', 'Prepare for data and AI tracks']
    },
    'Data Science': {
        'category': 'Data Science', 'category_key': 'data', 'icon': 'fa-chart-bar', 'duration': '6 weeks', 'difficulty': 'Intermediate', 'rating': 4.5, 'reviews': 104,
        'description': 'Learn the end-to-end data workflow from cleaning and exploration to insight communication.',
        'instructor': 'Prof. Arjun Malhotra', 'weekly_hours': '6-8 hours/week', 'certificate': 'Yes',
        'skills': ['Data cleaning', 'Exploratory analysis', 'Visualization', 'Insight reporting'],
        'prerequisites': ['Basic math', 'Comfort with spreadsheets'],
        'modules': ['Data wrangling', 'Exploratory data analysis', 'Visualization dashboards', 'Case studies'],
        'outcomes': ['Analyze learner data', 'Present trends clearly', 'Transition into analytics roles']
    },
    'Web Development': {
        'category': 'Web Development', 'category_key': 'web', 'icon': 'fa-code', 'duration': '6 weeks', 'difficulty': 'Intermediate', 'rating': 4.5, 'reviews': 88,
        'description': 'Design and build responsive modern websites with production-ready frontend and backend patterns.',
        'instructor': 'Ritika Rao', 'weekly_hours': '6-8 hours/week', 'certificate': 'Yes',
        'skills': ['HTML/CSS', 'JavaScript', 'Responsive design', 'REST basics'],
        'prerequisites': ['Basic computer usage', 'Willingness to build projects'],
        'modules': ['Frontend fundamentals', 'Responsive layouts', 'Interactive JavaScript', 'Deployment basics'],
        'outcomes': ['Build portfolio-ready web apps', 'Understand full web delivery flow', 'Prepare for frontend/backend specialization']
    },
    'Cloud Computing': {
        'category': 'Cloud Computing', 'category_key': 'cloud', 'icon': 'fa-cloud', 'duration': '6 weeks', 'difficulty': 'Intermediate', 'rating': 4.5, 'reviews': 72,
        'description': 'Understand cloud services, deployment models, and operations for scalable systems.',
        'instructor': 'Karan Bhave', 'weekly_hours': '5-7 hours/week', 'certificate': 'Yes',
        'skills': ['Cloud architecture', 'Virtual machines', 'Storage services', 'Deployment workflows'],
        'prerequisites': ['Basic networking concepts'],
        'modules': ['Cloud fundamentals', 'Compute and storage', 'Identity and security', 'Deployment pipelines'],
        'outcomes': ['Deploy applications on cloud', 'Understand cloud cost/performance tradeoffs', 'Prepare for AWS/Azure paths']
    },
    'Machine Learning': {
        'category': 'AI & Machine Learning', 'category_key': 'ml', 'icon': 'fa-brain', 'duration': '6 weeks', 'difficulty': 'Intermediate', 'rating': 4.4, 'reviews': 48,
        'description': 'Get started with machine learning models, evaluation, and practical deployment thinking.',
        'instructor': 'Dr. Ishan Kulkarni', 'weekly_hours': '7-9 hours/week', 'certificate': 'Yes',
        'skills': ['Supervised learning', 'Feature engineering', 'Model evaluation', 'ML workflows'],
        'prerequisites': ['Python basics', 'Basic statistics'],
        'modules': ['ML pipeline', 'Regression and classification', 'Evaluation metrics', 'Mini capstone'],
        'outcomes': ['Train baseline ML models', 'Interpret results', 'Move into deep learning pathways']
    },
    'Prompt Engineering & AI Integration': {
        'category': 'AI & Machine Learning', 'category_key': 'ml', 'icon': 'fa-brain', 'duration': '4 weeks', 'difficulty': 'Intermediate', 'rating': 4.9, 'reviews': 2340,
        'description': 'Master prompt design and integrate LLM capabilities into real product workflows and apps.',
        'instructor': 'Aditi Mehra', 'weekly_hours': '4-6 hours/week', 'certificate': 'Yes',
        'skills': ['Prompt design', 'LLM evaluation', 'Workflow automation', 'AI integration patterns'],
        'prerequisites': ['Basic programming concepts'],
        'modules': ['Prompt frameworks', 'Evaluation patterns', 'RAG basics', 'Application integration'],
        'outcomes': ['Write reliable prompts', 'Integrate AI into products', 'Design practical AI workflows']
    },
    'Cloud Native Architecture with Kubernetes': {
        'category': 'Cloud Computing', 'category_key': 'cloud', 'icon': 'fa-cloud', 'duration': '6 weeks', 'difficulty': 'Advanced', 'rating': 4.8, 'reviews': 1890,
        'description': 'Design resilient microservices and orchestrate them using Kubernetes in modern cloud environments.',
        'instructor': 'Samar Verghese', 'weekly_hours': '7-9 hours/week', 'certificate': 'Yes',
        'skills': ['Containers', 'Kubernetes', 'Microservices', 'Scaling and observability'],
        'prerequisites': ['Linux basics', 'Docker familiarity'],
        'modules': ['Containers and images', 'Kubernetes objects', 'Service mesh concepts', 'Production operations'],
        'outcomes': ['Deploy cloud-native apps', 'Manage clusters', 'Design scalable resilient services']
    },
    'Full Stack Development with Modern Frameworks': {
        'category': 'Web Development', 'category_key': 'web', 'icon': 'fa-code', 'duration': '8 weeks', 'difficulty': 'Intermediate', 'rating': 4.7, 'reviews': 3210,
        'description': 'Build full-stack products with modern frontend frameworks, APIs, auth, and deployment.',
        'instructor': 'Kabir Deshmukh', 'weekly_hours': '7-9 hours/week', 'certificate': 'Yes',
        'skills': ['Frontend frameworks', 'REST APIs', 'Authentication', 'Deployment'],
        'prerequisites': ['HTML/CSS basics', 'JavaScript fundamentals'],
        'modules': ['Modern frontend', 'API architecture', 'Database integration', 'Deployment and testing'],
        'outcomes': ['Ship full-stack applications', 'Understand architecture decisions', 'Prepare for developer roles']
    },
    'React.js Advanced Patterns': {
        'category': 'Web Development', 'category_key': 'web', 'icon': 'fa-react', 'duration': '5 weeks', 'difficulty': 'Advanced', 'rating': 4.6, 'reviews': 1540,
        'description': 'Master composable React architectures, complex state patterns, and scalable UI systems.',
        'instructor': 'Naina Bhatia', 'weekly_hours': '5-7 hours/week', 'certificate': 'Yes',
        'skills': ['Compound components', 'State architecture', 'Performance optimization', 'Design systems'],
        'prerequisites': ['React fundamentals', 'ES6 JavaScript'],
        'modules': ['Advanced composition', 'State patterns', 'Performance tuning', 'Scalable component libraries'],
        'outcomes': ['Build scalable React apps', 'Improve maintainability', 'Work with advanced team patterns']
    },
    'Vue.js Fundamentals': {
        'category': 'Web Development', 'category_key': 'web', 'icon': 'fa-code', 'duration': '3 weeks', 'difficulty': 'Beginner', 'rating': 4.5, 'reviews': 980,
        'description': 'Get started with Vue by building interactive interfaces and component-based applications.',
        'instructor': 'Maya Kapoor', 'weekly_hours': '4-5 hours/week', 'certificate': 'Yes',
        'skills': ['Vue basics', 'Components', 'Reactivity', 'Routing'],
        'prerequisites': ['HTML/CSS basics', 'Basic JavaScript'],
        'modules': ['Vue setup', 'Templates and components', 'State and routing', 'Mini app project'],
        'outcomes': ['Build Vue apps', 'Understand reactive UI patterns', 'Expand into advanced SPA work']
    },
    'Backend API Development with Node.js': {
        'category': 'Web Development', 'category_key': 'web', 'icon': 'fa-code', 'duration': '6 weeks', 'difficulty': 'Intermediate', 'rating': 4.7, 'reviews': 2120,
        'description': 'Create production-ready REST and GraphQL APIs with authentication, validation, and testing.',
        'instructor': 'Rohan Dutta', 'weekly_hours': '6-8 hours/week', 'certificate': 'Yes',
        'skills': ['Node.js', 'REST APIs', 'GraphQL', 'Authentication'],
        'prerequisites': ['JavaScript basics', 'HTTP fundamentals'],
        'modules': ['Express and routing', 'API design', 'Auth and security', 'Testing and deployment'],
        'outcomes': ['Build backend services', 'Secure APIs', 'Work on production integrations']
    },
    'Data Analytics with Python': {
        'category': 'Data Science', 'category_key': 'data', 'icon': 'fa-chart-bar', 'duration': '5 weeks', 'difficulty': 'Intermediate', 'rating': 4.6, 'reviews': 1670,
        'description': 'Analyze, visualize, and communicate data stories using Python and core analytics libraries.',
        'instructor': 'Shruti Menon', 'weekly_hours': '5-7 hours/week', 'certificate': 'Yes',
        'skills': ['Pandas', 'Visualization', 'Reporting', 'EDA'],
        'prerequisites': ['Basic Python'],
        'modules': ['Pandas workflows', 'Data cleaning', 'Visualization', 'Business case dashboards'],
        'outcomes': ['Perform practical analysis', 'Present insights clearly', 'Prepare analytics portfolios']
    },
    'SQL for Data Analysis': {
        'category': 'Data Science', 'category_key': 'data', 'icon': 'fa-database', 'duration': '4 weeks', 'difficulty': 'Beginner', 'rating': 4.4, 'reviews': 1230,
        'description': 'Learn SQL querying techniques for exploration, aggregation, and insight extraction from data.',
        'instructor': 'Harsh Jain', 'weekly_hours': '4-6 hours/week', 'certificate': 'Yes',
        'skills': ['SQL querying', 'Joins', 'Aggregation', 'Window functions'],
        'prerequisites': ['No prior SQL required'],
        'modules': ['SELECT and filtering', 'Joins', 'Aggregations', 'Analytical SQL patterns'],
        'outcomes': ['Write effective SQL queries', 'Analyze databases', 'Support BI and analytics workflows']
    },
    'Big Data Processing with Spark': {
        'category': 'Data Science', 'category_key': 'data', 'icon': 'fa-fire', 'duration': '7 weeks', 'difficulty': 'Advanced', 'rating': 4.8, 'reviews': 890,
        'description': 'Process large datasets efficiently using Spark for scalable analytics and data engineering pipelines.',
        'instructor': 'Dev Chawla', 'weekly_hours': '7-9 hours/week', 'certificate': 'Yes',
        'skills': ['Spark', 'Distributed processing', 'ETL pipelines', 'Performance tuning'],
        'prerequisites': ['Python or Scala basics', 'Data processing familiarity'],
        'modules': ['Spark fundamentals', 'RDD/DataFrame APIs', 'Optimization', 'Pipeline case study'],
        'outcomes': ['Run distributed data jobs', 'Understand scale bottlenecks', 'Enter data engineering roles']
    },
    'Deep Learning Fundamentals': {
        'category': 'AI & Machine Learning', 'category_key': 'ml', 'icon': 'fa-brain', 'duration': '8 weeks', 'difficulty': 'Advanced', 'rating': 4.9, 'reviews': 1450,
        'description': 'Learn neural network design, training, and evaluation for real-world deep learning use cases.',
        'instructor': 'Dr. Sana Qureshi', 'weekly_hours': '8-10 hours/week', 'certificate': 'Yes',
        'skills': ['Neural networks', 'TensorFlow', 'Model tuning', 'Evaluation'],
        'prerequisites': ['Python', 'Linear algebra basics', 'ML fundamentals'],
        'modules': ['Neural network basics', 'CNNs and sequence models', 'Optimization', 'Applied deep learning labs'],
        'outcomes': ['Train DL models', 'Tune architectures', 'Prepare for advanced AI systems work']
    },
    'Computer Vision with OpenCV': {
        'category': 'AI & Machine Learning', 'category_key': 'ml', 'icon': 'fa-brain', 'duration': '6 weeks', 'difficulty': 'Advanced', 'rating': 4.7, 'reviews': 1120,
        'description': 'Build computer vision systems using OpenCV for detection, tracking, and image analysis.',
        'instructor': 'Ira Sen', 'weekly_hours': '6-8 hours/week', 'certificate': 'Yes',
        'skills': ['OpenCV', 'Image processing', 'Detection pipelines', 'Vision deployment'],
        'prerequisites': ['Python basics', 'ML familiarity'],
        'modules': ['Image processing basics', 'Feature extraction', 'Detection pipelines', 'Vision project'],
        'outcomes': ['Build vision applications', 'Process real images and video', 'Prepare for CV specialization']
    },
    'Natural Language Processing Essentials': {
        'category': 'AI & Machine Learning', 'category_key': 'ml', 'icon': 'fa-brain', 'duration': '5 weeks', 'difficulty': 'Intermediate', 'rating': 4.8, 'reviews': 1890,
        'description': 'Work with text pipelines, embeddings, transformers, and practical NLP applications.',
        'instructor': 'Mehul Thomas', 'weekly_hours': '6-7 hours/week', 'certificate': 'Yes',
        'skills': ['Text preprocessing', 'Embeddings', 'Transformers', 'NLP evaluation'],
        'prerequisites': ['Python basics', 'Intro ML concepts'],
        'modules': ['Text processing', 'Embeddings', 'Transformer basics', 'Applied NLP labs'],
        'outcomes': ['Build NLP features', 'Understand transformer workflows', 'Work on language-based AI products']
    },
    'AWS Solutions Architect Professional': {
        'category': 'Cloud Computing', 'category_key': 'cloud', 'icon': 'fa-cloud', 'duration': '7 weeks', 'difficulty': 'Advanced', 'rating': 4.7, 'reviews': 2340,
        'description': 'Design secure, resilient, and cost-optimized AWS architectures for complex enterprise workloads.',
        'instructor': 'Aniket Bose', 'weekly_hours': '7-9 hours/week', 'certificate': 'Yes',
        'skills': ['AWS architecture', 'Reliability design', 'Security', 'Cost optimization'],
        'prerequisites': ['AWS basics', 'Networking concepts'],
        'modules': ['Core AWS services', 'Architecture design', 'Security and compliance', 'Exam-style case studies'],
        'outcomes': ['Architect cloud solutions', 'Prepare for certification', 'Lead cloud migration decisions']
    },
    'Azure for Beginners': {
        'category': 'Cloud Computing', 'category_key': 'cloud', 'icon': 'fa-cloud', 'duration': '4 weeks', 'difficulty': 'Beginner', 'rating': 4.5, 'reviews': 1560,
        'description': 'Get comfortable with Microsoft Azure services, deployment basics, and cloud administration workflows.',
        'instructor': 'Priya Narang', 'weekly_hours': '4-6 hours/week', 'certificate': 'Yes',
        'skills': ['Azure services', 'Cloud basics', 'Identity basics', 'Resource management'],
        'prerequisites': ['No prior cloud experience required'],
        'modules': ['Azure fundamentals', 'Compute and storage', 'Monitoring', 'Deployment exercises'],
        'outcomes': ['Use Azure confidently', 'Understand cloud admin basics', 'Prepare for Azure associate tracks']
    },
    'DevOps & CI/CD Pipelines': {
        'category': 'Cloud Computing', 'category_key': 'cloud', 'icon': 'fa-cloud', 'duration': '6 weeks', 'difficulty': 'Intermediate', 'rating': 4.8, 'reviews': 1780,
        'description': 'Automate testing, delivery, and deployment using modern DevOps tooling and pipeline practices.',
        'instructor': 'Faizan Ali', 'weekly_hours': '6-8 hours/week', 'certificate': 'Yes',
        'skills': ['CI/CD', 'Automation', 'Containers', 'Deployment workflows'],
        'prerequisites': ['Git basics', 'Command line familiarity'],
        'modules': ['Version control workflows', 'Pipeline stages', 'Container delivery', 'Monitoring and rollback'],
        'outcomes': ['Build delivery pipelines', 'Automate deployment', 'Support modern engineering teams']
    },
    'Flutter App Development': {
        'category': 'Mobile Apps', 'category_key': 'mobile', 'icon': 'fa-mobile', 'duration': '6 weeks', 'difficulty': 'Intermediate', 'rating': 4.6, 'reviews': 1340,
        'description': 'Create polished cross-platform mobile apps with Flutter and a modern UI architecture.',
        'instructor': 'Tanya Vora', 'weekly_hours': '6-7 hours/week', 'certificate': 'Yes',
        'skills': ['Flutter', 'Dart', 'Cross-platform UI', 'State management'],
        'prerequisites': ['Basic programming concepts'],
        'modules': ['Dart basics', 'Flutter widgets', 'State handling', 'Publishing and polish'],
        'outcomes': ['Build mobile apps', 'Ship cross-platform products', 'Prepare for app prototyping roles']
    },
    'React Native Fundamentals': {
        'category': 'Mobile Apps', 'category_key': 'mobile', 'icon': 'fa-mobile', 'duration': '5 weeks', 'difficulty': 'Intermediate', 'rating': 4.5, 'reviews': 1120,
        'description': 'Develop mobile apps using React Native with reusable UI and native platform integration.',
        'instructor': 'Varsha Pillai', 'weekly_hours': '5-7 hours/week', 'certificate': 'Yes',
        'skills': ['React Native', 'Navigation', 'State management', 'Native APIs'],
        'prerequisites': ['JavaScript basics', 'React basics helpful'],
        'modules': ['RN setup', 'Navigation patterns', 'State and forms', 'Native integration'],
        'outcomes': ['Build mobile experiences', 'Reuse JavaScript skills for apps', 'Work on hybrid mobile teams']
    },
    'iOS Development with Swift': {
        'category': 'Mobile Apps', 'category_key': 'mobile', 'icon': 'fa-mobile', 'duration': '7 weeks', 'difficulty': 'Advanced', 'rating': 4.8, 'reviews': 980,
        'description': 'Build production-quality iOS applications with Swift, native UI patterns, and app lifecycle management.',
        'instructor': 'Aman Joseph', 'weekly_hours': '7-8 hours/week', 'certificate': 'Yes',
        'skills': ['Swift', 'UIKit/SwiftUI', 'App lifecycle', 'Native iOS patterns'],
        'prerequisites': ['Basic programming knowledge', 'Mac development environment preferred'],
        'modules': ['Swift essentials', 'UI architecture', 'Networking and persistence', 'App submission workflow'],
        'outcomes': ['Build iOS apps', 'Understand native app architecture', 'Move toward iOS specialization']
    }
}


def get_course_details(course_name, fallback=None):
    """Return detailed course metadata for a title, merged with fallback values."""
    details = deepcopy(COURSE_CATALOG.get(course_name, {}))
    fallback = fallback or {}

    merged = {
        'title': course_name,
        'category': fallback.get('category', 'General'),
        'category_key': fallback.get('category_key', 'all'),
        'icon': fallback.get('icon', 'fa-book'),
        'duration': fallback.get('duration', '6 weeks'),
        'difficulty': fallback.get('difficulty', 'Intermediate'),
        'rating': fallback.get('rating', 4.5),
        'reviews': fallback.get('reviews', 0),
        'description': fallback.get('description', 'Build relevant skills with this recommended course.'),
        'instructor': 'Faculty Team',
        'weekly_hours': '5-7 hours/week',
        'certificate': 'Yes',
        'skills': ['Core concepts', 'Hands-on projects'],
        'prerequisites': ['Interest in the subject'],
        'modules': ['Foundations', 'Applied practice', 'Capstone'],
        'outcomes': ['Gain practical skills', 'Build confidence in the subject']
    }
    merged.update(details)

    for key, value in fallback.items():
        if value not in [None, ''] and key in merged and not details.get(key):
            merged[key] = value

    return merged


def compute_course_dashboard_insights(df):
    """Compute user dashboard course insights from student activity data."""
    default = {
        'top_enrolled': {'course': 'N/A', 'count': 0, 'metric': 'No data'},
        'least_enrolled': {'course': 'N/A', 'count': 0, 'metric': 'No data'},
        'market_useful': {'course': 'N/A', 'score': 0.0, 'metric': 'No data'},
        'high_impact': {'course': 'N/A', 'score': 0.0, 'metric': 'No data'}
    }

    if df is None or df.empty or 'course_name' not in df.columns or 'student_id' not in df.columns:
        return default

    enrollments = df.groupby('course_name')['student_id'].nunique().sort_values(ascending=False)
    if enrollments.empty:
        return default

    top_course = enrollments.index[0]
    top_count = int(enrollments.iloc[0])
    least_course = enrollments.index[-1]
    least_count = int(enrollments.iloc[-1])

    course_metrics = pd.DataFrame({'enrollments': enrollments})
    if 'quiz_score' in df.columns:
        course_metrics['avg_quiz'] = df.groupby('course_name')['quiz_score'].mean()
    else:
        course_metrics['avg_quiz'] = 0.0

    if 'engagement_score' in df.columns:
        course_metrics['avg_engagement'] = df.groupby('course_name')['engagement_score'].mean()
    else:
        course_metrics['avg_engagement'] = 0.0

    if 'course_progress' in df.columns:
        course_completion = (
            df.groupby(['course_name', 'student_id'])['course_progress'].max().reset_index()
            .assign(completed=lambda x: (x['course_progress'] >= 100).astype(float))
            .groupby('course_name')['completed'].mean()
        )
        course_metrics['completion_rate'] = course_completion
    else:
        course_metrics['completion_rate'] = 0.0

    def _normalize(series):
        s = series.fillna(0.0).astype(float)
        min_v = s.min()
        max_v = s.max()
        if max_v == min_v:
            return pd.Series([1.0] * len(s), index=s.index)
        return (s - min_v) / (max_v - min_v)

    market_score = 0.6 * _normalize(course_metrics['enrollments']) + 0.4 * _normalize(course_metrics['avg_quiz'])
    impact_score = 0.5 * _normalize(course_metrics['avg_engagement']) + 0.5 * _normalize(course_metrics['completion_rate'])

    market_course = market_score.idxmax()
    impact_course = impact_score.idxmax()

    return {
        'top_enrolled': {
            'course': str(top_course),
            'count': top_count,
            'metric': f"{top_count} students"
        },
        'least_enrolled': {
            'course': str(least_course),
            'count': least_count,
            'metric': f"{least_count} students"
        },
        'market_useful': {
            'course': str(market_course),
            'score': float(market_score.loc[market_course]),
            'metric': f"Market score {(market_score.loc[market_course] * 100):.1f}/100"
        },
        'high_impact': {
            'course': str(impact_course),
            'score': float(impact_score.loc[impact_course]),
            'metric': f"Impact score {(impact_score.loc[impact_course] * 100):.1f}/100"
        }
    }


def build_student_course_map(df):
    """Build student-to-course mapping points for dashboard visualization."""
    if df is None or df.empty or 'student_id' not in df.columns or 'course_name' not in df.columns:
        return {'courses': [], 'points': []}

    mapping = df[['student_id', 'course_name']].dropna().drop_duplicates()
    mapping['student_id'] = pd.to_numeric(mapping['student_id'], errors='coerce')
    mapping = mapping.dropna(subset=['student_id'])
    mapping['student_id'] = mapping['student_id'].astype(int)

    courses = sorted(mapping['course_name'].astype(str).unique().tolist())
    course_index = {name: index + 1 for index, name in enumerate(courses)}

    points = [
        {
            'x': int(row.student_id),
            'y': int(course_index[str(row.course_name)]),
            'course': str(row.course_name)
        }
        for row in mapping.itertuples(index=False)
    ]

    return {
        'courses': courses,
        'points': points
    }


def infer_course_category(course_name):
    """Infer a display category from course title keywords."""
    name = str(course_name or '').lower()
    if any(keyword in name for keyword in ['machine learning', 'deep learning', 'ai', 'nlp']):
        return 'AI & Machine Learning', 'ml', 'fa-brain'
    if any(keyword in name for keyword in ['web', 'full stack', 'frontend', 'backend']):
        return 'Web Development', 'web', 'fa-code'
    if any(keyword in name for keyword in ['data', 'analytics', 'sql', 'spark']):
        return 'Data Science', 'data', 'fa-chart-bar'
    if any(keyword in name for keyword in ['cloud', 'aws', 'azure', 'devops', 'kubernetes']):
        return 'Cloud Computing', 'cloud', 'fa-cloud'
    if any(keyword in name for keyword in ['mobile', 'flutter', 'ios', 'android', 'react native']):
        return 'Mobile Apps', 'mobile', 'fa-mobile'
    return 'General', 'all', 'fa-book'


def build_trending_courses(df, limit=6):
    """Build trending course suggestions from usage data."""
    if df is None or df.empty or 'course_name' not in df.columns:
        return []

    group_cols = ['course_name']
    if 'student_id' in df.columns:
        enrollment_series = df.groupby('course_name')['student_id'].nunique()
    else:
        enrollment_series = df.groupby('course_name').size()

    metrics = pd.DataFrame({'enrollments': enrollment_series})
    if 'engagement_score' in df.columns:
        metrics['avg_engagement'] = df.groupby('course_name')['engagement_score'].mean().round(1)
    else:
        metrics['avg_engagement'] = 0.0

    if 'quiz_score' in df.columns:
        metrics['avg_quiz_score'] = df.groupby('course_name')['quiz_score'].mean().round(1)
    else:
        metrics['avg_quiz_score'] = 0.0

    if 'platform' in df.columns:
        top_platform = (
            df.groupby(['course_name', 'platform']).size().reset_index(name='count')
            .sort_values(['course_name', 'count'], ascending=[True, False])
            .drop_duplicates(subset=['course_name'])
            .set_index('course_name')['platform']
        )
        metrics['platform'] = top_platform
    else:
        metrics['platform'] = 'Online'

    metrics = metrics.sort_values(['enrollments', 'avg_engagement'], ascending=[False, False]).head(limit)

    results = []
    for course_name, row in metrics.iterrows():
        category, category_key, icon = infer_course_category(course_name)
        avg_engagement = float(row.get('avg_engagement', 0.0) or 0.0)
        if avg_engagement >= 8:
            difficulty = 'Advanced'
        elif avg_engagement >= 6:
            difficulty = 'Intermediate'
        else:
            difficulty = 'Beginner'

        results.append(get_course_details(str(course_name), fallback={
            'title': str(course_name),
            'category': category,
            'categoryKey': category_key,
            'category_key': category_key,
            'icon': icon,
            'description': f"Popular course with strong learner activity on {row.get('platform', 'Online')}.",
            'duration': '6 weeks',
            'difficulty': difficulty,
            'rating': round(min(5.0, 3.8 + (avg_engagement / 10.0) + (float(row.get('enrollments', 0)) / 200.0)), 1),
            'reviews': int(row.get('enrollments', 0)) * 8,
            'trending': True,
            'marketTrend': True,
            'enrollments': int(row.get('enrollments', 0)),
            'avg_engagement': avg_engagement
        }))

    return results


def build_recommended_courses(trending_courses, user_id):
    """Build personalized recommendations for the current user."""
    if not trending_courses:
        return []

    enrollments_collection = mongo_db[MONGO_COURSE_ENROLLMENTS_COLLECTION]
    user_enrollments = list(enrollments_collection.find({'user_id': user_id}, {'course_name': 1, 'category_key': 1}))
    enrolled_names = {str(item.get('course_name', '')).lower() for item in user_enrollments}

    candidates = [
        course for course in trending_courses
        if str(course.get('title', '')).lower() not in enrolled_names
    ]

    if not user_enrollments:
        for course in candidates:
            course['recommendation_reason'] = 'High-demand course and a strong starting point right now.'
        return candidates[:3]

    category_counts = {}
    for item in user_enrollments:
        key = item.get('category_key')
        if key:
            category_counts[key] = category_counts.get(key, 0) + 1

    preferred_category = None
    if category_counts:
        preferred_category = max(category_counts.items(), key=lambda x: x[1])[0]

    if preferred_category:
        preferred = [c for c in candidates if c.get('categoryKey') == preferred_category]
        others = [c for c in candidates if c.get('categoryKey') != preferred_category]
        ordered = preferred + others
    else:
        ordered = candidates

    selected = ordered[:3]
    for course in selected:
        if preferred_category and course.get('categoryKey') == preferred_category:
            course['recommendation_reason'] = 'Matches your recent learning path and current market demand.'
        else:
            course['recommendation_reason'] = 'Trending now and complements your current learning track.'

    return selected


def ensure_course_enrollment(user_id, course_name, category_key=''):
    """Create or return an existing course enrollment for a user."""
    enrollments_collection = mongo_db[MONGO_COURSE_ENROLLMENTS_COLLECTION]
    existing = enrollments_collection.find_one({
        'user_id': user_id,
        'course_name': course_name
    })
    if existing:
        return False

    enrollments_collection.insert_one({
        'user_id': user_id,
        'course_name': course_name,
        'category_key': category_key,
        'enrolled_at': datetime.utcnow()
    })
    return True


def attach_student_names(predictions_df):
    """Attach stable pseudo-random student names for display."""
    names = [
        'Aarav Sharma', 'Aisha Khan', 'Arjun Mehta', 'Diya Patel', 'Ishan Verma',
        'Kavya Rao', 'Neha Gupta', 'Rahul Singh', 'Riya Nair', 'Sana Ali',
        'Aditya Joshi', 'Ananya Kapoor', 'Ishita Das', 'Karan Malhotra', 'Meera Iyer',
        'Nikhil Bansal', 'Pooja Menon', 'Rohan Khanna', 'Siddharth Jain', 'Tanvi Kulkarni',
        'Varun Chopra', 'Zoya Farooq', 'Vivaan Roy', 'Anika Bhatt', 'Manav Sethi'
    ]
    predictions_df = predictions_df.copy()
    predictions_df['student_id'] = pd.to_numeric(predictions_df['student_id'], errors='coerce')
    student_ids = sorted(predictions_df['student_id'].dropna().unique())
    rng = random.Random(2026)
    rng.shuffle(names)
    name_map = {
        student_id: names[index % len(names)]
        for index, student_id in enumerate(student_ids)
    }
    predictions_df['student_name'] = predictions_df['student_id'].map(name_map)
    predictions_df['student_name'] = predictions_df.apply(
        lambda row: row['student_name']
        if pd.notna(row['student_name'])
        else f"Student #{int(row['student_id'])}" if pd.notna(row['student_id'])
        else 'Student',
        axis=1
    )
    return predictions_df


@app.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        error = None
        
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            try:
                user = mongo_db[MONGO_USERS_COLLECTION].find_one({'email': email})

                if user is None:
                    error = 'Incorrect email. Please check your email or register first.'
                elif not check_password_hash(user['password'], password):
                    error = 'Incorrect password.'
                else:
                    # Login successful
                    session.clear()
                    session['user_id'] = str(user['_id'])
                    session['email'] = user.get('email')
                    session['name'] = user.get('name')
                    session['role'] = user.get('role', 'student')  # Default to student
                    session.permanent = True
                    print(f"✅ User {user['_id']} logged in successfully. Role: {session.get('role')}")
                    print(f"Session: {dict(session)}")
                    
                    # Redirect based on role
                    if session.get('role') == 'admin':
                        print(f"Redirecting admin to admin dashboard")
                        return redirect(url_for('admin_dashboard'))
                    else:
                        print(f"Redirecting {session.get('role')} to dashboard")
                        return redirect(url_for('dashboard'))
            except Exception as e:
                print(f"Login error: {e}")
                import traceback
                traceback.print_exc()
                error = f'Database error. Please try again.'
        
        return render_template('login.html', error=error)
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')  # Default to student
        error = None
        success_message = None
        
        if not name:
            error = 'Name is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not confirm_password:
            error = 'Confirm password is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters long.'
        
        if error is None:
            try:
                user_data = {
                    'name': name,
                    'email': email,
                    'password': generate_password_hash(password),
                    'role': role,  # Store role: admin or student
                    'created_at': datetime.utcnow()
                }
                
                result = mongo_db[MONGO_USERS_COLLECTION].insert_one(user_data)
                print(f"User registered successfully: {email} (Role: {role})")
                
                # Show role-specific success message
                if role == 'admin':
                    success_message = f"""
                    ✅ Welcome Admin!
                    
                    Account successfully registered.
                    Name: {name}
                    Email: {email}
                    Role: Administrator
                    
                    Please login to continue to the Admin Dashboard.
                    """
                    redirect_time = 5
                else:
                    success_message = f"""
                    ✅ Welcome Student!
                    
                    Account successfully registered.
                    Name: {name}
                    Email: {email}
                    Role: Student
                    
                    Please login to continue to your Dashboard.
                    """
                    redirect_time = 5
                
                return render_template('register.html', 
                                     success_message=success_message,
                                     redirect_after=redirect_time,
                                     registered_role=role)
                
            except DuplicateKeyError as e:
                print(f"Registration DuplicateKeyError: {e}")
                error = 'Email already registered. Please login instead.'
            except Exception as e:
                print(f"Registration error: {e}")
                import traceback
                traceback.print_exc()
                error = f'An error occurred during registration. Please try again.'
        
        return render_template('register.html', error=error)
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))


# ============================================================================
# PROFILE ROUTES
# ============================================================================

@app.route('/profile')
@login_required
def student_profile():
    """Student profile page"""
    try:
        user_id = session.get('user_id')
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return redirect(url_for('login'))
        
        # Mock statistics for student (can be replaced with actual data)
        stats = {
            'courses_enrolled': 5,
            'certificates_earned': 2,
            'avg_quiz_score': 78,
            'hours_learned': 24
        }
        
        return render_template('student_profile.html', user=user, stats=stats)
    except Exception as e:
        print(f"Profile error: {e}")
        return redirect(url_for('dashboard'))


@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change student password"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user_id = session.get('user_id')
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        
        # Verify current password
        if not check_password_hash(user['password'], current_password):
            return render_template('student_profile.html', 
                                 user=user, 
                                 stats={},
                                 error_message='Current password is incorrect.')
        
        # Validate new password
        if new_password != confirm_password:
            return render_template('student_profile.html', 
                                 user=user, 
                                 stats={},
                                 error_message='New passwords do not match.')
        
        if len(new_password) < 6:
            return render_template('student_profile.html', 
                                 user=user, 
                                 stats={},
                                 error_message='Password must be at least 6 characters.')
        
        # Update password
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': generate_password_hash(new_password)}}
        )
        
        return render_template('student_profile.html', 
                             user=user, 
                             stats={},
                             success_message='Password updated successfully!')
    except Exception as e:
        print(f"Password change error: {e}")
        return redirect(url_for('student_profile'))


@app.route('/profile/delete-account', methods=['POST'])
@login_required
def delete_student_account():
    """Delete student account"""
    try:
        user_id = session.get('user_id')
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count > 0:
            session.clear()
            return jsonify({'success': True, 'message': 'Account deleted'}), 200
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        print(f"Delete account error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/profile')
@admin_required
def admin_profile():
    """Admin profile page"""
    try:
        admin_id = session.get('user_id')
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        admin = users_collection.find_one({'_id': ObjectId(admin_id)})
        
        if not admin:
            return redirect(url_for('login'))
        
        # Get system statistics
        total_users = users_collection.count_documents({})
        admin_count = users_collection.count_documents({'role': 'admin'})
        student_count = users_collection.count_documents({'role': 'student'})
        
        # Load data statistics
        df = load_data()
        total_data_records = len(df) if df is not None else 0
        
        stats = {
            'total_users': total_users,
            'admin_count': admin_count,
            'student_count': student_count,
            'total_data_records': total_data_records
        }
        
        # Mock recent activities
        activities = [
            {'icon': 'user-plus', 'action': 'New user registration', 'timestamp': 'Today at 2:30 PM'},
            {'icon': 'lock', 'action': 'Password change', 'timestamp': 'Today at 1:15 PM'},
            {'icon': 'download', 'action': 'Data export', 'timestamp': 'Yesterday at 4:45 PM'},
            {'icon': 'trash', 'action': 'User account deleted', 'timestamp': 'Yesterday at 10:20 AM'},
        ]
        
        return render_template('admin_profile.html', admin=admin, stats=stats, activities=activities)
    except Exception as e:
        print(f"Admin profile error: {e}")
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/profile/change-password', methods=['POST'])
@admin_required
def admin_change_password():
    """Change admin password"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        admin_id = session.get('user_id')
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        admin = users_collection.find_one({'_id': ObjectId(admin_id)})
        
        # Verify current password
        if not check_password_hash(admin['password'], current_password):
            return render_template('admin_profile.html', 
                                 admin=admin, 
                                 stats={},
                                 activities=[],
                                 error_message='Current password is incorrect.')
        
        # Validate new password
        if new_password != confirm_password:
            return render_template('admin_profile.html', 
                                 admin=admin, 
                                 stats={},
                                 activities=[],
                                 error_message='New passwords do not match.')
        
        if len(new_password) < 6:
            return render_template('admin_profile.html', 
                                 admin=admin, 
                                 stats={},
                                 activities=[],
                                 error_message='Password must be at least 6 characters.')
        
        # Update password
        users_collection.update_one(
            {'_id': ObjectId(admin_id)},
            {'$set': {'password': generate_password_hash(new_password)}}
        )
        
        return render_template('admin_profile.html', 
                             admin=admin, 
                             stats={},
                             activities=[],
                             success_message='Password updated successfully!')
    except Exception as e:
        print(f"Admin password change error: {e}")
        return redirect(url_for('admin_profile'))


@app.route('/admin/profile/export-data')
@admin_required
def export_admin_data():
    """Export system data for admin"""
    try:
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        
        # Get all users (excluding sensitive data)
        users = list(users_collection.find({}, {'password': 0}))
        
        # Convert ObjectId to string for JSON serialization
        for user in users:
            user['_id'] = str(user['_id'])
            if 'created_at' in user:
                user['created_at'] = str(user['created_at'])
        
        # Create CSV response
        from io import StringIO
        import csv
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = ['ID', 'Name', 'Email', 'Role', 'Created At']
        writer.writerow(headers)
        
        # Write data
        for user in users:
            writer.writerow([
                user.get('_id', 'N/A'),
                user.get('name', 'N/A'),
                user.get('email', 'N/A'),
                user.get('role', 'N/A'),
                user.get('created_at', 'N/A')
            ])
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Disposition': 'attachment; filename=system_data.csv',
            'Content-Type': 'text/csv'
        }
    except Exception as e:
        print(f"Export data error: {e}")
        return redirect(url_for('admin_profile'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard view"""
    print(f"Dashboard accessed by user_id: {session.get('user_id')}")
    df = load_data()
    
    if df is not None:
        # Calculate statistics
        stats = {
            'total_students': int(df['student_id'].nunique()),
            'avg_engagement': float(df['engagement_score'].mean()),
            'completion_rate': float((df.groupby('student_id')['course_progress'].max() == 100).mean() * 100),
            'avg_quiz_score': float(df['quiz_score'].mean()),
            'avg_time_spent': float(df['time_spent_hours'].mean()),
            'total_records': int(len(df))
        }
        course_insights = compute_course_dashboard_insights(df)
    else:
        stats = {
            'total_students': 0,
            'avg_engagement': 0,
            'completion_rate': 0,
            'avg_quiz_score': 0,
            'avg_time_spent': 0,
            'total_records': 0
        }
        course_insights = compute_course_dashboard_insights(None)
    
    return render_template('dashboard.html', stats=stats, course_insights=course_insights)


@app.route('/courses')
@login_required
def courses():
    """Courses page for students"""
    try:
        user_id = session.get('user_id')
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        user = None
        if user_id:
            try:
                user = users_collection.find_one({'_id': ObjectId(user_id)})
            except Exception:
                user = None
        
        if not user:
            user = {
                'name': session.get('name', 'Student'),
                'email': session.get('email', '')
            }
        
        # Return the courses page with course data (data is handled client-side for dynamic filtering)
        return render_template('courses.html', user=user)
    except Exception as e:
        print(f"Courses page error: {e}")
        return redirect(url_for('dashboard'))


@app.route('/courses/enrollment')
@login_required
def course_enrollment_page():
    """Enrollment details page shown after a student selects a course."""
    try:
        course_name = request.args.get('course_name', '').strip()
        if not course_name:
            return redirect(url_for('courses'))

        category = request.args.get('category', 'General').strip() or 'General'
        category_key = request.args.get('category_key', 'all').strip() or 'all'
        description = request.args.get('description', 'Build relevant skills with this recommended course.').strip()
        icon = request.args.get('icon', 'fa-book').strip() or 'fa-book'
        difficulty = request.args.get('difficulty', 'Intermediate').strip() or 'Intermediate'
        duration = request.args.get('duration', '6 weeks').strip() or '6 weeks'
        rating = request.args.get('rating', '4.7').strip() or '4.7'
        reviews = request.args.get('reviews', '0').strip() or '0'
        recommendation_reason = request.args.get('reason', '').strip()

        user_id = session.get('user_id')
        created = ensure_course_enrollment(user_id, course_name, category_key)

        enrollment_details = get_course_details(course_name, fallback={
            'category': category,
            'category_key': category_key,
            'description': description,
            'icon': icon,
            'difficulty': difficulty,
            'duration': duration,
            'rating': rating,
            'reviews': reviews
        })
        enrollment_details['recommendation_reason'] = recommendation_reason
        enrollment_details['status'] = 'Newly Enrolled' if created else 'Already Enrolled'
        enrollment_details['enrolled_at'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M')

        user = {
            'name': session.get('name', 'Student'),
            'email': session.get('email', '')
        }

        return render_template('enrollment.html', user=user, enrollment=enrollment_details)
    except Exception as e:
        print(f"Enrollment page error: {e}")
        return redirect(url_for('courses'))


@app.route('/api/courses/suggestions', methods=['GET'])
@login_required
def api_course_suggestions():
    """Return trending and personalized course suggestions for student view."""
    try:
        df = load_data()
        trending_courses = build_trending_courses(df, limit=8)
        recommended_courses = build_recommended_courses(trending_courses, session.get('user_id'))

        return jsonify({
            'success': True,
            'trending': trending_courses,
            'recommended': recommended_courses
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/courses/enroll', methods=['POST'])
@login_required
def api_enroll_course():
    """Enroll current user into a selected course for recommendation tracking."""
    try:
        payload = request.json or {}
        course_name = str(payload.get('course_name', '')).strip()
        category_key = str(payload.get('category_key', '')).strip()

        if not course_name:
            return jsonify({'success': False, 'error': 'course_name is required'}), 400

        user_id = session.get('user_id')
        ensure_course_enrollment(user_id, course_name, category_key)

        return jsonify({'success': True, 'message': f'Enrolled in {course_name}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard view"""
    print(f"Admin dashboard accessed by admin_id: {session.get('user_id')}")
    
    # Get all users statistics
    users_collection = mongo_db[MONGO_USERS_COLLECTION]
    
    all_users = list(users_collection.find({}, {'_id': 1, 'name': 1, 'email': 1, 'role': 1, 'created_at': 1}))
    
    # Count users by role
    admin_count = users_collection.count_documents({'role': 'admin'})
    student_count = users_collection.count_documents({'role': 'student'})
    total_users = len(all_users)
    
    # Load data statistics
    df = load_data()
    if df is not None:
        data_stats = {
            'total_students': int(df['student_id'].nunique()),
            'total_records': int(len(df)),
            'avg_engagement': float(df['engagement_score'].mean()),
            'completion_rate': float((df.groupby('student_id')['course_progress'].max() == 100).mean() * 100)
        }
        data_preview = build_data_preview(df)
    else:
        data_stats = {
            'total_students': 0,
            'total_records': 0,
            'avg_engagement': 0,
            'completion_rate': 0
        }
        data_preview = build_data_preview(None)
    
    admin_info = {
        'name': session.get('name'),
        'email': session.get('email'),
        'registered_at': session.get('created_at', 'N/A')
    }
    
    stats = {
        'total_users': total_users,
        'admin_count': admin_count,
        'student_count': student_count,
        'data_stats': data_stats,
        'admin_info': admin_info
    }
    
    return render_template('admin_dashboard.html', 
                         stats=stats,
                         users=all_users,
                         data_preview=data_preview)


# ============================================================================
# ADMIN API ROUTES
# ============================================================================

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users in the system"""
    try:
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        users = list(users_collection.find({}, {'password': 0}))  # Exclude passwords
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return jsonify({
            'success': True,
            'total': len(users),
            'users': users
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/users/<user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """Update user role"""
    try:
        data = request.json
        new_role = data.get('role')
        
        if new_role not in ['admin', 'student']:
            return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'role': new_role}}
        )
        
        if result.modified_count == 0:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f'User role updated to {new_role}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    try:
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        
        # Prevent deleting yourself
        if user_id == session.get('user_id'):
            return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 400
        
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count == 0:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/stats/summary', methods=['GET'])
@admin_required
def get_admin_stats_summary():
    """Get system statistics summary"""
    try:
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        
        stats = {
            'total_users': users_collection.count_documents({}),
            'admins': users_collection.count_documents({'role': 'admin'}),

            'students': users_collection.count_documents({'role': 'student'})
        }
        
        # Add data statistics
        df = load_data()
        if df is not None:
            stats['data_records'] = int(len(df))
            stats['unique_students'] = int(df['student_id'].nunique())
            stats['avg_engagement'] = float(df['engagement_score'].mean())
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/audit-log', methods=['GET'])
@admin_required
def get_audit_log():
    """Get system audit log (login history)"""
    try:
        # For now, return recent user registrations
        users_collection = mongo_db[MONGO_USERS_COLLECTION]
        recent_users = list(users_collection.find(
            {},
            {'name': 1, 'email': 1, 'role': 1, 'created_at': 1}
        ).sort('created_at', -1).limit(50))
        
        for user in recent_users:
            user['_id'] = str(user['_id'])
        
        return jsonify({
            'success': True,
            'total': len(recent_users),
            'logs': recent_users
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/data/upload', methods=['POST'])
@admin_required
def upload_admin_data():
    """Upload CSV/Excel data and replace the processed dataset."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename is None or file.filename.strip() == '':
            return jsonify({'success': False, 'error': 'Please select a file'}), 400

        filename = file.filename.strip()
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ['.csv', '.xlsx', '.xls']:
            return jsonify({'success': False, 'error': 'Unsupported file type. Use CSV or Excel (.xlsx/.xls).'}), 400

        try:
            if extension == '.csv':
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except ImportError:
            return jsonify({'success': False, 'error': 'Excel support requires openpyxl. Install it and try again.'}), 500

        if df is None or df.empty:
            return jsonify({'success': False, 'error': 'Uploaded file has no data rows'}), 400

        processed_dir = os.path.join(BASE_DIR, 'data', 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        target_path = os.path.join(processed_dir, 'cleaned_data.csv')

        df.to_csv(target_path, index=False)

        return jsonify({
            'success': True,
            'message': 'Data uploaded successfully',
            'saved_to': 'Backend/data/processed/cleaned_data.csv',
            'rows': int(len(df)),
            'columns': int(len(df.columns)),
            'preview': build_data_preview(df)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/analytics')
@login_required
def analytics():
    """Analytics view with detailed charts"""
    df = load_data()
    training_summary = load_training_summary()
    course_insights = compute_course_dashboard_insights(df)
    
    return render_template('analytics.html', 
                         has_data=df is not None,
                         has_training=training_summary is not None,
                         course_insights=course_insights)


@app.route('/predictions')
@login_required
def predictions():
    """Predictions view"""
    predictions_df = load_predictions()
    
    if predictions_df is not None:
        predictions_df = attach_student_names(predictions_df)
        # Calculate risk distribution
        risk_counts = predictions_df['risk_level'].value_counts().to_dict()
        
        # Get high-risk students
        high_risk = predictions_df[predictions_df['risk_level'] == 'High Risk'].to_dict('records')
        
        summary = {
            'total': len(predictions_df),
            'risk_distribution': risk_counts,
            'high_risk_students': high_risk,
            'avg_score': float(predictions_df['engagement_score'].mean())
        }
    else:
        summary = None
    
    return render_template('predictions.html', 
                         predictions=predictions_df.to_dict('records') if predictions_df is not None else None,
                         summary=summary)


@app.route('/api/student-progress')
def api_student_progress():
    """API endpoint for student progress data"""
    df = load_data()
    
    if df is None:
        return jsonify({'error': 'No data available'}), 404
    
    # Calculate weekly progress for each student
    progress_data = []
    for student_id in df['student_id'].unique()[:10]:  # Limit to 10 students
        student_df = df[df['student_id'] == student_id]
        progress_data.append({
            'student_id': int(student_id),
            'weeks': student_df['week'].tolist(),
            'progress': student_df['course_progress'].tolist(),
            'engagement': student_df['engagement_score'].tolist()
        })
    
    return jsonify(progress_data)


@app.route('/api/engagement-trends')
def api_engagement_trends():
    """API endpoint for engagement trends"""
    df = load_data()
    
    if df is None:
        return jsonify({'error': 'No data available'}), 404
    
    # Calculate average engagement by week
    weekly_engagement = df.groupby('week')['engagement_score'].mean()
    
    return jsonify({
        'weeks': weekly_engagement.index.tolist(),
        'engagement': weekly_engagement.values.tolist()
    })


@app.route('/api/quiz-scores')
def api_quiz_scores():
    """API endpoint for quiz score distribution"""
    df = load_data()
    
    if df is None:
        return jsonify({'error': 'No data available'}), 404
    
    # Get latest quiz scores for each student
    latest_scores = df.groupby('student_id')['quiz_score'].last()
    
    # Create bins
    bins = [0, 50, 60, 70, 80, 90, 100]
    labels = ['0-50', '51-60', '61-70', '71-80', '81-90', '91-100']
    score_distribution = pd.cut(latest_scores, bins=bins, labels=labels, include_lowest=True)
    
    return jsonify({
        'labels': labels,
        'counts': score_distribution.value_counts().sort_index().tolist()
    })


@app.route('/api/time-performance')
def api_time_performance():
    """API endpoint for time spent vs performance"""
    df = load_data()

    if df is None:
        return jsonify({'error': 'No data available'}), 404

    required_columns = {'time_spent_hours', 'quiz_score'}
    if not required_columns.issubset(df.columns):
        return jsonify({'error': 'Required data not available'}), 404

    points = df[['time_spent_hours', 'quiz_score']].dropna()

    return jsonify({
        'points': [
            {'x': float(row.time_spent_hours), 'y': float(row.quiz_score)}
            for row in points.itertuples(index=False)
        ]
    })


@app.route('/api/engagement-distribution')
def api_engagement_distribution():
    """API endpoint for engagement score distribution"""
    df = load_data()

    if df is None:
        return jsonify({'error': 'No data available'}), 404

    if 'engagement_score' not in df.columns:
        return jsonify({'error': 'Engagement data not available'}), 404

    bins = [0, 2, 4, 6, 8, 10]
    labels = ['0-2', '2-4', '4-6', '6-8', '8-10']
    distribution = pd.cut(df['engagement_score'], bins=bins, labels=labels, include_lowest=True)

    return jsonify({
        'labels': labels,
        'counts': distribution.value_counts().sort_index().tolist()
    })


@app.route('/api/training-metrics')
def api_training_metrics():
    """API endpoint for training metrics"""
    summary = load_training_summary()
    
    if summary is None:
        return jsonify({'error': 'No training data available'}), 404
    
    return jsonify(summary)


@app.route('/api/predict-student', methods=['POST'])
def api_predict_student():
    """API endpoint to predict for a specific student"""
    try:
        initialize_predictor()
        
        if predictor is None:
            return jsonify({'error': 'Model not loaded. Please train the model first.'}), 500
        
        data = request.json
        student_id = data.get('student_id')
        
        df = load_data()
        if df is None:
            return jsonify({'error': 'No data available'}), 404
        
        # Get student data
        student_data = df[df['student_id'] == student_id].tail(3)
        
        if len(student_data) < 3:
            return jsonify({'error': 'Insufficient data for prediction'}), 400
        
        # Make prediction
        prediction = predictor.predict_for_student(student_data)
        
        return jsonify(prediction)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/risk-distribution')
def api_risk_distribution():
    """API endpoint for risk distribution"""
    predictions_df = load_predictions()
    
    if predictions_df is None:
        return jsonify({'error': 'No predictions available'}), 404
    
    risk_counts = predictions_df['risk_level'].value_counts()
    
    return jsonify({
        'labels': risk_counts.index.tolist(),
        'values': risk_counts.values.tolist()
    })


@app.route('/api/statistics')
def api_statistics():
    """API endpoint for general statistics"""
    df = load_data()
    
    if df is None:
        return jsonify({'error': 'No data available'}), 404
    
    stats = {
        'total_students': int(df['student_id'].nunique()),
        'total_records': int(len(df)),
        'avg_engagement': float(df['engagement_score'].mean()),
        'avg_quiz_score': float(df['quiz_score'].mean()),
        'avg_assignment_score': float(df['assignment_score'].mean()),
        'avg_time_spent': float(df['time_spent_hours'].mean()),
        'completion_rate': float((df.groupby('student_id')['course_progress'].max() == 100).mean() * 100),
        'avg_video_completion': float(df['video_completion_rate'].mean() * 100)
    }
    
    return jsonify(stats)


@app.route('/api/platform-distribution')
def api_platform_distribution():
    """API endpoint for platform usage distribution"""
    df = load_data()
    
    if df is None:
        return jsonify({'error': 'No data available'}), 404
    
    # Check if platform column exists
    if 'platform' not in df.columns:
        return jsonify({'error': 'Platform data not available'}), 404
    
    # Get unique students per platform
    platform_counts = df.groupby('platform')['student_id'].nunique()
    
    return jsonify({
        'labels': platform_counts.index.tolist(),
        'values': platform_counts.values.tolist()
    })


@app.route('/api/course-distribution')
def api_course_distribution():
    """API endpoint for course enrollment distribution"""
    df = load_data()
    
    if df is None:
        return jsonify({'error': 'No data available'}), 404
    
    # Check if course_name column exists
    if 'course_name' not in df.columns:
        return jsonify({'error': 'Course data not available'}), 404
    
    # Get unique students per course
    course_counts = df.groupby('course_name')['student_id'].nunique()
    
    return jsonify({
        'labels': course_counts.index.tolist(),
        'values': course_counts.values.tolist()
    })


@app.route('/api/student-course-map')
def api_student_course_map():
    """API endpoint for mapping student enrollments to courses."""
    df = load_data()

    if df is None:
        return jsonify({'error': 'No data available'}), 404

    if 'student_id' not in df.columns or 'course_name' not in df.columns:
        return jsonify({'error': 'Student-course data not available'}), 404

    return jsonify(build_student_course_map(df))


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Initialize database (only in main process, not reloader)
    import os
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\n" + "=" * 70)
        print("AI E-LEARNING ANALYTICS PLATFORM")
        print("=" * 70)
    
    # Always initialize database
    init_db()
    
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\nStarting Flask application...")
        print("Login page will be available at: http://127.0.0.1:5000/login")
        print("Dashboard will be available at: http://127.0.0.1:5000/dashboard")
        print("\nFirst time user? Register at: http://127.0.0.1:5000/register")
        print("\nPress CTRL+C to stop the server")
        print("=" * 70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
