import csv
import io
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from students.models import Student
from .models import Report, ReportCategory

def reports_list(request):
    """
    يعرض قائمة بجميع التقارير.
    """
    reports = Report.objects.all()
    return render(request, "reports/reports_list.html", {"reports": reports})

def view_report(request, report_id):
    """
    يعرض التقرير المحدد بناءً على معرّف التقرير.
    """
    report = get_object_or_404(Report, pk=report_id)
    return render(request, "reports/view_report.html", {"report": report})

def reports_by_category(request, category):
    """
    يعرض التقارير بحسب الفئة.
    """
    reports = Report.objects.filter(category=category)
    category_display = dict(ReportCategory.choices).get(category, category)
    return render(request, "reports/reports_by_category.html", {"reports": reports, "category": category_display})

def auto_generate_reports(request):
    """
    ينشئ تقارير جماعية لجميع الطلاب استنادًا إلى فئة معينة.
    """
    if request.method == "POST":
        selected_category = request.POST.get("report_category")
        students = Student.objects.filter(is_active=True)
        generated_count = 0
        for student in students:
            # كمثال، يتم توليد تقرير Personal لكل طالب
            data = student.generate_report_data()
            new_report = Report.objects.create(
                student=student,
                category=selected_category,
                report_type="Automatic",
                data=data
            )
            generated_count += 1
        message = f"{generated_count} reports generated for category '{selected_category}'."
        return render(request, "reports/auto_generate_reports.html", {"message": message})
    else:
        return render(request, "reports/auto_generate_reports.html")

def export_reports_pdf_view(request):
    """
    يصدر جميع التقارير بصيغة PDF.
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

        # عرض محتوى التقرير
        for key, value in report.data.items():
            pdf.drawString(120, y, f"{key}: {value}")
            y -= 15
            if y < 100:
                pdf.showPage()
                y = 750
        y -= 20

    pdf.save()
    return response

def export_reports_csv_view(request):
    """
    يصدر جميع التقارير بصيغة CSV.
    """
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
    ينشئ تقريرًا فرديًا لطالب محدد بناءً على اختيار فئة التقرير.
    """
    student = get_object_or_404(Student, pk=student_id)
    if request.method == "POST":
        selected_category = request.POST.get("report_category")
        if selected_category == ReportCategory.PERSONAL:
            data = {
                "Full Name": student.full_name,
                "Date of Birth": str(student.date_of_birth),
                "Gender": student.gender,
                "Email": student.email,
                "Mobile": student.mobile,
                "Nationality": student.nationality,
                "Address": student.address,
            }
        elif selected_category == ReportCategory.GUARDIAN:
            data = {
                "Guardian Name": student.guardian_name,
                "Guardian Relationship": student.guardian_relationship,
                "Guardian Contact": student.guardian_contact,
                "Guardian Address": student.guardian_address,
                "Guardian Job Title": student.guardian_job_title,
                "Guardian Monthly Income": str(student.guardian_monthly_income or "N/A"),
            }
        elif selected_category == ReportCategory.HEALTH:
            if hasattr(student, 'health_information'):
                health = student.health_information
                data = {
                    "Dental Health": health.dental_health,
                    "Ear Health": health.ear_health,
                    "General Health": health.general_health_status,
                    "Last Checkup": str(health.last_medical_checkup) if health.last_medical_checkup else "N/A",
                    "Weight": health.weight,
                    "Height": health.height,
                    "Blood Type": health.blood_type,
                }
            else:
                data = {"Health Information": "Not Available"}
        elif selected_category == ReportCategory.ACADEMIC:
            data = student.generate_report_data()
            data["Subjects"] = [subj.name for subj in student.subjects.all()]
            data["Attendance"] = f"{student.attendance_percentage}%"
        else:
            data = {}

        new_report = Report.objects.create(
            student=student,
            category=selected_category,
            report_type="Automatic",
            data=data
        )
        return redirect('view_report', report_id=new_report.id)
    else:
        return render(request, "reports/generate_single.html", {"student": student})

def import_reports_csv_view(request):
    """
    يتيح للمستخدم رفع ملف CSV يحتوي على تقارير أو بيانات أخرى.
    يمكن تخصيص المنطق حسب تنسيق ملف CSV المطلوب.
    """
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            return render(request, "reports/import_reports.html", {
                "error_message": "No file was uploaded."
            })
        if not csv_file.name.endswith(".csv"):
            return render(request, "reports/import_reports.html", {
                "error_message": "Please upload a valid CSV file (ends with .csv)."
            })

        # قراءة محتوى الملف
        decoded_file = csv_file.read().decode('utf-8', errors='replace')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        created_count = 0
        for row in reader:
            # نتوقع أن الملف يحتوي على أعمدة: "StudentEmail", "Category", "ReportData"
            student_email = row.get("StudentEmail")
            category_key = row.get("Category", "personal")
            report_data_str = row.get("ReportData", "{}")

            try:
                student = Student.objects.get(email=student_email)
            except Student.DoesNotExist:
                continue

            import json
            try:
                parsed_data = json.loads(report_data_str)
            except json.JSONDecodeError:
                parsed_data = {"CSV Import": report_data_str}

            new_report = Report.objects.create(
                student=student,
                category=category_key,
                report_type="Imported",
                data=parsed_data
            )
            created_count += 1

        return render(request, "reports/import_reports.html", {
            "success_message": f"{created_count} reports imported successfully!"
        })

    return render(request, "reports/import_reports.html")

def generate_report_dropdown(request):
    """
    دالة لتوليد تقرير بناءً على اختيار الطالب والفئة من قائمة منسدلة.
    """
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        selected_category = request.POST.get("report_category")

        # جلب الطالب بناءً على المعرّف
        student = get_object_or_404(Student, pk=student_id)

        # تجهيز بيانات التقرير بناءً على الفئة المختارة
        if selected_category == ReportCategory.PERSONAL:
            data = {
                "Full Name": student.full_name,
                "Date of Birth": str(student.date_of_birth),
                "Gender": student.gender,
                "Email": student.email,
                "Mobile": student.mobile,
                "Nationality": student.nationality,
                "Address": student.address,
            }
        elif selected_category == ReportCategory.GUARDIAN:
            data = {
                "Guardian Name": student.guardian_name,
                "Guardian Relationship": student.guardian_relationship,
                "Guardian Contact": student.guardian_contact,
                "Guardian Address": student.guardian_address,
                "Guardian Job Title": student.guardian_job_title,
                "Guardian Monthly Income": str(student.guardian_monthly_income or "N/A"),
            }
        elif selected_category == ReportCategory.HEALTH:
            if hasattr(student, 'health_information'):
                health = student.health_information
                data = {
                    "Dental Health": health.dental_health,
                    "Ear Health": health.ear_health,
                    "General Health": health.general_health_status,
                    "Last Checkup": str(health.last_medical_checkup) if health.last_medical_checkup else "N/A",
                    "Weight": health.weight,
                    "Height": health.height,
                    "Blood Type": health.blood_type,
                }
            else:
                data = {"Health Information": "Not Available"}
        elif selected_category == ReportCategory.ACADEMIC:
            data = student.generate_report_data()
            data["Subjects"] = [subj.name for subj in student.subjects.all()]
            data["Attendance"] = f"{student.attendance_percentage}%"
        else:
            data = {}

        new_report = Report.objects.create(
            student=student,
            category=selected_category,
            report_type="Automatic",
            data=data
        )
        return redirect('view_report', report_id=new_report.id)
    else:
        # عرض قائمة الطلاب للاختيار منها
        students = Student.objects.all()
        return render(request, "reports/generate_dropdown.html", {"students": students})
