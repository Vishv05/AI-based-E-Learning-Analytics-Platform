# 🚀 Quick Reference - API Endpoints & Usage

## Email Alerts API

### Check At-Risk Students
```
POST /api/alerts/check
Authentication: Required (login_required)
Rate Limit: Moderate tier

Response:
{
  "success": true,
  "at_risk_count": 5,
  "alerts_sent": 5,
  "students": [
    {
      "id": 42,
      "name": "John Doe",
      "engagement_score": 3.8,
      "risk_level": "CRITICAL",
      "last_active": "2024-02-20",
      "login_count": 5,
      "time_spent": 12.5,
      "quiz_score": 65,
      "assignment_score": 70
    }
  ]
}
```

### Send Daily Summary
```
POST /api/alerts/send-summary
Authentication: Required
Rate Limit: Moderate tier

Response:
{
  "success": true,
  "message": "Summary sent for X at-risk students",
  "count": 5
}
```

### Get Alert Configuration
```
GET /api/alerts/config
Authentication: Required
Rate Limit: Default tier

Response:
{
  "immediate": 4.0,
  "warning": 5.5,
  "check_in": 6.5,
  "enable_alerts": false
}
```

### Update Alert Configuration
```
PUT /api/alerts/config
Authentication: Required
Content-Type: application/json

Body:
{
  "immediate": 4.0,
  "warning": 5.5,
  "check_in": 6.5,
  "enable_alerts": true,
  "alert_frequency": "daily"
}

Response:
{
  "success": true,
  "message": "Configuration updated"
}
```

### Get Alert History
```
GET /api/alerts/history
Authentication: Required
Rate Limit: Default tier
Query Params: (optional) limit=100

Response:
[
  {
    "timestamp": "2024-02-26T10:30:45Z",
    "student_name": "John Doe",
    "alert_type": "at_risk",
    "status": "sent"
  },
  ...
]
```

### View Alert Management Page
```
GET /alerts
Authentication: Required

Response: HTML page with alerts dashboard
```

---

## Data Export API

### Export Predictions
```
GET /api/export
Authentication: Required
Rate Limit: Export tier (20 requests/hour)
Query Params:
  - format: csv | excel | pdf | json (default: csv)

Examples:
  GET /api/export?format=csv
  GET /api/export?format=excel
  GET /api/export?format=pdf
  GET /api/export?format=json

Response: File download
  - Content-Type: text/csv | application/vnd.openxmlformats... | application/pdf | application/json
  - Content-Disposition: attachment; filename="predictions-2024-02-26.csv"
```

### Export Analytics Report
```
GET /api/export/analytics
Authentication: Required
Rate Limit: Export tier
Query Params:
  - format: pdf | json (default: pdf)

Response: File download (PDF or JSON analytics report)
```

---

## Student Timeline API

### Get Timeline (JSON)
```
GET /api/student/<student_id>/timeline
Authentication: Required
Rate Limit: Default tier

Example:
  GET /api/student/42/timeline

Response:
{
  "student_id": 42,
  "student_name": "John Doe",
  "milestones": [
    {
      "week": 1,
      "icon": "🎓",
      "title": "Course Started",
      "description": "Student enrolled in course",
      "type": "milestone-event"
    },
    {
      "week": 3,
      "icon": "📈",
      "title": "High Quiz Score",
      "description": "Achieved 95% on quiz",
      "type": "milestone-achievement"
    }
  ],
  "summary": {
    "status": "good",
    "current_engagement": 7.2,
    "weeks_tracked": 8,
    "weekly_engagement": [6.5, 6.8, 7.0, 7.2, 7.1, 7.3, 7.4, 7.2],
    "engagement_trend": [6.5, 6.72, 6.94, 7.16, 7.38, 7.60, 7.82, ...]
  },
  "weekly_details": [
    {
      "week": 1,
      "login_count": 3,
      "time_spent": 4.5,
      "quiz_count": 1,
      "assignment_count": 1,
      "forum_posts": 2,
      "engagement_score": 6.5
    },
    ...
  ]
}
```

