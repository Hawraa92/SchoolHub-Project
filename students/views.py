import csv
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Student

def home_view(request):
    """
    (Alternate home view) Renders the home page with dynamic statistics.
    This view is not used if the root URL is mapped to schoolhub/views.py home.
    """
    student_count = Student.objects.count()
    context = {
        'student_count': student_count,
    }
    return render(request, 'home.html', context)

def student_search(request):
    """
    Searches for students based on the query parameter 'q'.
    """
    query = request.GET.get("q", "")
    if query:
        students = Student.objects.filter(full_name__icontains=query)
    else:
        students = Student.objects.all()
    return render(request, "students/student_search.html", {"students": students, "query": query})

def export_students_csv(request):
    """
    Exports all students' data as a CSV file.
    """
    students = Student.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "Full Name", "Student ID", "Email", "Mobile",
        "Grade Level", "Academic Performance", "Enrollment Date"
    ])
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
