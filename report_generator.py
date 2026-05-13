from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import io
import pandas as pd
import numpy as np
from datetime import datetime

def generate_pdf_report(user_info, input_data, predicted_score, recommendations, comparison_chart_path=None):
    """Generate PDF report for student"""
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("Student Performance Report", title_style))
    story.append(Spacer(1, 12))
    
    # Student Info
    story.append(Paragraph(f"<b>Student Name:</b> {user_info['full_name']}", styles['Normal']))
    story.append(Paragraph(f"<b>School/College:</b> {user_info['school_name']}", styles['Normal']))
    story.append(Paragraph(f"<b>Grade:</b> {user_info.get('grade', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"<b>Email:</b> {user_info.get('email', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Predicted Score
    story.append(Paragraph("<b>📊 Predicted Exam Score</b>", styles['Heading2']))
    score_style = ParagraphStyle(
        'ScoreStyle',
        parent=styles['Normal'],
        fontSize=48,
        textColor=colors.HexColor('#4CAF50'),
        alignment=1
    )
    story.append(Paragraph(f"{predicted_score}/100", score_style))
    
    # Grade interpretation
    if predicted_score >= 90:
        grade = "A+ (Excellent)"
        message = "Outstanding performance! You're in the top tier."
    elif predicted_score >= 80:
        grade = "A (Very Good)"
        message = "Very good performance! Keep up the momentum."
    elif predicted_score >= 70:
        grade = "B (Good)"
        message = "Good performance. Consistent effort will lead to improvement."
    elif predicted_score >= 60:
        grade = "C (Satisfactory)"
        message = "Satisfactory. More focused study time recommended."
    elif predicted_score >= 50:
        grade = "D (Needs Improvement)"
        message = "Needs improvement. Consider tutoring or study groups."
    else:
        grade = "F (Critical)"
        message = "Critical level. Immediate intervention recommended."
    
    story.append(Paragraph(f"<b>Grade:</b> {grade}", styles['Normal']))
    story.append(Paragraph(f"<b>Interpretation:</b> {message}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Input Parameters
    story.append(Paragraph("<b>📋 Input Parameters</b>", styles['Heading2']))
    input_data_table = [
        ["Parameter", "Value", "Optimal Range"],
        ["Hours Studied", f"{input_data['Hours_Studied']} hrs", "6-8 hrs"],
        ["Attendance", f"{input_data['Attendance']}%", "85-100%"],
        ["Previous Score", f"{input_data['Previous_Scores']}", "70-100"],
        ["Tutoring Sessions", f"{input_data['Tutoring_Sessions']}/week", "2-3 sessions"],
        ["Sleep Hours", f"{input_data['Sleep_Hours']} hrs", "7-9 hrs"],
        ["Physical Activity", f"{input_data['Physical_Activity']} hrs/week", "2-3 hrs"],
        ["Health Status", f"{input_data['Health']}/5", "4-5"],
        ["Motivation", input_data['Motivation_Level'], "High"],
        ["Teacher Quality", input_data['Teacher_Quality'], "Good"],
        ["Parental Involvement", input_data['Parental_Involvement'], "High"],
        ["Peer Influence", input_data['Peer_Influence'], "Positive"]
    ]
    
    table = Table(input_data_table, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Recommendations
    story.append(Paragraph("<b>💡 Personalized Recommendations</b>", styles['Heading2']))
    for i, rec in enumerate(recommendations[:8], 1):
        story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 20))
    
    # Impact Analysis
    story.append(Paragraph("<b>📈 Impact Analysis</b>", styles['Heading2']))
    
    impacts = []
    if input_data['Hours_Studied'] < 6:
        impacts.append("• Low study hours (-15-20 points impact)")
    elif input_data['Hours_Studied'] > 10:
        impacts.append("• Excessive study hours may lead to burnout")
    
    if input_data['Attendance'] < 85:
        impacts.append("• Low attendance (-10-15 points impact)")
    
    if input_data['Sleep_Hours'] < 7:
        impacts.append("• Insufficient sleep affects memory and focus (-5-10 points)")
    
    if input_data['Motivation_Level'] != "High":
        impacts.append("• Motivation level affects consistency and effort (-8-12 points)")
    
    if input_data['Teacher_Quality'] != "Good":
        impacts.append("• Teacher quality influences understanding (-5-10 points)")
    
    if input_data['Parental_Involvement'] != "High":
        impacts.append("• Parental involvement correlates with academic success")
    
    if not impacts:
        impacts.append("• You're on the right track! Continue maintaining good habits")
    
    for impact in impacts:
        story.append(Paragraph(impact, styles['Normal']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 20))
    
    # Add comparison chart if provided
    if comparison_chart_path:
        try:
            img = Image(comparison_chart_path, width=6*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 20))
        except:
            pass
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = "This report is generated based on predictive analysis using historical student performance data. Actual results may vary."
    story.append(Paragraph(footer_text, styles['Italic']))
    
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer
