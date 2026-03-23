"""
Data Export Module
Functionality to export predictions, analytics, and reports to CSV and PDF
"""

import io
import csv
import json
from datetime import datetime
from typing import List, Dict, Union
import pandas as pd
# Optional PDF exports support
HAS_REPORTLAB = False
try:
    from reportlab.lib.pagesizes import letter, A4  # type: ignore
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
    from reportlab.lib import colors  # type: ignore
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak  # type: ignore
    from reportlab.lib.units import inch  # type: ignore
    HAS_REPORTLAB = True
except ImportError:
    pass  # PDF exports will be disabled



class DataExporter:
    """Service for exporting data to various formats"""
    
    @staticmethod
    def export_predictions_to_csv(predictions_df: pd.DataFrame) -> bytes:
        """
        Export predictions to CSV format
        
        Args:
            predictions_df: DataFrame with prediction data
        
        Returns:
            bytes: CSV file content
        """
        try:
            buffer = io.StringIO()
            predictions_df.to_csv(buffer, index=False)
            return buffer.getvalue().encode()
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            raise
    
    @staticmethod
    def export_predictions_to_excel(predictions_df: pd.DataFrame) -> bytes:
        """
        Export predictions to Excel format
        
        Args:
            predictions_df: DataFrame with prediction data
        
        Returns:
            bytes: Excel file content
        """
        try:
            buffer = io.BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Write main data
                predictions_df.to_excel(writer, sheet_name='Predictions', index=False)
                
                # Add summary sheet - handle missing columns gracefully
                high_risk = 0
                medium_risk = 0
                low_risk = 0
                avg_engagement = 0
                
                if 'risk_level' in predictions_df.columns:
                    # Count all risk levels, including CRITICAL
                    high_risk = len(predictions_df[predictions_df['risk_level'].isin(['HIGH', 'CRITICAL'])])
                    medium_risk = len(predictions_df[predictions_df['risk_level'] == 'MEDIUM'])
                    low_risk = len(predictions_df[predictions_df['risk_level'] == 'LOW'])
                
                if 'engagement_score' in predictions_df.columns:
                    avg_engagement = predictions_df['engagement_score'].mean()
                
                summary_df = pd.DataFrame({
                    'Metric': ['Total Students', 'High Risk', 'Medium Risk', 'Low Risk', 'Avg Engagement'],
                    'Value': [
                        len(predictions_df),
                        high_risk,
                        medium_risk,
                        low_risk,
                        avg_engagement
                    ]
                })
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            raise
    
    @staticmethod
    def export_to_json(data: Union[Dict, list], filename: str = 'export') -> bytes:
        """
        Export data to JSON format
        
        Args:
            data: Dictionary or list with data to export
            filename: Name for the export (used for metadata)
        
        Returns:
            bytes: JSON file content
        """
        try:
            # If data is a list, wrap it with metadata using filename
            if isinstance(data, list):
                json_data = {
                    'export_name': filename,
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }
            else:
                json_data = data
            
            json_str = json.dumps(json_data, indent=2, default=str)
            return json_str.encode()
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            raise
    
    @staticmethod
    def get_export_filename(format_type: str) -> str:
        """
        Generate filename for export
        
        Args:
            format_type: Type of export (csv, excel, json, pdf)
        
        Returns:
            str: Filename with timestamp
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extensions = {
            'csv': '.csv',
            'excel': '.xlsx',
            'json': '.json',
            'pdf': '.pdf'
        }
        return f"predictions_export_{timestamp}{extensions.get(format_type, '.txt')}"
    
    @staticmethod
    def create_analytics_report(analytics_data: Dict) -> Dict:
        """
        Create comprehensive analytics report
        
        Args:
            analytics_data: Dictionary with analytics metrics
        
        Returns:
            dict: Formatted report data
        """
        return {
            'report_title': 'E-Learning Analytics Report',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_students': analytics_data.get('total_students', 0),
                'reporting_period': analytics_data.get('period', 'Current'),
            },
            'risk_distribution': {
                'high': analytics_data.get('high_risk', 0),
                'medium': analytics_data.get('medium_risk', 0),
                'low': analytics_data.get('low_risk', 0),
            },
            'engagement_metrics': {
                'average': analytics_data.get('avg_engagement', 0),
                'median': analytics_data.get('median_engagement', 0),
                'std_dev': analytics_data.get('std_engagement', 0),
            },
            'recommendations': [
                'Reach out to high-risk students',
                'Provide additional resources for struggling learners',
                'Recognize and reward high-performing students',
                'Review course difficulty and pacing'
            ]
        }

    @staticmethod
    def generate_pdf_report(predictions_df, title: str = "Student Analytics Report", include_summary: bool = True) -> bytes:
        """
        Generate PDF report from predictions
        Requires reportlab library
        
        Args:
            predictions_df: DataFrame with prediction data
            title: Title for the report
            include_summary: Whether to include summary statistics (default: True)
        
        Returns:
            bytes: PDF file content
        """
        if not HAS_REPORTLAB:
            raise ImportError("reportlab is required for PDF export. Install it with: pip install reportlab")
        
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            # Title
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=30,
                alignment=1
            )
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Report metadata
            metadata_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            elements.append(Paragraph(metadata_text, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary section
            elements.append(Paragraph("Summary Statistics", styles['Heading2']))
            # Build summary data with error handling
            high_risk_count = 0
            medium_risk_count = 0
            low_risk_count = 0
            avg_engagement = 0
            
            if 'risk_level' in predictions_df.columns:
                high_risk_count = len(predictions_df[predictions_df['risk_level'].isin(['HIGH', 'CRITICAL'])])
                medium_risk_count = len(predictions_df[predictions_df['risk_level'] == 'MEDIUM'])
                low_risk_count = len(predictions_df[predictions_df['risk_level'] == 'LOW'])
            
            if 'engagement_score' in predictions_df.columns:
                avg_engagement = predictions_df['engagement_score'].mean()
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Students', str(len(predictions_df))],
                ['High Risk', str(high_risk_count)],
                ['Medium Risk', str(medium_risk_count)],
                ['Low Risk', str(low_risk_count)],
                ['Average Engagement', f"{avg_engagement:.2f}/10"],
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.5*inch))
            
            # Detailed data section
            elements.append(PageBreak())
            elements.append(Paragraph("Detailed Student Data", styles['Heading2']))
            
            # Create table from dataframe
            df_data = [list(predictions_df.columns)] + predictions_df.head(20).values.tolist()
            df_table = Table(df_data)
            df_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(df_table)
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()
        
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise
