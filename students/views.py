# students/views.py
import csv
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Student

def student_search(request):
    """
    صفحة بحث عن الطلاب بناءً على الاسم؛ يمكن استخدامها أيضًا لتوجيه المستخدم إلى التقارير.
    """
    query = request.GET.get("q", "")
    if query:
        students = Student.objects.filter(full_name__icontains=query)
    else:
        students = Student.objects.all()
    return render(request, "students/student_search.html", {"students": students, "query": query})

def export_students_csv(request):
    """
    تصدير بيانات جميع الطلاب إلى ملف CSV.
    """
    students = Student.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    writer = csv.writer(response)
    writer.writerow(["Full Name", "Student ID", "Email", "Mobile", "Grade Level", "Academic Performance", "Enrollment Date"])
    for student in students:
        writer.writerow([
            student.full_name,
            student.student_id,
            student.email,
            student.mobile,
            student.grade_level,
            student.academic_performance,
            student.enrollment_date,
        ])
    return response
