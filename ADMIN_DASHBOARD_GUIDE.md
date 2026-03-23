# 🛡️ ADMIN DASHBOARD - Complete Features & Guide

## Overview
The Admin Dashboard is a comprehensive control center for system administrators to manage users, monitor analytics, and maintain the E-Learning Analytics Platform.

---

## 📋 TABLE OF CONTENTS
1. [Dashboard Components](#dashboard-components)
2. [User Management](#user-management)
3. [Data Management](#data-management)
4. [Audit Logs](#audit-logs)
5. [System Settings](#system-settings)
6. [API Endpoints](#api-endpoints)
7. [Access Control & Security](#access-control--security)

---

## 🎯 Dashboard Components

### 1. **Dashboard Overview Tab** (Home)
The main dashboard displays real-time system statistics:

#### System User Statistics:
- **Total Users**: Count of all registered users in the system
- **Administrators**: Number of admin accounts
- **Teachers**: Number of teacher accounts  
- **Students**: Number of student accounts

#### Learning Analytics Data:
- **Unique Students Tracked**: Total unique students in the learning data
- **Total Data Records**: Complete dataset records for analysis
- **Average Engagement Score**: Mean engagement level (0-10 scale)
- **Completion Rate**: Percentage of students who completed courses (%)

**Visual Features:**
- Color-coded stat cards (Purple for Users, Red for Admins, Teal for Teachers, Green for Students)
- Hover animations for interactivity
- Real-time data updates

---

## 👥 User Management

### Features:
1. **View All Users**
   - Complete list of registered users
   - Displays: Name, Email, Role, Registration Date
   - Role badges with color coding (Red=Admin, Teal=Teacher, Green=Student)

2. **Edit User Role**
   - Change user role from Student → Teacher → Admin
   - Dropdown selector in action buttons
   - Non-destructive changes

3. **Delete User**
   - Remove users from the system
   - Confirmation dialog prevents accidental deletion
   - Cannot delete your own admin account (safety)
   - API call to `/api/admin/users/<user_id>` with DELETE method

4. **User Filtering** (Coming Soon)
   - Filter by role
   - Search by name/email
   - Sort by registration date

### Database Integration:
Users are stored in MongoDB collection `users` with fields:
```json
{
  "_id": ObjectId,
  "name": "string",
  "email": "string",
  "password": "hashed_password",
  "role": "admin|teacher|student",
  "created_at": "ISO timestamp"
}
```

---

## 💾 Data Management

### 1. **Upload New Data**
- **Purpose**: Import student activity data from CSV files
- **Format**: CSV with headers: student_id, week, engagement_score, quiz_score, etc.
- **Location**: `/data/processed/cleaned_data.csv`

### 2. **Export Data**
- **CSV Export**: Download current analytics data in CSV format
- **JSON Export**: Download complete system data in JSON format
- **Use Cases**: Backup, external analysis, reporting

### 3. **Data Refresh**
- Reload predictions from cached results
- Re-run ML model training
- Update statistics

---

## 📊 Audit Logs

### Features:
1. **View Recent Activities**
   - User registration logs
   - Login history (Track admin logins)
   - Data upload/export records
   - System configuration changes

2. **Log Details**
   - Username
   - Email
   - Action type
   - Timestamp

3. **Export Audit Trail**
   - Download logs as CSV
   - Filter by date range
   - Search by user

### Data Captured:
```
User: John Doe
Email: john@example.com
Action: Registered Account
Timestamp: 2026-02-26 10:30:45
```

---

## ⚙️ System Settings

### Configuration Options:

1. **Alert Threshold Settings**
   - **Engagement Score Threshold**: Default = 4.0 (0-10 scale)
   - Students below this score are flagged as "At-Risk"
   - Adjustable range: 0-10

2. **Rate Limiting**
   - **API Requests/Hour**: Default = 100
   - Prevents system overload
   - Different tiers for different endpoints

3. **Email Notifications**
   - Enable/Disable email alerts
   - Configure alert frequency
   - Set recipient email addresses

4. **Model Training Settings**
   - Auto-training schedule
   - Model evaluation metrics
   - Prediction update frequency

5. **User Roles Configuration**
   - Permissions for each role
   - API access levels
   - Feature availability

---

## 🔌 API Endpoints

### Admin-Only API Endpoints:

#### 1. Get All Users
```
GET /api/admin/users
Authentication: Required (Admin role)

Response:
{
  "success": true,
  "total": 5,
  "users": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "admin",
      "created_at": "2026-02-26T10:00:00Z"
    }
  ]
}
```

#### 2. Update User Role
```
PUT /api/admin/users/<user_id>/role
Authentication: Required (Admin role)

Request Body:
{
  "role": "teacher"
}

Response:
{
  "success": true,
  "message": "User role updated to teacher"
}
```

#### 3. Delete User
```
DELETE /api/admin/users/<user_id>
Authentication: Required (Admin role)

Response:
{
  "success": true,
  "message": "User deleted successfully"
}
```

#### 4. Get System Statistics Summary
```
GET /api/admin/stats/summary
Authentication: Required (Admin role)

Response:
{
  "success": true,
  "stats": {
    "total_users": 10,
    "admins": 1,
    "teachers": 3,
    "students": 6,
    "data_records": 1500,
    "unique_students": 45,
    "avg_engagement": 6.8
  }
}
```

#### 5. Get Audit Log
```
GET /api/admin/audit-log
Authentication: Required (Admin role)

Response:
{
  "success": true,
  "total": 50,
  "logs": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "role": "teacher",
      "created_at": "2026-02-26T09:30:00Z"
    }
  ]
}
```

#### 6. Get API Analytics
```
GET /api/admin/analytics
Authentication: Required (Admin role)

Response:
{
  "total_requests": 5432,
  "endpoints": {
    "/api/predictions": {"requests": 234, "errors": 2},
    "/api/alerts": {"requests": 156, "errors": 0}
  },
  "average_response_time": 0.34
}
```

---

## 🔐 Access Control & Security

### Role-Based Access Control:

#### **Student Role**
- ✅ View own dashboard
- ✅ View own progress
- ✅ View predictions
- ❌ Cannot access admin features

#### **Teacher Role**
- ✅ View student analytics
- ✅ Send alerts to students
- ✅ Export student data
- ✅ View class statistics
- ❌ Cannot manage users
- ❌ Cannot access admin features

#### **Admin Role**
- ✅ Full system access
- ✅ User management
- ✅ Data management
- ✅ System configuration
- ✅ Audit logs
- ✅ All analytics
- ✅ API key management
- ✅ Permission management

### Security Features:

1. **Admin Decorator**
   ```python
   @admin_required
   def admin_dashboard():
       # Only admins can access
   ```

2. **Session Management**
   - Role stored in session
   - Checked on each request
   - Auto-logout after 24 hours

3. **Password Security**
   - Passwords hashed with Werkzeug
   - Never stored in plain text
   - Minimum 6 characters

4. **API Security**
   - Rate limiting per endpoint
   - Request validation
   - Error message sanitization

---

## 📱 Registration & Login Flow

### New Admin Registration:

**Step 1: Register Page**
1. Navigate to `/register`
2. Select "Admin" role
3. Enter Name, Email, Password
4. Click Register

**Step 2: Success Message**
- Displays welcome banner
- Shows registered Name & Email
- Confirmation message

**Step 3: Auto-Redirect**
- Redirect to login page (5 second countdown)
- Login with email and password

**Step 4: Dashboard Access**
- Upon login, admin role detected
- Redirect to `/admin/dashboard`
- Full admin access granted

---

## 📈 Dashboard Workflow

### Example Daily Admin Tasks:

1. **Morning Check:**
   ```
   Dashboard → Check user count & engagement stats
             → Review latest audit logs
             → Monitor system health
   ```

2. **User Management:**
   ```
   User Management Tab → View all users
                      → Change roles if needed
                      → Add alerts for inactive users
   ```

3. **Data Operations:**
   ```
   Data Management Tab → Download latest data
                      → Check data integrity
                      → Export for analysis
   ```

4. **System Monitoring:**
   ```
   Settings Tab → Adjust alert thresholds
              → Configure email settings
              → Update rate limits
   ```

---

## 🚀 Future Enhancements

- [ ] User search and filtering
- [ ] Batch user operations
- [ ] Advanced data analytics
- [ ] Custom report generation
- [ ] Backup & restore functionality
- [ ] API key management
- [ ] Two-factor authentication
- [ ] Advanced audit logging
- [ ] Performance dashboards
- [ ] Alert customization UI

---

## 📞 Support & Troubleshooting

### Common Issues:

**Issue**: Cannot access admin dashboard
- **Solution**: Verify your role is set to "admin" in MongoDB users collection

**Issue**: User management showing empty list
- **Solution**: Check MongoDB connection and ensure users are properly registered

**Issue**: API endpoints returning 403
- **Solution**: Verify admin session is active, check browser cookies

---

## ✅ Checklists

### First-Time Admin Setup:
- [ ] Create admin account
- [ ] Log in to admin dashboard
- [ ] Review all user accounts
- [ ] Configure alert thresholds
- [ ] Set up email notifications
- [ ] Review audit logs
- [ ] Test user management features
- [ ] Export sample data

### Regular Maintenance:
- [ ] Weekly user review
- [ ] Monitor system statistics
- [ ] Check audit logs
- [ ] Update security settings
- [ ] Backup data regularly
- [ ] Review performance metrics

---

## 📝 Version History

- **v1.0** - Initial Admin Dashboard Release
  - User management
  - Data management
  - Audit logs
  - System settings
  - Admin authentication

---

**Last Updated:** February 26, 2026
**Admin Dashboard Version:** v1.0
**Status:** Production Ready ✅
