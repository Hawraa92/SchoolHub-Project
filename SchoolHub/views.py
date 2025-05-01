from django.shortcuts import render
from students.models import Student, Subject  # Subject represents courses
from teachers.models import Teacher  # Teacher model

def home(request):
    """
    Render the home page with dynamic statistics.
    Retrieves the total numbers for students, teachers, and courses, and passes them to the template.
    """
    student_count = Student.objects.count()
    teacher_count = Teacher.objects.count()
    course_count = Subject.objects.count()
    context = {
        'student_count': student_count,
        'teacher_count': teacher_count,
        'course_count': course_count,
    }
    return render(request, "home.html", context)
