"""
Integration Guide for New Features
Shows how to integrate all the new features into the Flask app
"""

# ============================================================================
# 1. EMAIL ALERTS INTEGRATION
# ============================================================================

# In Flask app (Backend/app.py):
"""
from src.alert_service import EmailAlertService, ALERT_THRESHOLDS

alert_service = EmailAlertService()

@app.route('/api/check-at-risk-students', methods=['GET'])
@login_required
def check_at_risk_students():
    '''Check for at-risk students and send alerts'''
    predictions = load_predictions()
    teacher_email = session.get('email')
    
    at_risk_students = []
    for idx, student in predictions.iterrows():
        if student['engagement_score'] < ALERT_THRESHOLDS['immediate']:
            at_risk_students.append({
                'name': student['name'],
                'engagement_score': student['engagement_score'],
                'risk_level': 'HIGH'
            })
            
            # Send alert email
            alert_service.send_at_risk_alert(teacher_email, student)
    
    return jsonify({
        'at_risk_count': len(at_risk_students),
        'students': at_risk_students,
        'alerts_sent': len(at_risk_students)
    })

# Add to dashboard/predictions page
@app.route('/alerts')
@login_required
def alerts_page():
    '''Page to manage and configure alerts'''
    return render_template('alerts.html')
"""

# Required .env variables:
"""
ENABLE_EMAIL_ALERTS=False  # Set to True to enable
ALERT_EMAIL=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
"""


# ============================================================================
# 2. DARK MODE INTEGRATION
# ============================================================================

# In base template (Frontend/templates/base.html or dashboard.html):
"""
<head>
    <!-- Include dark mode CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dark_mode.css') }}">
    <!-- Include dark mode JavaScript -->
    <script src="{{ url_for('static', filename='js/dark_mode.js') }}"></script>
</head>

<body>
    <!-- Rest of your HTML -->
</body>
"""

# JavaScript usage:
"""
// Toggle theme
Theme.toggle();

// Set specific theme
Theme.set('dark-mode');
Theme.set('light-mode');

// Check current theme
if (Theme.isDark()) {
    console.log('Dark mode is on');
}

// Get theme
const current = Theme.get(); // Returns 'dark-mode' or 'light-mode'
"""

# Keyboard shortcut: Press 'T' to toggle theme
# Button appears in bottom-right corner automatically


# ============================================================================
# 3. DATA EXPORT INTEGRATION
# ============================================================================

# In Flask app:
"""
from src.data_export import DataExporter
import pandas as pd

@app.route('/api/export/predictions', methods=['GET'])
@login_required
@rate_limit(max_requests=20, window_seconds=3600)
def export_predictions():
    '''Export predictions to CSV'''
    format_type = request.args.get('format', 'csv')
    
    predictions = load_predictions()
    df = pd.DataFrame(predictions)
    
    exporter = DataExporter()
    
    if format_type == 'csv':
        data = exporter.export_predictions_to_csv(df)
        filename = exporter.get_export_filename('csv')
        return send_file(
            io.BytesIO(data),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    elif format_type == 'excel':
        data = exporter.export_predictions_to_excel(df)
        filename = exporter.get_export_filename('excel')
        return send_file(
            io.BytesIO(data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    elif format_type == 'pdf':
        data = exporter.generate_pdf_report(df, 'Student Predictions Report')
        filename = exporter.get_export_filename('pdf')
        return send_file(
            io.BytesIO(data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    elif format_type == 'json':
        data = exporter.export_to_json(df.to_dict('records'))
        filename = exporter.get_export_filename('json')
        return send_file(
            io.BytesIO(data),
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    
    return jsonify({'error': 'Invalid format'}), 400

# Frontend JavaScript to trigger export
@app.route('/predictions')
@login_required
def predictions():
    return render_template('predictions.html')
"""

# Frontend (in predictions.html):
"""
<div class="export-buttons">
    <button onclick="exportData('csv')" class="btn btn-primary">
        📥 Export as CSV
    </button>
    <button onclick="exportData('excel')" class="btn btn-primary">
        📊 Export as Excel
    </button>
    <button onclick="exportData('pdf')" class="btn btn-primary">
        📄 Export as PDF
    </button>
</div>

<script>
function exportData(format) {
    window.location.href = `/api/export/predictions?format=${format}`;
}
</script>
"""


# ============================================================================
# 4. STUDENT TIMELINE INTEGRATION
# ============================================================================

# In Flask app:
"""
from src.student_timeline import StudentTimeline
import pandas as pd

@app.route('/api/student/<int:student_id>/timeline', methods=['GET'])
@login_required
def get_student_timeline(student_id):
    '''Get student progress timeline'''
    
    # Load student activity data
    data_path = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.csv')
    all_data = pd.read_csv(data_path)
    student_data = all_data[all_data['student_id'] == student_id]
    
    if student_data.empty:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get student name
    student_name = student_data.iloc[0].get('name', f'Student {student_id}')
    
    # Generate timeline
    timeline = StudentTimeline(student_id, student_name)
    timeline_data = timeline.generate_timeline_data(student_data)
    
    return jsonify(timeline_data)

@app.route('/student/<int:student_id>/timeline')
@login_required
def student_timeline_page(student_id):
    '''Render student timeline page'''
    return render_template('student_timeline.html', student_id=student_id)
"""

