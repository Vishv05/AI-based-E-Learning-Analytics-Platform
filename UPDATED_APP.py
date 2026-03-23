"""
UPDATED app.py - Complete Integration of All 5 New Features

This shows how to integrate all 5 new features into your existing Flask app.
Copy the relevant sections into your actual Backend/app.py file.

Features integrated:
1. Email Alerts to Teachers
2. Dark Mode Theme
3. Data Export (CSV/Excel/PDF/JSON)
4. Student Timeline & Milestones
5. API Rate Limiting

Author: E-Learning Analytics Platform
Date: 2024
"""

import os
import sys
import json
from datetime import datetime
from functools import wraps

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

import pandas as pd
from flask import (
    Flask, render_template, jsonify, request, session, 
    redirect, url_for, send_file, g
)
from pymongo import MongoClient
from dotenv import load_dotenv
import io

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ============================================================================
# IMPORT NEW MODULES
# ============================================================================

# Import new modules with error handling
EmailAlertService = None
ALERT_THRESHOLDS = {}
try:
    from alert_service import EmailAlertService, ALERT_THRESHOLDS  # type: ignore
except ImportError:
    pass

DataExporter = None
try:
    from data_export import DataExporter  # type: ignore
except ImportError:
    pass

StudentTimeline = None
try:
    from student_timeline import StudentTimeline  # type: ignore
except ImportError:
    pass

rate_limit = None
add_rate_limit_headers = None
get_rate_limit_decorator = None
APIUsageAnalytics = None
try:
    from rate_limiter import (  # type: ignore
        rate_limit, add_rate_limit_headers, get_rate_limit_decorator, 
        APIUsageAnalytics
    )
except ImportError:
    pass

LSTMModel = None
try:
    from lstm_model import LSTMModel  # type: ignore
except ImportError:
    pass

StudentPredictor = None
try:
    from predict import StudentPredictor  # type: ignore
except ImportError:
    pass

DataPreprocessor = None
try:
    from data_preprocessing import DataPreprocessor  # type: ignore
except ImportError:
    pass

# ============================================================================
# CONFIGURATION
# ============================================================================

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/elearning_analytics')
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['elearning_analytics']

# Initialize services
alert_service = EmailAlertService()
api_analytics = APIUsageAnalytics()

# ============================================================================
# BEFORE REQUEST HANDLERS & RESPONSE HANDLERS
# ============================================================================

@app.before_request
def before_request():
    """Execute before each request"""
    g.start_time = datetime.now()
    g.request_id = request.headers.get('X-Request-ID', 'none')


@app.after_request
def after_request(response):
    """Add rate limit headers to all responses"""
    try:
        # Add rate limit headers
        response = add_rate_limit_headers(response)
        
        # Record API analytics
        if request.endpoint and hasattr(g, 'start_time'):
            elapsed = (datetime.now() - g.start_time).total_seconds()
            api_analytics.record_request(
                endpoint=request.endpoint,
                status_code=response.status_code,
                response_time=elapsed
            )
    except Exception as e:
        print(f"Error in after_request: {e}")
    
    return response


# ============================================================================
# FEATURE 1: EMAIL ALERTS ROUTES
# ============================================================================

