# reports/urls.py
from django.urls import path
from .views import (
    reports_list,                      # Displays a list of all reports.
    view_report,                       # Displays a single report's details.
    reports_by_category,               # Filters reports by a given category.
    export_reports_pdf_view,           # Exports reports as a PDF document.
    export_reports_csv_view,           # Exports reports as a CSV file.
    generate_single_student_report,    # Generates a report for a single student.
    import_reports_csv_view,           # Imports reports data from a CSV file.
    generate_report_dropdown,          # Generates report from dropdown selections.
    dashboard_view                     # Dashboard view with analytics and evaluation metrics.
)

urlpatterns = [
    path("", reports_list, name="reports_home"),
    path("view/<int:report_id>/", view_report, name="view_report"),
    path("category/<str:category>/", reports_by_category, name="reports_by_category"),
    path("export/pdf/", export_reports_pdf_view, name="export_reports_pdf_view"),
    path("export/csv/", export_reports_csv_view, name="export_reports_csv_view"),
    path("generate/single/<int:student_id>/", generate_single_student_report, name="generate_single_student_report"),
    path("import/", import_reports_csv_view, name="import_reports_csv_view"),
    path("generate/dropdown/", generate_report_dropdown, name="generate_report_dropdown"),
    path("dashboard/", dashboard_view, name="reports_dashboard"),
]
