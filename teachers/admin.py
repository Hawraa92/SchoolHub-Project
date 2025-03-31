from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    # عرض الحقول الرئيسية في قائمة المعلمين
    list_display = (
        'full_name',
        'national_id',
        'email',
        'mobile',
        'specialization',
        'years_of_experience',
        'date_of_appointment',
    )

    # حقول قابلة للبحث
    search_fields = (
        'full_name',
        'email',
        'mobile',
        'national_id',
        'specialization',
    )

    # إضافة فلاتر جانبية
    list_filter = (
        'gender',
        'marital_status',
        'specialization',
        'academic_rank',
        'housing_status',
        'annual_performance_rating',
        'disability_type',
    )

    # عرض التفاصيل بطريقة منسقة داخل لوحة الإدارة
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'user',
                'full_name',
                'national_id',
                'date_of_birth',
                'gender',
                'marital_status',
                'email',
                'mobile',
                'address',
                'profile_image',
            )
        }),
        ('Academic Information', {
            'fields': (
                'qualifications',
                'years_of_experience',
                'specialization',
                'assigned_classes',
                'subjects_taught',
                'academic_rank',
                'date_of_appointment',
                'last_professional_training_date',
                'completed_training_courses',
                'annual_performance_rating',
                'awards_and_certifications',
                'projects_supervised',
            )
        }),
        ('Health Information', {
            'fields': (
                'chronic_illnesses',
                'general_health_status',
            )
        }),
        ('Emergency Information', {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_relationship',
                'emergency_contact_phone',
            )
        }),
        ('Disability Information', {
            'fields': (
                'disability_type',
                'disability_details',
                'assistive_devices',
                'special_requirements',
                'care_instructions',
            )
        }),
        ('Housing Information', {
            'fields': (
                'housing_status',
            )
        }),
        ('Additional Information', {
            'fields': (
                'languages_spoken',
                'hobbies',
                'transportation',
                'professional_development_log',
                'personal_development_plan',
                'strengths',
                'weaknesses',
                'technological_proficiency',
            )
        }),
    )

    # جعل بعض الحقول للقراءة فقط
    readonly_fields = (
        'date_of_appointment',
    )
