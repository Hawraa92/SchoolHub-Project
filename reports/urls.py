# reports/urls.py

from django.urls import path
from .views import (
    reports_list,
    view_report,
    reports_by_category,
    auto_generate_reports,
    export_reports_pdf_view,
    export_reports_csv_view,
    generate_single_student_report,
    import_reports_csv_view,
    generate_report_dropdown,
)

urlpatterns = [
    # استخدمنا name="reports_home" هنا
    path("", reports_list, name="reports_home"),

    path("view/<int:report_id>/", view_report, name="view_report"),
    path("category/<str:category>/", reports_by_category, name="reports_by_category"),
    path("generate/", auto_generate_reports, name="auto_generate_reports"),
    path("export/pdf/", export_reports_pdf_view, name="export_reports_pdf_view"),
    path("export/csv/", export_reports_csv_view, name="export_reports_csv_view"),
    path("generate/single/<int:student_id>/", generate_single_student_report, name="generate_single_student_report"),
    path("import/", import_reports_csv_view, name="import_reports_csv_view"),
    path("generate/dropdown/", generate_report_dropdown, name="generate_report_dropdown"),
]