@app.route('/api/alerts/check', methods=['POST'])
@login_required
@get_rate_limit_decorator('moderate')
def check_at_risk_students():
    """
    Check for at-risk students and send email alerts
    Called manually or on a schedule
    """
    try:
        # Load predictions
        predictions_path = os.path.join(
            os.path.dirname(__file__), 'outputs', 'predictions', 'results.csv'
        )
        
        if not os.path.exists(predictions_path):
            return jsonify({'error': 'No predictions available'}), 404
        
        predictions_df = pd.read_csv(predictions_path)
        teacher_email = session.get('email')
        
        at_risk_students = []
        
        # Check each student against thresholds
        for idx, row in predictions_df.iterrows():
            engagement_score = row.get('engagement_score', 0)
            
            # Categorize risk level
            if engagement_score < ALERT_THRESHOLDS['immediate']:
                risk_level = 'CRITICAL'
            elif engagement_score < ALERT_THRESHOLDS['warning']:
                risk_level = 'HIGH'
            elif engagement_score < ALERT_THRESHOLDS['check_in']:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            # Only include at-risk students
            if risk_level != 'LOW':
                student_info = {
                    'id': row.get('student_id'),
                    'name': row.get('name', 'Unknown'),
                    'engagement_score': engagement_score,
                    'risk_level': risk_level,
                    'last_active': row.get('last_active', 'Unknown'),
                    'login_count': row.get('login_count'),
                    'time_spent': row.get('time_spent'),
                    'quiz_score': row.get('quiz_score'),
                    'assignment_score': row.get('assignment_score')
                }
                
                at_risk_students.append(student_info)
                
                # Send email alert if enabled
                if os.getenv('ENABLE_EMAIL_ALERTS', 'False').lower() == 'true':
                    alert_service.send_at_risk_alert(teacher_email, student_info)
        
        # Sort by risk level
        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        at_risk_students.sort(key=lambda x: risk_order.get(x['risk_level'], 999))
        
        return jsonify({
            'success': True,
            'at_risk_count': len(at_risk_students),
            'alerts_sent': len(at_risk_students) if os.getenv('ENABLE_EMAIL_ALERTS') else 0,
            'students': at_risk_students
        })
    
    except Exception as e:
        print(f"Error checking alerts: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/send-summary', methods=['POST'])
@login_required
@get_rate_limit_decorator('moderate')
def send_alert_summary():
    """Send daily summary email of all at-risk students"""
    try:
        teacher_email = session.get('email')
        teacher_name = session.get('name', 'Teacher')
        
        # Get current at-risk students
        predictions_path = os.path.join(
            os.path.dirname(__file__), 'outputs', 'predictions', 'results.csv'
        )
        predictions_df = pd.read_csv(predictions_path)
        
        at_risk_students = []
        for idx, row in predictions_df.iterrows():
            if row.get('engagement_score', 10) < ALERT_THRESHOLDS['check_in']:
                at_risk_students.append({
                    'name': row.get('name'),
                    'engagement_score': row.get('engagement_score'),
                    'risk_level': 'HIGH' if row.get('engagement_score') < 5.5 else 'MEDIUM'
                })
        
        # Send summary if alerts enabled
        if os.getenv('ENABLE_EMAIL_ALERTS', 'False').lower() == 'true' and at_risk_students:
            alert_service.send_daily_summary(
                teacher_email=teacher_email,
                teacher_name=teacher_name,
                at_risk_students=at_risk_students
            )
            
        return jsonify({
            'success': True,
            'message': f'Summary sent for {len(at_risk_students)} at-risk students',
            'count': len(at_risk_students)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/config', methods=['GET'])
@login_required
def get_alert_config():
    """Get current alert configuration"""
    return jsonify({
        'immediate': ALERT_THRESHOLDS['immediate'],
        'warning': ALERT_THRESHOLDS['warning'],
        'check_in': ALERT_THRESHOLDS['check_in'],
        'enable_alerts': os.getenv('ENABLE_EMAIL_ALERTS', 'False').lower() == 'true'
    })


@app.route('/api/alerts/config', methods=['PUT'])
@login_required
def update_alert_config():
    """Update alert configuration"""
    try:
        data = request.json
        
        # Store in database
        user_id = session.get('user_id')
        db.alert_configs.update_one(
            {'user_id': user_id},
            {'$set': {
                'immediate': data.get('immediate', ALERT_THRESHOLDS['immediate']),
                'warning': data.get('warning', ALERT_THRESHOLDS['warning']),
                'check_in': data.get('check_in', ALERT_THRESHOLDS['check_in']),
                'enable_alerts': data.get('enable_alerts', False),
                'alert_frequency': data.get('alert_frequency', 'immediate'),
                'updated_at': datetime.now()
            }},
            upsert=True
        )
        
        return jsonify({'success': True, 'message': 'Configuration updated'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/history', methods=['GET'])
@login_required
@get_rate_limit_decorator('default')
def get_alert_history():
    """Get alert history for current user"""
    try:
        user_id = session.get('user_id')
        
        history = list(db.alert_history.find(
            {'user_id': user_id},
            {'_id': 0}
        ).sort('timestamp', -1).limit(100))
        
        return jsonify(history)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/alerts', methods=['GET'])
@login_required
def alerts_page():
    """Render alerts management page"""
    return render_template('alerts.html')


# ============================================================================
# FEATURE 2: DATA EXPORT ROUTES
# ============================================================================

@app.route('/api/export', methods=['GET'])
@login_required
@get_rate_limit_decorator('export')
def export_data():
    """
    Export predictions in various formats
    Query params:
        format: csv, excel, pdf, json (default: csv)
    """
    try:
        format_type = request.args.get('format', 'csv').lower()
        
        # Load predictions
        predictions_path = os.path.join(
            os.path.dirname(__file__), 'outputs', 'predictions', 'results.csv'
        )
        
        if not os.path.exists(predictions_path):
            return jsonify({'error': 'No predictions available'}), 404
        
        df = pd.read_csv(predictions_path)
        exporter = DataExporter()
        
        # Export to requested format
        if format_type == 'csv':
            data = exporter.export_predictions_to_csv(df)
            filename = exporter.get_export_filename('csv')
            mimetype = 'text/csv'
        
        elif format_type == 'excel':
            data = exporter.export_predictions_to_excel(df)
            filename = exporter.get_export_filename('xlsx')
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        elif format_type == 'pdf':
            data = exporter.generate_pdf_report(
                df, 
                title='Student Predictions Report'
            )
            filename = exporter.get_export_filename('pdf')
            mimetype = 'application/pdf'
        
        elif format_type == 'json':
            data = exporter.export_to_json(df.to_dict('records'))
            filename = exporter.get_export_filename('json')
            mimetype = 'application/json'
        
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        
        # Send file
        return send_file(
            io.BytesIO(data) if isinstance(data, bytes) else io.BytesIO(data.encode()),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"Export error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/analytics', methods=['GET'])
@login_required
@get_rate_limit_decorator('export')
def export_analytics():
    """Export analytics/dashboard data"""
    try:
        format_type = request.args.get('format', 'pdf').lower()
        
        # Create analytics report
        exporter = DataExporter()
        
        # Gather analytics data
        predictions_path = os.path.join(
            os.path.dirname(__file__), 'outputs', 'predictions', 'results.csv'
        )
        df = pd.read_csv(predictions_path)
        
        # Create report data dictionary
        report_data = {
            'total_students': len(df),
            'period': 'Current',
            'high_risk': len(df[df['risk_level'].isin(['HIGH', 'CRITICAL'])]) if 'risk_level' in df.columns else 0,
            'medium_risk': len(df[df['risk_level'] == 'MEDIUM']) if 'risk_level' in df.columns else 0,
            'low_risk': len(df[df['risk_level'] == 'LOW']) if 'risk_level' in df.columns else 0,
            'avg_engagement': df['engagement_score'].mean() if 'engagement_score' in df.columns else 0
        }
        
        analytics_report = exporter.create_analytics_report(report_data)
        
        if format_type == 'pdf':
            data = exporter.generate_pdf_report(df, title='Analytics Report')
            mimetype = 'application/pdf'
            filename = exporter.get_export_filename('pdf')
        
        elif format_type == 'json':
            data = exporter.export_to_json(report_data)
            mimetype = 'application/json'
            filename = exporter.get_export_filename('json')
        
        else:
            return jsonify({'error': 'Unsupported format'}), 400
        
        return send_file(
            io.BytesIO(data) if isinstance(data, bytes) else io.BytesIO(data.encode()),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# FEATURE 3: STUDENT TIMELINE ROUTES
# ============================================================================

@app.route('/api/student/<int:student_id>/timeline', methods=['GET'])
@login_required
@get_rate_limit_decorator('default')
def get_student_timeline(student_id):
    """Get student progress timeline with milestones"""
    try:
        # Load student data
        data_path = os.path.join(
            os.path.dirname(__file__), 'data', 'processed', 'cleaned_data.csv'
        )
        
        if not os.path.exists(data_path):
            return jsonify({'error': 'Student data not available'}), 404
        
        df = pd.read_csv(data_path)
        student_data = df[df['student_id'] == student_id]
        
        if student_data.empty:
            return jsonify({'error': f'Student {student_id} not found'}), 404
        
        # Get student name
        student_name = student_data.iloc[0].get('name', f'Student {student_id}')
        
        # Generate timeline
        timeline_generator = StudentTimeline(student_id, student_name)
        timeline_data = timeline_generator.generate_timeline_data(student_data)
        
        return jsonify(timeline_data)
    
    except Exception as e:
        print(f"Timeline error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/student/<int:student_id>/timeline', methods=['GET'])
@login_required
def student_timeline_page(student_id):
    """Render student timeline page"""
    return render_template('student_timeline.html', student_id=student_id)


@app.route('/api/student/<int:student_id>/timeline/html', methods=['GET'])
@login_required
def get_student_timeline_html(student_id):
    """Get student timeline as HTML"""
    try:
        # Load student data
        data_path = os.path.join(
            os.path.dirname(__file__), 'data', 'processed', 'cleaned_data.csv'
        )
        df = pd.read_csv(data_path)
        student_data = df[df['student_id'] == student_id]
        
        if student_data.empty:
            return "<p>Student not found</p>", 404
        
        # Generate timeline HTML
        timeline_generator = StudentTimeline(student_id)
        html = timeline_generator.generate_timeline_html(student_data)
        
        return html, 200, {'Content-Type': 'text/html'}
    
    except Exception as e:
        return f"Error: {str(e)}", 500


# ============================================================================
# FEATURE 4: RATE LIMITING & ANALYTICS ROUTES
# ============================================================================

@app.route('/api/admin/analytics', methods=['GET'])
@login_required
@get_rate_limit_decorator('default')
def get_api_analytics():
    """Get API usage analytics"""
    try:
        # Verify user is admin
        if session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        analytics = api_analytics.get_analytics()
        
        return jsonify({
            'total_requests': analytics.get('total_requests', 0),
            'endpoints': analytics.get('endpoints', {}),
            'errors': analytics.get('errors', 0),
            'average_response_time': analytics.get('average_response_time', 0)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/rate-limits', methods=['GET'])
@login_required
def get_rate_limits():
    """Get rate limit configuration"""
    try:
        if session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Return rate limit tiers
        return jsonify({
            'tiers': {
                'default': {'requests': 100, 'window': 3600},
                'login': {'requests': 5, 'window': 900},
                'predict': {'requests': 50, 'window': 3600},
                'export': {'requests': 20, 'window': 3600},
                'moderate': {'requests': 30, 'window': 3600}
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# EXISTING ROUTES (Keep your original routes)
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            return render_template('login.html', error='Email and password required')
        
        # Validate user (implementation depends on your auth system)
        user = db.users.find_one({'email': email})
        
        # In a real scenario, validate password with secure hashing
        # For now, we check if user exists (you should add password verification)
        if user and 'password_hash' in user:
            # Password should be validated using secure hashing like bcrypt
            # This is a placeholder - implement proper password validation
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            session['name'] = user.get('name', 'User')
            session['role'] = user.get('role', 'user')
            
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


@app.route('/analytics')
@login_required
def analytics():
    """Analytics page"""
    return render_template('analytics.html')


@app.route('/predictions')
@login_required
def predictions():
    """Predictions page"""
    return render_template('predictions.html')


@app.route('/api/predictions', methods=['GET'])
@login_required
@get_rate_limit_decorator('predict')
def get_predictions():
    """Get student predictions"""
    try:
        predictions_path = os.path.join(
            os.path.dirname(__file__), 'outputs', 'predictions', 'results.csv'
        )
        
        if not os.path.exists(predictions_path):
            return jsonify({'error': 'No predictions available'}), 404
        
        df = pd.read_csv(predictions_path)
        
        return jsonify({
            'count': len(df),
            'predictions': df.to_dict('records')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    return redirect(url_for('login'))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """500 error handler"""
    return render_template('500.html'), 500


@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Rate limit exceeded"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Check configuration
    flask_env = os.getenv('FLASK_ENV', 'development')
    debug_mode = flask_env == 'development'
    
    if debug_mode:
        print("🚀 Starting in DEVELOPMENT mode")
        print(f"⚠️  Email alerts: {os.getenv('ENABLE_EMAIL_ALERTS', 'Disabled')}")
        print(f"📊 Rate limiting: Enabled")
        print(f"📁 Data path: {os.path.join(os.path.dirname(__file__), 'data')}")
        print(f"🗄️  MongoDB: {os.getenv('MONGO_URI', 'localhost:27017')}")
    else:
        print("🚀 Starting in PRODUCTION mode")
        print("⚠️  Running with debug=False")
        # Use Gunicorn in production:
        # gunicorn -w 4 -b 0.0.0.0:5000 app:app
    
    app.run(debug=debug_mode, port=5000)