# Frontend template (student_timeline.html):
"""
<div id="timeline-container"></div>

<script>
// Load and render timeline
const studentId = {{ student_id }};

fetch(`/api/student/${studentId}/timeline`)
    .then(r => r.json())
    .then(data => {
        renderTimeline(data);
    });

function renderTimeline(timeline) {
    let html = `<h2>${timeline.student_name} - Progress Timeline</h2>`;
    
    // Render milestones
    html += '<div class="milestones">';
    timeline.milestones.forEach(m => {
        html += `
            <div class="milestone">
                <span>${m.icon}</span>
                <div>
                    <strong>Week ${m.week}:</strong> ${m.description}
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    document.getElementById('timeline-container').innerHTML = html;
}
</script>
"""


# ============================================================================
# 5. RATE LIMITING INTEGRATION
# ============================================================================

# In Flask app (Backend/app.py):
"""
from src.rate_limiter import (
    rate_limit, add_rate_limit_headers, get_rate_limit_decorator
)

# Add rate limit headers to all responses
@app.after_request
def add_headers(response):
    return add_rate_limit_headers(response)

# Example: Different rate limits for different endpoints
@app.route('/api/login', methods=['POST'])
@get_rate_limit_decorator('login')  # 5 requests per 15 minutes
def login():
    # Login logic...
    pass

@app.route('/api/predict', methods=['POST'])
@get_rate_limit_decorator('predict')  # 50 requests per hour
def predict():
    # Prediction logic...
    pass

@app.route('/api/export/predictions')
@get_rate_limit_decorator('export')  # 20 requests per hour
def export_predictions():
    # Export logic...
    pass

# Multiple endpoints
@app.route('/api/student/progress')
@rate_limit(max_requests=100, window_seconds=3600)
def student_progress():
    # Logic...
    pass
"""

# Response headers:
"""
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 2026-02-26T20:30:45.123456
"""

# Error response when limit exceeded:
"""
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "error": "Rate limit exceeded",
    "message": "Maximum 100 requests per 3600 seconds",
    "retry_after": 3600
}
"""


# ============================================================================
# COMPLETE EXAMPLE: Integrating All Features
# ============================================================================

"""
# In Backend/app.py:

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_file, g
import os, sys, io
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import new modules
from alert_service import EmailAlertService, ALERT_THRESHOLDS
from data_export import DataExporter
from student_timeline import StudentTimeline
from rate_limiter import (
    rate_limit, add_rate_limit_headers, get_rate_limit_decorator, api_analytics
)

# Initialize app and services
app = Flask(__name__)
alert_service = EmailAlertService()

# Register rate limit headers
@app.after_request
def apply_rate_limit_headers(response):
    # Track analytics
    endpoint = request.endpoint or 'unknown'
    status = response.status_code
    api_analytics.record_request(endpoint, status, 0)
    return add_rate_limit_headers(response)

# Alert endpoints
@app.route('/api/alerts/check', methods=['POST'])
@login_required
@get_rate_limit_decorator('moderate')
def check_alerts():
    predictions = load_predictions()
    teacher_email = session.get('email')
    
    at_risk = []
    for idx, student in predictions.iterrows():
        if student['engagement_score'] < ALERT_THRESHOLDS['immediate']:
            at_risk.append(student.to_dict())
            alert_service.send_at_risk_alert(teacher_email, student.to_dict())
    
    return jsonify({'alerts_sent': len(at_risk), 'at_risk_students': at_risk})

# Export endpoints
@app.route('/api/export', methods=['GET'])
@login_required
@get_rate_limit_decorator('export')
def export_data():
    format_type = request.args.get('format', 'csv')
    predictions = pd.read_csv('Backend/outputs/predictions/results.csv')
    
    exporter = DataExporter()
    
    if format_type == 'csv':
        data = exporter.export_predictions_to_csv(predictions)
    elif format_type == 'pdf':
        data = exporter.generate_pdf_report(predictions)
    else:
        return {'error': 'Invalid format'}, 400
    
    return send_file(io.BytesIO(data), as_attachment=True)

# Timeline endpoints
@app.route('/api/student/<int:sid>/timeline', methods=['GET'])
@login_required
@get_rate_limit_decorator('default')
def get_timeline(sid):
    data = pd.read_csv('Backend/data/processed/cleaned_data.csv')
    student_data = data[data['student_id'] == sid]
    
    timeline = StudentTimeline(sid)
    return jsonify(timeline.generate_timeline_data(student_data))

if __name__ == '__main__':
    app.run(debug=True)
"""

print("✅ Integration guide created successfully!")
print("\nNext steps:")
print("1. Copy the code snippets above into your app.py")
print("2. Import the new modules")
print("3. Register the new routes")
print("4. Add the new templates (alerts.html, student_timeline.html)")
print("5. Include CSS/JS files in base templates")
print("6. Test each feature")
