import json
import datetime
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator

from .models import Report, ReportCategory
from .report_builder import ReportBuilder
from students.models import Student
from .evaluation import compute_evaluation_metrics


def reports_list(request):
    """
    Displays a paginated list of reports (20 per page).
    """
    all_reports = Report.objects.all()
    paginator = Paginator(all_reports, 20)  # 20 reports per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "reports/reports_list.html", {"page_obj": page_obj})


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
    category_display = dict(ReportCategory.choices).get(category, category)
    return render(request, "reports/reports_by_category.html", {"reports": reports, "category": category_display})


def export_reports_pdf_view(request):
    """
    Exports all reports as a PDF document.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    reports = Report.objects.all()
    response = HttpResponse(content_type="application/pdf")
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
    response = HttpResponse(content_type="text/csv")
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
    Generates a report for a single student based on selected category.
    """
    student = get_object_or_404(Student, pk=student_id)
    if request.method == "POST":
        selected_category = request.POST.get("report_category")
        builder = ReportBuilder(student, selected_category)
        new_report = builder.build()
        return redirect('view_report', report_id=new_report.id)
    return render(request, "reports/generate_single.html", {"student": student})


def import_reports_csv_view(request):
    """
    Allows the user to upload a CSV file to import reports in bulk.
    """
    import csv, io

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
            student_email   = row.get("StudentEmail")
            category_key    = row.get("Category", "personal")
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
    Generates a report based on dropdown selection of student and category.
    """
    if request.method == "POST":
        student_id        = request.POST.get("student_id")
        selected_category = request.POST.get("report_category")
        student = get_object_or_404(Student, pk=student_id)
        builder = ReportBuilder(student, selected_category)
        new_report = builder.build()
        return redirect('view_report', report_id=new_report.id)
    students = Student.objects.all()
    return render(request, "reports/generate_dropdown.html", {"students": students})


def dashboard_view(request):
    """
    Dashboard view to aggregate and display analytics for reports and evaluation metrics.
    Limits data processed to reduce memory usage on low-RAM environments.
    """
    # Aggregations over all reports
    total_reports = Report.objects.count()
    category_counts = Report.objects.values('category').annotate(count=Count('id'))
    category_data = { dict(ReportCategory.choices)[e['category']]: e['count'] for e in category_counts }
    status_counts = Report.objects.values('status').annotate(count=Count('id'))
    status_data = { e['status']: e['count'] for e in status_counts }

    # Limit student dataset for performance
    MAX_STUDENTS = 200
    students_qs = Student.objects.all()[:MAX_STUDENTS]
    level_counts = students_qs.values('academic_performance').annotate(count=Count('id'))
    levels_data = { (e['academic_performance'] or "Not Specified"): e['count'] for e in level_counts }

    # Dummy evaluation data (replace with real y_true, y_pred lists)
    y_true = [1, 0, 1, 1, 0, 1, 0, 0, 1, 0]
    y_pred = [1, 0, 0, 1, 0, 1, 0, 1, 1, 0]
    evaluation_metrics = compute_evaluation_metrics(y_true, y_pred)

    context = {
        'total_reports': total_reports,
        'category_data': category_data,
        'status_data':   status_data,
        'evaluation_metrics': evaluation_metrics,
        'levels_data':   levels_data,
    }
    return render(request, 'reports/dashboard.html', context)
