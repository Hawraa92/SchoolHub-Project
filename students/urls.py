from django.urls import path
from .views import home_view, student_search, export_students_csv

urlpatterns = [
    path("", home_view, name="home"),
    path("search/", student_search, name="student_search"),
    path("export/csv/", export_students_csv, name="export_students_csv"),
]