### Get Timeline (HTML)
```
GET /api/student/<student_id>/timeline/html
Authentication: Required
Rate Limit: Default tier

Response: HTML string (raw HTML for embedding)
```

### View Timeline Page
```
GET /student/<student_id>/timeline
Authentication: Required

Example:
  GET /student/42/timeline

Response: HTML page with timeline visualization
```

---

## Rate Limiting API

### Get API Analytics
```
GET /api/admin/analytics
Authentication: Required
Authorization: admin role only
Rate Limit: Default tier

Response:
{
  "total_requests": 5432,
  "endpoints": {
    "/api/alerts/check": {
      "requests": 45,
      "errors": 2,
      "avg_response_time": 0.23
    },
    "/api/export": {
      "requests": 23,
      "errors": 0,
      "avg_response_time": 1.45
    },
    ...
  },
  "errors": 5,
  "average_response_time": 0.34
}
```

### Get Rate Limit Configuration
```
GET /api/admin/rate-limits
Authentication: Required
Authorization: admin role only

Response:
{
  "tiers": {
    "default": { "requests": 100, "window": 3600 },
    "login": { "requests": 5, "window": 900 },
    "predict": { "requests": 50, "window": 3600 },
    "export": { "requests": 20, "window": 3600 },
    "moderate": { "requests": 30, "window": 3600 }
  }
}
```

### Response Headers (All Endpoints)
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 2024-02-26T20:30:45.123456Z
```

### When Rate Limited (429 Error)
```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 2024-02-26T20:45:30.123456Z

{
  "error": "Rate limit exceeded",
  "message": "Maximum 100 requests per 3600 seconds",
  "retry_after": 3600
}
```

---

## Dark Mode API

### JavaScript API (Client-Side)
```javascript
// Get current theme
const currentTheme = Theme.get();  // Returns: 'light-mode' or 'dark-mode'

// Set theme
Theme.set('dark-mode');
Theme.set('light-mode');

// Toggle theme
Theme.toggle();

// Check if dark mode active
if (Theme.isDark()) {
  console.log('Dark mode is on');
}

