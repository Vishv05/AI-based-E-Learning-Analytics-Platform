"""
Student Timeline Visualization Module
Creates visual timeline of student progress and milestones
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class StudentTimeline:
    """Generate and manage student progress timeline"""
    
    # Milestone definitions
    MILESTONES = {
        'course_start': {'icon': '🚀', 'label': 'Course Started'},
        'first_assignment': {'icon': '📝', 'label': 'First Assignment'},
        'quiz_perfect': {'icon': '🎯', 'label': 'Perfect Quiz Score'},
        'forum_first_post': {'icon': '💬', 'label': 'First Forum Post'},
        'midway': {'icon': '⏱️', 'label': 'Course Halfway'},
        'assignment_late': {'icon': '⏰', 'label': 'Late Submission'},
        'forum_helper': {'icon': '🤝', 'label': 'Helped 5 Peers'},
        'video_completion': {'icon': '✅', 'label': 'Video Series Complete'},
        'engagement_drop': {'icon': '📉', 'label': 'Engagement Declining'},
        'recovery': {'icon': '📈', 'label': 'Engagement Recovering'},
        'course_complete': {'icon': '🏆', 'label': 'Course Completed'},
    }
    
    def __init__(self, student_id: int, student_name: str = None):
        """
        Initialize timeline for a student
        
        Args:
            student_id: ID of the student
            student_name: Name of the student
        """
        self.student_id = student_id
        self.student_name = student_name or f"Student {student_id}"
        self.events = []
        self.milestones = []
    
    def add_event(self, week: int, event_type: str, value: float, note: str = None):
        """
        Add an event to the timeline
        
        Args:
            week: Week number (1-based)
            event_type: Type of event (engagement, score, etc)
            value: Numeric value for the event
            note: Optional note/description
        """
        self.events.append({
            'week': week,
            'type': event_type,
            'value': value,
            'note': note,
            'date': self._calculate_date(week)
        })
    
    def detect_milestones(self, activity_data: pd.DataFrame) -> List[Dict]:
        """
        Detect milestones from activity data
        
        Args:
            activity_data: DataFrame with student activity
        
        Returns:
            list: List of detected milestones
        """
        milestones = []
        
        # Course start milestone (first week with activity)
        if len(activity_data) > 0:
            milestones.append({
                'week': activity_data.iloc[0]['week'],
                'type': 'course_start',
                'description': 'Course Started',
                'icon': self.MILESTONES['course_start']['icon']
            })
        
        # First assignment milestone
        assignment_weeks = activity_data[activity_data['assignment_score'] > 0]['week'].values
        if len(assignment_weeks) > 0:
            milestones.append({
                'week': int(assignment_weeks[0]),
                'type': 'first_assignment',
                'description': 'First Assignment Submitted',
                'icon': self.MILESTONES['first_assignment']['icon']
            })
        
        # Perfect quiz milestone
        perfect_quizzes = activity_data[activity_data['quiz_score'] >= 95]['week'].values
        if len(perfect_quizzes) > 0:
            milestones.append({
                'week': int(perfect_quizzes[0]),
                'type': 'quiz_perfect',
                'description': f"Perfect Quiz Score ({perfect_quizzes[0]})",
                'icon': self.MILESTONES['quiz_perfect']['icon']
            })
        
        # Forum participation milestone
        forum_weeks = activity_data[activity_data['forum_posts'] > 0]['week'].values
        if len(forum_weeks) > 0:
            milestones.append({
                'week': int(forum_weeks[0]),
                'type': 'forum_first_post',
                'description': 'First Forum Post',
                'icon': self.MILESTONES['forum_first_post']['icon']
            })
        
        # Course completion milestone
        if len(activity_data) > 0 and activity_data.iloc[-1]['course_progress'] >= 100:
            milestones.append({
                'week': int(activity_data.iloc[-1]['week']),
                'type': 'course_complete',
                'description': '🏆 Course Completed!',
                'icon': self.MILESTONES['course_complete']['icon']
            })
        
        # Engagement drop detection
        if len(activity_data) >= 4:
            recent_engagement = activity_data.iloc[-2:]['engagement_score'].mean()
            previous_engagement = activity_data.iloc[-4:-2]['engagement_score'].mean()
            
            if recent_engagement < previous_engagement - 1.0:
                milestones.append({
                    'week': int(activity_data.iloc[-1]['week']),
                    'type': 'engagement_drop',
                    'description': 'Engagement Declining - Check In Needed',
                    'icon': self.MILESTONES['engagement_drop']['icon'],
                    'severity': 'warning'
                })
        
        self.milestones = milestones
        return milestones
    
    def generate_timeline_data(self, activity_data: pd.DataFrame) -> Dict:
        """
        Generate complete timeline data for visualization
        
        Args:
            activity_data: DataFrame with student activity
        
        Returns:
            dict: Timeline data ready for frontend visualization
        """
        self.detect_milestones(activity_data)
        
        timeline_data = {
            'student_id': self.student_id,
            'student_name': self.student_name,
            'total_weeks': len(activity_data),
            'milestones': self.milestones,
            'week_by_week': []
        }
        
        # Add week-by-week breakdown
        for idx, row in activity_data.iterrows():
            week_data = {
                'week': int(row['week']),
                'engagement_score': float(row['engagement_score']),
                'quiz_score': float(row['quiz_score']),
                'assignment_score': float(row['assignment_score']),
                'course_progress': float(row['course_progress']),
                'login_count': int(row['login_count']),
                'time_spent_hours': float(row['time_spent_hours']),
                'forum_posts': int(row['forum_posts']),
                'video_completion_rate': float(row['video_completion_rate']),
                'status': self._determine_status(row['engagement_score']),
                'date': self._calculate_date(int(row['week']))
            }
            timeline_data['week_by_week'].append(week_data)
        
        # Add summary statistics
        timeline_data['summary'] = {
            'start_engagement': float(activity_data.iloc[0]['engagement_score']),
            'end_engagement': float(activity_data.iloc[-1]['engagement_score']),
            'avg_engagement': float(activity_data['engagement_score'].mean()),
            'engagement_trend': self._calculate_trend(activity_data['engagement_score']),
            'peak_week': int(activity_data.loc[activity_data['engagement_score'].idxmax(), 'week']),
            'low_week': int(activity_data.loc[activity_data['engagement_score'].idxmin(), 'week']),
            'total_assignments': int(activity_data['assignment_score'].gt(0).sum()),
            'total_forum_posts': int(activity_data['forum_posts'].sum()),
            'avg_study_hours': float(activity_data['time_spent_hours'].mean())
        }
        
        return timeline_data
    
    def generate_timeline_html(self, activity_data: pd.DataFrame) -> str:
        """
        Generate HTML for timeline visualization
        
        Args:
            activity_data: DataFrame with student activity
        
        Returns:
            str: HTML timeline code
        """
        timeline = self.generate_timeline_data(activity_data)
        
        html = '<div class="student-timeline">\n'
        html += f'<h2>Timeline for {self.student_name}</h2>\n'
        html += '<div class="timeline-container">\n'
        
        # Milestones
        html += '<div class="milestones">\n'
        for milestone in timeline['milestones']:
            severity_class = milestone.get('severity', 'info')
            html += f'''
            <div class="milestone {severity_class}" data-week="{milestone['week']}">
                <span class="milestone-icon">{milestone['icon']}</span>
                <div class="milestone-content">
                    <strong>Week {milestone['week']}</strong>
                    <p>{milestone['description']}</p>
                </div>
            </div>
            '''
        html += '</div>\n'
        
        # Week-by-week breakdown
        html += '<div class="week-by-week">\n'
        for week in timeline['week_by_week']:
            status_class = week['status'].lower()
            html += f'''
            <div class="week-card {status_class}">
                <h4>Week {week['week']}</h4>
                <ul>
                    <li>📊 Engagement: {week['engagement_score']:.1f}/10</li>
                    <li>🎯 Quiz: {week['quiz_score']:.0f}%</li>
                    <li>📝 Assignment: {week['assignment_score']:.0f}%</li>
                    <li>📈 Progress: {week['course_progress']:.0f}%</li>
                    <li>⏱️ Study: {week['time_spent_hours']:.1f}h</li>
                    <li>💬 Posts: {week['forum_posts']}</li>
                </ul>
            </div>
            '''
        html += '</div>\n'
        
        # Summary
        summary = timeline['summary']
        html += f'''
        <div class="timeline-summary">
            <h3>Summary Statistics</h3>
            <div class="summary-grid">
                <div class="stat">
                    <strong>Engagement Trend</strong>
                    <p>{self._trend_arrow(summary['engagement_trend'])} {summary['engagement_trend']:.2f}</p>
                </div>
                <div class="stat">
                    <strong>Average Engagement</strong>
                    <p>{summary['avg_engagement']:.1f}/10</p>
                </div>
                <div class="stat">
                    <strong>Peak Week</strong>
                    <p>Week {summary['peak_week']}</p>
                </div>
                <div class="stat">
                    <strong>Study Hours</strong>
                    <p>{summary['avg_study_hours']:.1f}h/week</p>
                </div>
            </div>
        </div>
        '''
        
        html += '</div>\n</div>\n'
        return html
    
    @staticmethod
    def _calculate_date(week: int) -> str:
        """Calculate date from week number"""
        start_date = datetime(2024, 1, 1)
        target_date = start_date + timedelta(weeks=week - 1)
        return target_date.strftime('%Y-%m-%d')
    
    @staticmethod
    def _determine_status(engagement_score: float) -> str:
        """Determine status based on engagement score"""
        if engagement_score >= 8:
            return 'excellent'
        elif engagement_score >= 6:
            return 'good'
        elif engagement_score >= 4:
            return 'fair'
        else:
            return 'poor'
    
    @staticmethod
    def _calculate_trend(engagement_series) -> float:
        """Calculate engagement trend (slope)"""
        if len(engagement_series) < 2:
            return 0
        x = np.arange(len(engagement_series))
        z = np.polyfit(x, engagement_series.values, 1)
        return z[0]  # Return slope
    
    @staticmethod
    def _trend_arrow(trend_value: float) -> str:
        """Get arrow emoji based on trend"""
        if trend_value > 0.1:
            return '📈'
        elif trend_value < -0.1:
            return '📉'
        else:
            return '➡️'
