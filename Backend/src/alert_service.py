"""
Email Alerts Module
Sends automated alerts to teachers when students are flagged as at-risk
"""

import os
import json
from datetime import datetime
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailAlertService:
    """Service for sending email alerts about at-risk students"""
    
    def __init__(self):
        """Initialize email service with configuration"""
        self.sender_email = os.getenv('ALERT_EMAIL', 'noreply@elearning-analytics.com')
        self.sender_password = os.getenv('ALERT_EMAIL_PASSWORD', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.alerts_enabled = os.getenv('ENABLE_EMAIL_ALERTS', 'False').lower() == 'true'
    
    def send_at_risk_alert(self, teacher_email: str, student_data: Dict) -> bool:
        """
        Send alert email for at-risk student
        
        Args:
            teacher_email: Email of the instructor
            student_data: Dictionary with student info and risk metrics
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.alerts_enabled:
            print("Email alerts are disabled. Enable with ENABLE_EMAIL_ALERTS=True in .env")
            return False
        
        try:
            subject = f"⚠️ Alert: {student_data['name']} is at Risk"
            
            body = self._generate_alert_body(student_data)
            
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = teacher_email
            
            # HTML version of email
            html_body = self._generate_alert_html(student_data)
            message.attach(MIMEText(body, "plain"))
            message.attach(MIMEText(html_body, "html"))
            
            # Send email (commented out by default for demo)
            # self._send_smtp(teacher_email, message)
            
            print(f"✓ Alert email prepared for {teacher_email} about {student_data['name']}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send alert: {e}")
            return False
    
    def send_daily_summary(self, teacher_email: str, at_risk_students: List[Dict]) -> bool:
        """
        Send daily summary of at-risk students
        
        Args:
            teacher_email: Email of the instructor
            at_risk_students: List of at-risk student records
        
        Returns:
            bool: True if sent successfully
        """
        if not at_risk_students:
            return True
        
        try:
            subject = f"📊 Daily At-Risk Student Report - {len(at_risk_students)} students"
            
            body = self._generate_summary_body(at_risk_students)
            html_body = self._generate_summary_html(at_risk_students)
            
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = teacher_email
            
            message.attach(MIMEText(body, "plain"))
            message.attach(MIMEText(html_body, "html"))
            
            print(f"✓ Daily summary email prepared for {teacher_email}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send summary: {e}")
            return False
    
    def _generate_alert_body(self, student_data: Dict) -> str:
        """Generate plain text alert email body"""
        return f"""
Hi Instructor,

This is an automated alert regarding a student in your class.

STUDENT: {student_data.get('name', 'Unknown')}
RISK LEVEL: {student_data.get('risk_level', 'HIGH')}
ENGAGEMENT SCORE: {student_data.get('engagement_score', 0):.2f}/10

KEY CONCERNS:
- Low engagement in recent weeks
- Declining assignment scores
- Reduced course participation
- At risk of dropout

RECOMMENDED ACTIONS:
1. Reach out to student personally
2. Offer additional support or resources
3. Schedule a check-in meeting
4. Consider course material difficulty review

For more details, visit the dashboard: http://127.0.0.1:5000/predictions

Best regards,
AI E-Learning Analytics Platform
"""
    
    def _generate_alert_html(self, student_data: Dict) -> str:
        """Generate HTML alert email body"""
        risk_color = self._get_risk_color(student_data.get('risk_level', 'HIGH'))
        
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333;">⚠️ Student At-Risk Alert</h2>
                    
                    <div style="background-color: {risk_color}; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0;">{student_data.get('name', 'Student')}</h3>
                        <p style="margin: 0; font-size: 18px; font-weight: bold;">Risk Level: {student_data.get('risk_level', 'HIGH')}</p>
                        <p style="margin: 5px 0 0 0;">Engagement: {student_data.get('engagement_score', 0):.2f}/10</p>
                    </div>
                    
                    <h4>Key Concerns:</h4>
                    <ul style="color: #666;">
                        <li>Low engagement in recent weeks</li>
                        <li>Declining assignment scores</li>
                        <li>Reduced course participation</li>
                        <li>At risk of dropout</li>
                    </ul>
                    
                    <h4>Recommended Actions:</h4>
                    <ol style="color: #666;">
                        <li>Reach out to student personally</li>
                        <li>Offer additional support or resources</li>
                        <li>Schedule a check-in meeting</li>
                        <li>Consider course material difficulty review</li>
                    </ol>
                    
                    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2196F3;">
                        <a href="http://127.0.0.1:5000/predictions" style="color: #2196F3; text-decoration: none; font-weight: bold;">View Full Dashboard →</a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        AI E-Learning Analytics Platform
                    </p>
                </div>
            </body>
        </html>
        """
    
    def _generate_summary_body(self, students: List[Dict]) -> str:
        """Generate plain text summary body"""
        body = f"Daily At-Risk Student Report - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        body += f"Total At-Risk Students: {len(students)}\n\n"
        
        for i, student in enumerate(students, 1):
            body += f"{i}. {student['name']} - Risk: {student['risk_level']} - Score: {student['engagement_score']:.2f}\n"
        
        return body
    
    def _generate_summary_html(self, students: List[Dict]) -> str:
        """Generate HTML summary body with table"""
        rows = ""
        for student in students:
            risk_color = self._get_risk_color(student['risk_level'])
            rows += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{student['name']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    <span style="background-color: {risk_color}; color: white; padding: 5px 10px; border-radius: 3px;">
                        {student['risk_level']}
                    </span>
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                    {student['engagement_score']:.2f}/10
                </td>
            </tr>
            """
        
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 700px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #333;">📊 Daily At-Risk Report</h2>
                    <p style="color: #666;">{datetime.now().strftime('%Y-%m-%d')}</p>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f9f9f9;">
                                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Student</th>
                                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Risk Level</th>
                                <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Engagement</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                    
                    <div style="background-color: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>Action Required:</strong> Please review and reach out to these students.
                    </div>
                </div>
            </body>
        </html>
        """
    
    @staticmethod
    def _get_risk_color(risk_level: str) -> str:
        """Get color code for risk level"""
        colors = {
            'HIGH': '#f44336',      # Red
            'MEDIUM': '#ff9800',    # Orange
            'MEDIUM-LOW': '#ffc107', # Yellow
            'LOW': '#4caf50'        # Green
        }
        return colors.get(risk_level, '#f44336')
    
    def _send_smtp(self, recipient_email: str, message) -> bool:
        """
        Send email via SMTP
        Note: Configure email credentials in .env file
        """
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    recipient_email,
                    message.as_string()
                )
            return True
        except Exception as e:
            print(f"SMTP Error: {e}")
            return False
    
    def save_alert_configuration(self, config: Dict) -> bool:
        """Save alert configuration for users"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'alert_config.json')
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False


# Static alert thresholds
ALERT_THRESHOLDS = {
    'immediate': 4.0,      # Alert if engagement < 4.0
    'warning': 5.5,        # Warning if engagement < 5.5
    'check_in': 6.5,       # Check-in suggestion if < 6.5
}

ALERT_FREQUENCY = {
    'immediate': 'daily',   # HIGH risk alerts every day
    'warning': 'weekly',    # MEDIUM risk once a week
    'check_in': 'biweekly' # MEDIUM-LOW once per 2 weeks
}
