"""
Django Admin settings for SchoolHub's student management system.

This file configures (optionally) export actions (PDF/Excel/Word/CSV) and ModelAdmin settings for various models.
"""

import datetime
import logging
from io import BytesIO
import pandas as pd

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import (
    Student,
    ChronicIllness,
    Subject,
    EyeCondition,
    Allergy,
    Vaccination,
    Grade,
    EconomicSituation,
    SocialMediaAndTechnology,
    HealthInformation,
    GradeHistory,
    StudentPerformanceTrend,
)
from teachers.models import Teacher

logger = logging.getLogger(__name__)

# =============================================================================
# (Optional) Export Functions
# =============================================================================

def export_student_pdf(modeladmin, request, queryset):
    """
    Export selected students as PDF.
    """
    try:
        response = HttpResponse(content_type='application/pdf')
        filename = f'students_{datetime.datetime.now().strftime("%Y%m%d")}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        pdf = canvas.Canvas(response, pagesize=letter)
        pdf.setTitle("Student Information")
        y = 750

        for student in queryset:
            if y < 100:
                pdf.showPage()
                y = 750
            pdf.drawString(100, y, f"Student Name: {student.full_name}")
            y -= 20

        pdf.save()
        return response
    except Exception as e:
        logger.exception("Error exporting students to PDF: %s", e)
        return HttpResponse("An error occurred while generating the PDF.", status=500)

def export_students_excel(modeladmin, request, queryset):
    """
    Export selected students as Excel.
    """
    try:
        data = [
            {
                "Full Name": student.full_name,
                "Email": student.email,
                "Mobile": student.mobile,
                "Date of Birth": student.date_of_birth,
                "Grade Level": student.grade_level or "None",
                "Academic Performance": student.academic_performance or "None",
            }
            for student in queryset
        ]
        df = pd.DataFrame(data)
        with BytesIO() as b:
            with pd.ExcelWriter(b, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Students")
            b.seek(0)
            response = HttpResponse(
                b.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
            return response
    except Exception as e:
        logger.exception("Error exporting students to Excel: %s", e)
        return HttpResponse("An error occurred while generating the Excel file.", status=500)

def export_students_word(modeladmin, request, queryset):
    """
    Export selected students as Word.
    """
    try:
        doc = Document()
        doc.add_heading("Student Information", level=1)
        for index, student in enumerate(queryset):
            doc.add_paragraph(f"Student Name: {student.full_name}")
            if index < len(queryset) - 1:
                doc.add_page_break()
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response["Content-Disposition"] = 'attachment; filename="students.docx"'
        doc.save(response)
        return response
    except Exception as e:
        logger.exception("Error exporting students to Word: %s", e)
        return HttpResponse("An error occurred while generating the Word document.", status=500)

def export_students_csv(modeladmin, request, queryset):
    """
    Export selected students as CSV.
    """
    import csv
    try:
        response = HttpResponse(content_type='text/csv')
        filename = f'students_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow([
            "Full Name",
            "Student ID",
            "Email",
            "Mobile",
            "Grade Level",
            "Academic Performance",
            "Enrollment Date"
        ])
        for student in queryset:
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
    except Exception as e:
        logger.exception("Error exporting students to CSV: %s", e)
        return HttpResponse("An error occurred while generating the CSV file.", status=500)

# =============================================================================
# Inline Admins
# =============================================================================

class GradeInline(admin.TabularInline):
    model = Grade
    extra = 1
    fields = (
        'subject',
        'score',
        'max_score',
        'percentage',
        'grade_level',
        'gpa_points',
        'exam_type',
        'semester',
        'date_recorded',
    )
    readonly_fields = ('percentage', 'grade_level', 'gpa_points', 'date_recorded')
    show_change_link = True
    autocomplete_fields = ('subject',)