// Listen to theme changes
document.addEventListener('themechange', (e) => {
  console.log('Theme changed to:', e.detail.theme);
});
```

### Keyboard Shortcut
```
Press 'T' to toggle between light and dark mode
(Works globally, doesn't trigger in form inputs)
```

### Automatic Detection
```
- System dark mode preference is detected on page load
- Updates in real-time if user changes OS settings
- User preference overrides system setting
- Persists in localStorage as 'elearning-theme'
```

---

## Frontend Integration Snippets

### Add Dark Mode to Template
```html
<head>
  <!-- Dark mode CSS -->
  <link rel="stylesheet" href="{{ url_for('static', filename='css/dark_mode.css') }}">
</head>
<body>
  <!-- Page content -->
  
  <!-- Dark mode JavaScript -->
  <script src="{{ url_for('static', filename='js/dark_mode.js') }}"></script>
</body>
```

### Add Export Buttons
```html
<div class="export-buttons">
  <button onclick="exportData('csv')" class="btn btn-primary">
    📥 Export CSV
  </button>
  <button onclick="exportData('excel')" class="btn btn-primary">
    📊 Export Excel
  </button>
  <button onclick="exportData('pdf')" class="btn btn-primary">
    📄 Export PDF
  </button>
</div>

<script>
function exportData(format) {
  window.location.href = `/api/export?format=${format}`;
}
</script>
```

### Add Timeline Link
```html
<a href="/student/{{ student.id }}/timeline" class="btn btn-info">
  📅 View Timeline
</a>
```

### Check Alerts
```javascript
fetch('/api/alerts/check', { method: 'POST' })
  .then(r => r.json())
  .then(data => {
    console.log(`${data.at_risk_count} at-risk students`);
    console.log(`${data.alerts_sent} alerts sent`);
  });
```

---

## Environment Configuration (.env)

### Required for Email Alerts
```env
ENABLE_EMAIL_ALERTS=False
ALERT_EMAIL=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Optional Configuration
```env
# Rate Limiting
RATE_LIMIT_ENABLED=True

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-random-secret-key

# MongoDB
MONGO_URI=mongodb://localhost:27017/elearning_analytics

# Application
APP_NAME=E-Learning Analytics
APP_DESCRIPTION=AI-based Student Progress Tracking
```

---

## Common Workflows

### Workflow 1: Check & Alert At-Risk Students
```python
# 1. Check for at-risk students
response = requests.post(
    'http://localhost:5000/api/alerts/check',
    headers={'Authorization': 'Bearer ' + token}
)
at_risk = response.json()['students']

# 2. View specific student timeline
timeline_response = requests.get(
    f'http://localhost:5000/api/student/{student_id}/timeline',
    headers={'Authorization': 'Bearer ' + token}
)
timeline = timeline_response.json()

# 3. Send summary email
requests.post(
    'http://localhost:5000/api/alerts/send-summary',
    headers={'Authorization': 'Bearer ' + token}
)
```

### Workflow 2: Export Student Data
```python
# 1. Export as CSV
csv_response = requests.get(
    'http://localhost:5000/api/export?format=csv',
    headers={'Authorization': 'Bearer ' + token}
)
with open('predictions.csv', 'wb') as f:
    f.write(csv_response.content)

# 2. Export as PDF
pdf_response = requests.get(
    'http://localhost:5000/api/export?format=pdf',
    headers={'Authorization': 'Bearer ' + token}
)
with open('report.pdf', 'wb') as f:
    f.write(pdf_response.content)
```

### Workflow 3: Monitor API Usage
```python
# Get analytics
analytics = requests.get(
    'http://localhost:5000/api/admin/analytics',
    headers={'Authorization': 'Bearer ' + admin_token}
).json()

# Check rate limits
limits = requests.get(
    'http://localhost:5000/api/admin/rate-limits',
    headers={'Authorization': 'Bearer ' + admin_token}
).json()
```

---

## HTTP Status Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid query params or JSON |
| 401 | Unauthorized | Not logged in, missing token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Student or resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Unexpected server error |

---

## Rate Limit Tiers

| Tier | Requests | Window | Use For |
|------|----------|--------|---------|
| login | 5 | 15 min | Login attempts |
| predict | 50 | 1 hour | Predictions |
| export | 20 | 1 hour | Data exports |
| moderate | 30 | 1 hour | Alerts, moderate endpoints |
| default | 100 | 1 hour | General API calls |

---

## troubleshooting Quick Reference

**501 Error on Export?**
→ Copy file exists: `Backend/outputs/predictions/results.csv`

**429 Too Many Requests?**
→ Wait for X-RateLimit-Reset time, or check tier limits

**Email not sending?**
→ Enable alerts: `ENABLE_EMAIL_ALERTS=True` and set SMTP credentials

**Dark mode not working?**
→ Check dark_mode.js loaded: Open browser console, no errors?

**Timeline returns empty?**
→ Check student_id exists in `cleaned_data.csv`

**Rate limit headers missing?**
→ Verify after_request handler registered in app.py

---

## Print-Friendly Endpoints Summary

```
ALERTS:
  POST   /api/alerts/check
  POST   /api/alerts/send-summary
  GET    /api/alerts/config
  PUT    /api/alerts/config
  GET    /api/alerts/history
  GET    /alerts

EXPORT:
  GET    /api/export?format={csv|excel|pdf|json}
  GET    /api/export/analytics?format={pdf|json}

TIMELINE:
  GET    /api/student/<id>/timeline
  GET    /api/student/<id>/timeline/html
  GET    /student/<id>/timeline

ADMIN:
  GET    /api/admin/analytics
  GET    /api/admin/rate-limits

DARK MODE: (Client-side only)
  Theme.get()    - Get current theme
  Theme.set()    - Set theme
  Theme.toggle() - Toggle theme
  Theme.isDark() - Check if dark
  Keyboard: Press 'T' to toggle
```

---

**Last Updated:** February 26, 2024  
**Quick Reference v1.0**  
**Print this page for easy reference while integrating!**
