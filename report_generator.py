from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

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
        alignment=1
    )
    story.append(Paragraph("Student Performance Report", title_style))
    story.append(Spacer(1, 12))
    
    # Student Info
    story.append(Paragraph(f"<b>Student Name:</b> {user_info['full_name']}", styles['Normal']))
    story.append(Paragraph(f"<b>School/College:</b> {user_info['school_name']}", styles['Normal']))
    if user_info.get('grade'):
        story.append(Paragraph(f"<b>Grade:</b> {user_info['grade']}", styles['Normal']))
    if user_info.get('email'):
        story.append(Paragraph(f"<b>Email:</b> {user_info['email']}", styles['Normal']))
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
    story.append(Spacer(1, 10))
    
    # Grade interpretation
    if predicted_score >= 90:
        grade = "A+ (Excellent)"
        message = "Outstanding performance! You're in the top tier."
        color = colors.HexColor('#4CAF50')
    elif predicted_score >= 80:
        grade = "A (Very Good)"
        message = "Very good performance! Keep up the momentum."
        color = colors.HexColor('#8BC34A')
    elif predicted_score >= 70:
        grade = "B (Good)"
        message = "Good performance. Consistent effort will lead to improvement."
        color = colors.HexColor('#FFC107')
    elif predicted_score >= 60:
        grade = "C (Satisfactory)"
        message = "Satisfactory. More focused study time recommended."
        color = colors.HexColor('#FF9800')
    elif predicted_score >= 50:
        grade = "D (Needs Improvement)"
        message = "Needs improvement. Consider tutoring or study groups."
        color = colors.HexColor('#FF5722')
    else:
        grade = "F (Critical)"
        message = "Critical level. Immediate intervention recommended."
        color = colors.HexColor('#f44336')
    
    story.append(Paragraph(f"<b>Grade:</b> {grade}", styles['Normal']))
    story.append(Paragraph(f"<b>Interpretation:</b> {message}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Key Metrics
    story.append(Paragraph("<b>📋 Key Metrics</b>", styles['Heading2']))
    metrics_data = [
        ["Metric", "Your Value", "Optimal Range", "Status"],
        ["Hours Studied", f"{input_data['Hours_Studied']} hrs", "6-8 hrs", 
         "Good" if 6 <= input_data['Hours_Studied'] <= 8 else "Needs Improvement"],
        ["Attendance", f"{input_data['Attendance']}%", "85-100%",
         "Good" if input_data['Attendance'] >= 85 else "Needs Improvement"],
        ["Previous Score", f"{input_data['Previous_Scores']}", "70-100",
         "Good" if input_data['Previous_Scores'] >= 70 else "Needs Improvement"],
        ["Sleep Hours", f"{input_data['Sleep_Hours']} hrs", "7-9 hrs",
         "Good" if 7 <= input_data['Sleep_Hours'] <= 9 else "Needs Improvement"],
        ["Motivation", input_data['Motivation_Level'], "High",
         "Good" if input_data['Motivation_Level'] == "High" else "Needs Improvement"],
        ["Teacher Quality", input_data['Teacher_Quality'], "Good",
         "Good" if input_data['Teacher_Quality'] == "Good" else "Needs Improvement"],
    ]
    
    table = Table(metrics_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Recommendations
    story.append(Paragraph("<b>💡 Personalized Recommendations</b>", styles['Heading2']))
    for i, rec in enumerate(recommendations[:6], 1):
        story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 20))
    
    # Impact Analysis
    story.append(Paragraph("<b>📈 Key Areas for Improvement</b>", styles['Heading2']))
    
    impacts = []
    if input_data['Hours_Studied'] < 6:
        impacts.append("• Study Hours: Increase to 6-8 hours per day")
    if input_data['Attendance'] < 85:
        impacts.append("• Attendance: Maintain 85%+ attendance")
    if input_data['Sleep_Hours'] < 7:
        impacts.append("• Sleep: Get 7-9 hours of quality sleep")
    if input_data['Motivation_Level'] != "High":
        impacts.append("• Motivation: Set daily goals and rewards")
    if input_data['Teacher_Quality'] != "Good":
        impacts.append("• Teacher Quality: Seek additional learning resources")
    if input_data['Parental_Involvement'] != "High":
        impacts.append("• Parental Involvement: Discuss studies with parents")
    
    if impacts:
        for impact in impacts[:5]:
            story.append(Paragraph(impact, styles['Normal']))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("✓ All metrics are optimal! Great job maintaining good habits.", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = "This report is generated based on predictive analysis using historical student performance data. Actual results may vary. For best results, follow the recommendations above."
    story.append(Paragraph(footer_text, styles['Italic']))
    
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer
