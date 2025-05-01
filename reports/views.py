# reports/views.py
import json
import datetime
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Report, ReportCategory
from .report_builder import ReportBuilder
from students.models import Student

# Import the evaluation function from the evaluation module.
# In a real scenario, you should implement compute_evaluation_metrics() in reports/evaluation.py.
from .evaluation import compute_evaluation_metrics

def reports_list(request):
    """
    Displays a list of all reports.
    """
    reports = Report.objects.all()
    return render(request, "reports/reports_list.html", {"reports": reports})

def view_report(request, report_id):
    """
    Displays a detailed view of a single report.
    """
    report = get_object_or_404(Report, pk=report_id)
    return render(request, "reports/view_report.html", {"report": report})

def reports_by_category(request, category):
    """
    Displays reports filtered by category.
    """
    reports = Report.objects.filter(category=category)
    # Convert the category code to its display text using ReportCategory.choices.
    category_display = dict(ReportCategory.choices).get(category, category)
    return render(request, "reports/reports_by_category.html", {"reports": reports, "category": category_display})

def auto_generate_reports(request):
    """
    Automatically generate reports for all active students based on a selected category.
    """
    if request.method == "POST":
        selected_category = request.POST.get("report_category")
        students = Student.objects.filter(is_active=True)
        generated_count = 0
        for student in students:
            builder = ReportBuilder(student, selected_category)
            builder.build()
            generated_count += 1
        message = f"{generated_count} reports generated for category '{selected_category}'."
        return render(request, "reports/auto_generate_reports.html", {"message": message})
    else:
        return render(request, "reports/auto_generate_reports.html")

def export_reports_pdf_view(request):
    """
    Exports all reports as a PDF document.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    reports = Report.objects.all()
    response = HttpResponse(content_type='application/pdf')
    filename = f'reports_{datetime.datetime.now().strftime("%Y%m%d")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    pdf = canvas.Canvas(response, pagesize=letter)
    y = 750
    for report in reports:
        if y < 100:
            pdf.showPage()
            y = 750
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y, f"Report for {report.student.full_name} - {report.get_category_display()}")
        y -= 20
        pdf.setFont("Helvetica", 10)
        pdf.drawString(100, y, f"Report Type: {report.report_type} | Generated At: {report.generated_at}")
        y -= 25
        if isinstance(report.data, dict):
            for key, value in report.data.items():
                pdf.drawString(120, y, f"{key}: {value}")
                y -= 15
                if y < 100:
                    pdf.showPage()
                    y = 750
        else:
            pdf.drawString(120, y, f"Data: {report.data}")
            y -= 15
        y -= 20
    pdf.save()
    return response

def export_reports_csv_view(request):
    """
    Exports all reports as a CSV file.
    """
    import csv
    reports = Report.objects.all()
    response = HttpResponse(content_type='text/csv')
    filename = f'reports_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(["Student", "Category", "Report Type", "Generated At", "Data"])
    for report in reports:
        writer.writerow([
            report.student.full_name,
            report.get_category_display(),
            report.report_type,
            report.generated_at,
            report.data,
        ])
    return response

def generate_single_student_report(request, student_id):
    """
    Generates a report for a single student based on the selected report category.
    """
    student = get_object_or_404(Student, pk=student_id)
    if request.method == "POST":
        selected_category = request.POST.get("report_category")
        builder = ReportBuilder(student, selected_category)
        new_report = builder.build()
        return redirect('view_report', report_id=new_report.id)
    else:
        return render(request, "reports/generate_single.html", {"student": student})

def import_reports_csv_view(request):
    """
    Allows the user to upload a CSV file to import reports.
    """
    import csv, io, json
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            return render(request, "reports/import_reports.html", {"error_message": "No file was uploaded."})
        if not csv_file.name.endswith(".csv"):
            return render(request, "reports/import_reports.html", {"error_message": "Please upload a valid CSV file (must end with .csv)."})
        
        decoded_file = csv_file.read().decode('utf-8', errors='replace')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        created_count = 0
        for row in reader:
            # Expected CSV columns: "StudentEmail", "Category", "ReportData"
            student_email = row.get("StudentEmail")
            category_key = row.get("Category", "personal")
            report_data_str = row.get("ReportData", "{}")
            try:
                student = Student.objects.get(email=student_email)
            except Student.DoesNotExist:
                continue
            try:
                parsed_data = json.loads(report_data_str)
            except json.JSONDecodeError:
                parsed_data = {"CSV Import": report_data_str}
            
            Report.objects.create(
                student=student,
                category=category_key,
                report_type="Imported",
                data=parsed_data
            )
            created_count += 1

        return render(request, "reports/import_reports.html", {"success_message": f"{created_count} reports imported successfully!"})
    return render(request, "reports/import_reports.html")

def generate_report_dropdown(request):
    """
    Generates a report for a student based on selecting a student and a report category from dropdown lists.
    """
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        selected_category = request.POST.get("report_category")
        student = get_object_or_404(Student, pk=student_id)
        builder = ReportBuilder(student, selected_category)
        new_report = builder.build()
        return redirect('view_report', report_id=new_report.id)
    else:
        students = Student.objects.all()
        return render(request, "reports/generate_dropdown.html", {"students": students})

##############################################################################
# NEW DASHBOARD VIEW FOR REPORT ANALYTICS WITH EVALUATION METRICS
##############################################################################
def dashboard_view(request):
    """
    Dashboard view to aggregate and display analytics for reports along with evaluation metrics.
    
    This view calculates:
      - Total number of reports.
      - Counts of reports by category.
      - Counts of reports by status.
      - Evaluation metrics computed from the model's predictions.
      - Distribution of student performance levels.
    
    In a real scenario, you would retrieve the ground truth and the model's predictions
    from your evaluation pipeline. For demonstration purposes, we use dummy values.
    Replace y_true and y_pred with real data.
    
    The data is passed to the template in JSON format for Chart.js rendering.
    """
    total_reports = Report.objects.count()

    # Aggregate reports by category.
    category_counts = Report.objects.values('category').annotate(count=Count('id'))
    category_data = {}
    for entry in category_counts:
        category_code = entry['category']
        display = dict(ReportCategory.choices).get(category_code, category_code)
        category_data[display] = entry['count']

    # Aggregate reports by status.
    status_counts = Report.objects.values('status').annotate(count=Count('id'))
    status_data = {}
    for entry in status_counts:
        status_data[entry['status']] = entry['count']

    # Dummy evaluation data; replace these lists with actual true and predicted values.
    y_true = [1, 0, 1, 1, 0, 1, 0, 0, 1, 0]
    y_pred = [1, 0, 0, 1, 0, 1, 0, 1, 1, 0]
    evaluation_metrics = compute_evaluation_metrics(y_true, y_pred)

    # Aggregate student performance levels.
    level_counts = Student.objects.values('academic_performance').annotate(count=Count('id'))
    levels_data = {}
    for entry in level_counts:
        level = entry['academic_performance'] or "Not Specified"
        levels_data[level] = entry['count']

    context = {
        'total_reports': total_reports,
        'category_data': json.dumps(category_data),
        'status_data': json.dumps(status_data),
        'evaluation_metrics': evaluation_metrics,
        'levels_data': json.dumps(levels_data),
    }
    return render(request, 'reports/dashboard.html', context)