class HealthInformationInline(admin.StackedInline):
    model = HealthInformation
    can_delete = False
    verbose_name_plural = "Health Information"
    fk_name = 'student'
    fieldsets = (
        ('General Health Information', {
            'fields': (
                'surgical_history',
                'has_chronic_illness',
                'chronic_illnesses_type',
                'allergies',
                'vaccinations',
                'eye_conditions',
                'left_eye_vision',
                'right_eye_vision',
                'dental_health',
                'ear_health',
                'general_health_status',
                'last_medical_checkup',
                'weight',
                'height',
                'blood_type',
                'disabilities',
            )
        }),
        ('Psychological Disorders and Behaviors', {
            'fields': (
                'academic_stress',
                'motivation',
                'depression',
                'sleep_disorder',
                'anxiety',
                'psychological_trauma',
                'isolation_tendency',
                'aggressive_behavior',
            )
        }),
        ('Psychosocial Factors', {
            'fields': (
                'personal_family_issues',
                'bullying',
                'study_life_balance',
                'psychological_support',
                'psychological_notes',
                'family_pressures',
            )
        }),
        ('Sensitive Information', {
            'fields': (
                'practices_masturbation',
                'abuse_at_home',
                'abuse_at_school',
                'sexual_harassment_at_home',
                'sexual_harassment_at_school',
                'alcohol_consumption',
                'smoking',
                'drug_use',
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Prevent editing sensitive info unless user is superuser.
        """
        sensitive_fields = (
            'practices_masturbation',
            'abuse_at_home',
            'abuse_at_school',
            'sexual_harassment_at_home',
            'sexual_harassment_at_school',
            'alcohol_consumption',
            'smoking',
            'drug_use',
        )
        if not request.user.is_superuser:
            return sensitive_fields
        return super().get_readonly_fields(request, obj)

class EconomicSituationInline(admin.StackedInline):
    model = EconomicSituation
    can_delete = False
    verbose_name_plural = "Economic Situation"
    fk_name = 'student'
    fieldsets = (
        ("Orphan Status", {
            "fields": ("is_orphan",)
        }),
        ("Guardian/Economic Information", {
            "fields": (
                'father_occupation',
                'mother_occupation',
                'parents_marital_status',
                'family_income_level',
                'income_source',
                'monthly_expenses',
                'housing_status',
                'access_to_electricity',
                'has_access_to_water',
                'access_to_internet',
                'has_private_study_room',
                'number_of_rooms_in_home',
                'daily_food_availability',
                'has_school_uniform',
                'has_stationery',
                'receives_financial_aid',
                'receives_meal_assistance',
                'receives_scholarship',
                'receives_private_tutoring',
                'daily_study_hours',
                'works_after_school',
                'work_hours_per_week',
                'responsible_for_household_tasks',
                'transportation_mode',
                'distance_to_school',
                'has_health_insurance',
                'household_size',
                'sibling_rank',
            )
        }),
    )

class SocialMediaAndTechnologyInline(admin.StackedInline):
    model = SocialMediaAndTechnology
    can_delete = False
    verbose_name_plural = "Social Media and Technology"
    fk_name = 'student'

# =============================================================================
# Model Admins
# =============================================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'student_id',
        'grade_level',
        'email',
        'mobile',
        'academic_performance',
        'get_age',
        'generate_report_link',  # حقل جديد لإنشاء زر توليد التقرير
    )
    list_display_links = ('full_name',)

    list_filter = (
        'grade_level',
        'academic_performance',
        'gender',
        'nationality',
    )
    search_fields = (
        'full_name',
        'email',
        'mobile',
        'guardian_name',
        'grades__subject__name',
        'grades__teacher__full_name',
        'grades__history__reason_for_update',
    )
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'user',
                'full_name',
                'date_of_birth',
                'student_id',
                'get_age',
                'gender',
                'nationality',
                'marital_status',
                'address',
                'profile_image',
                'email',
                'mobile',
                'spoken_language',
                'emergency_contact_name',
                'emergency_contact',
                'enrollment_date',
            )
        }),
        ('Guardian Information', {
            'fields': (
                'guardian_name',
                'guardian_relationship',
                'guardian_contact',
                'guardian_address',
                'guardian_job_title',
                'guardian_chronic_illnesses',
                'guardian_employment_status',
                'guardian_monthly_income',
                'guardian_education',
            )
        }),
        ('Academic Information', {
            'fields': (
                'grade_level',
                'subjects',
                'attendance_percentage',
                'academic_performance',
                'awards',
                'seat_zone',
            )
        }),
    )
    readonly_fields = ('get_age', 'student_id', 'academic_performance')
    filter_horizontal = ('subjects', 'guardian_chronic_illnesses',)
    ordering = ('student_id',)
    inlines = [
        GradeInline,
        HealthInformationInline,
        EconomicSituationInline,
        SocialMediaAndTechnologyInline,
    ]
    list_select_related = ('user',)

    # أضف إجراءات التصدير لتظهر في قائمة الإجراءات (Actions) في واجهة الـAdmin
    actions = [export_students_csv, export_student_pdf, export_students_excel, export_students_word]

    @admin.display(description="Age")
    def get_age(self, obj):
        return obj.age or "-"

    def generate_report_link(self, obj):
        """
        يُنشئ زرًا ينقلك إلى صفحة توليد تقرير فردي في تطبيق التقارير.
        يفترض أن لديك مسار (URL) باسم 'generate_single_student_report'
        يقبل رقم الطالب أو UUID.
        """
        if obj.pk:
            # إذا كنت تستخدم int PK: path("generate/single/<int:student_id>/", ...)
            # إذا UUID: path("generate/single/<uuid:student_id>/", ...)
            url = reverse("generate_single_student_report", args=[obj.pk])
            return format_html('<a class="button" href="{}" target="_blank">Generate Report</a>', url)
        return "-"
    generate_report_link.short_description = "Generate Report"

@admin.register(EconomicSituation)
class EconomicSituationAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Orphan Status", {
            "fields": ("is_orphan",)
        }),
        ("Guardian/Economic Information", {
            "fields": (
                'father_occupation',
                'mother_occupation',
                'parents_marital_status',
                'family_income_level',
                'income_source',
                'monthly_expenses',
                'housing_status',
                'access_to_electricity',
                'has_access_to_water',
                'access_to_internet',
                'has_private_study_room',
                'number_of_rooms_in_home',
                'daily_food_availability',
                'has_school_uniform',
                'has_stationery',
                'receives_financial_aid',
                'receives_meal_assistance',
                'receives_scholarship',
                'receives_private_tutoring',
                'daily_study_hours',
                'works_after_school',
                'work_hours_per_week',
                'responsible_for_household_tasks',
                'transportation_mode',
                'distance_to_school',
                'has_health_insurance',
                'household_size',
                'sibling_rank',
            )
        }),
    )
    list_display = (
        'student',
        'is_orphan',
        'father_occupation',
        'mother_occupation',
        'parents_marital_status',
        'family_income_level',
        'housing_status',
        'transportation_mode',
        'receives_financial_aid',
    )
    list_filter = (
        'is_orphan',
        'housing_status',
        'transportation_mode',
        'receives_financial_aid',
        'has_access_to_water',
        'has_private_study_room',
    )
    search_fields = ('student__full_name',)
    autocomplete_fields = ('student',)

@admin.register(SocialMediaAndTechnology)
class SocialMediaAndTechnologyAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'has_phone',
        'has_laptop',
        'has_tablet',
        'has_pc',
        'device_usage_purpose',
        'has_social_media_accounts',
        'daily_screen_time',
        'social_media_impact_on_studies',
        'content_type_watched',
        'social_media_impact_on_sleep',
        'social_media_impact_on_focus',
        'plays_video_games',
        'daily_gaming_hours',
        'aware_of_cybersecurity',
        'experienced_electronic_extortion',
    )
    list_filter = (
        'has_phone',
        'has_laptop',
        'has_tablet',
        'has_pc',
        'has_social_media_accounts',
        'plays_video_games',
        'aware_of_cybersecurity',
        'experienced_electronic_extortion',
    )
    search_fields = ('student__full_name',)
    autocomplete_fields = ('student',)

@admin.register(ChronicIllness)
class ChronicIllnessAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(EyeCondition)
class EyeConditionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('name', 'allergy_type')
    list_filter = ('allergy_type',)
    search_fields = ('name',)

@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_administered', 'status')
    list_filter = ('status', 'date_administered')
    search_fields = ('name',)
    date_hierarchy = 'date_administered'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'credit_hours')
    search_fields = ('name',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'subject',
        'score',
        'max_score',
        'percentage',
        'get_grade_level',
        'exam_type',
        'get_semester',
        'get_teacher',
        'date_recorded',
    )
    list_filter = ('exam_type', 'date_recorded')
    search_fields = ('student__full_name', 'subject__name', 'teacher__full_name')
    date_hierarchy = 'date_recorded'
    ordering = ('-date_recorded',)
    autocomplete_fields = ('student', 'subject')
    list_select_related = ('student', 'subject', 'teacher')

    @admin.display(description="Grade Level")
    def get_grade_level(self, obj):
        return getattr(obj, 'grade_level', "-")

    @admin.display(description="Semester")
    def get_semester(self, obj):
        return getattr(obj, 'semester', "-")

    @admin.display(description="Teacher")
    def get_teacher(self, obj):
        return obj.teacher.full_name if obj.teacher else "-"

@admin.register(GradeHistory)
class GradeHistoryAdmin(admin.ModelAdmin):
    list_display = ('grade', 'updated_by', 'previous_score', 'new_score', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = (
        'grade__student__full_name',
        'grade__subject__name',
        'updated_by__full_name',
        'reason_for_update'
    )
    date_hierarchy = 'updated_at'

@admin.register(StudentPerformanceTrend)
class StudentPerformanceTrendAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'average_percentage', 'gpa')
    list_filter = ('semester',)
    search_fields = ('student__full_name',)
    autocomplete_fields = ('student',)
