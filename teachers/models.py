from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Teacher(models.Model):
    # Personal Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    full_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Full Name"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date of Birth"))
    gender = models.CharField(
        max_length=15,
        choices=[("Male", _("Male")), ("Female", _("Female")), ("Other", _("Other"))],
        null=True,
        blank=True,
        verbose_name=_("Gender")
    )
    marital_status = models.CharField(
        max_length=20,
        choices=[
            ("Single", _("Single")),
            ("Married", _("Married")),
            ("Divorced", _("Divorced")),
            ("Widowed", _("Widowed"))
        ],
        null=True,
        blank=True,
        verbose_name=_("Marital Status")
    )
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name=_("Email"))
    mobile = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("Mobile"))
    address = models.TextField(null=True, blank=True, verbose_name=_("Address"))
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name=_("National ID"))

    # Academic and Professional Information
    qualifications = models.TextField(null=True, blank=True, verbose_name=_("Qualifications"))
    years_of_experience = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Years of Experience"))
    specialization = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Specialization"))
    assigned_classes = models.TextField(null=True, blank=True, verbose_name=_("Assigned Classes"))
    subjects_taught = models.TextField(null=True, blank=True, verbose_name=_("Subjects Taught"))
    date_of_appointment = models.DateField(null=True, blank=True, verbose_name=_("Date of Appointment"))
    academic_rank = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Academic Rank"))
    last_professional_training_date = models.DateField(null=True, blank=True, verbose_name=_("Last Professional Training Date"))
    completed_training_courses = models.PositiveIntegerField(default=0, verbose_name=_("Completed Training Courses"))
    annual_performance_rating = models.CharField(
        max_length=20,
        choices=[
            ("Excellent", _("Excellent")),
            ("Very Good", _("Very Good")),
            ("Good", _("Good")),
            ("Needs Improvement", _("Needs Improvement"))
        ],
        null=True,
        blank=True,
        verbose_name=_("Annual Performance Rating")
    )
    awards_and_certifications = models.TextField(null=True, blank=True, verbose_name=_("Awards and Certifications"))
    projects_supervised = models.PositiveIntegerField(default=0, verbose_name=_("Projects Supervised"))

    # Health Information
    chronic_illnesses = models.TextField(null=True, blank=True, verbose_name=_("Chronic Illnesses"))
    general_health_status = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("General Health Status"))

    # Emergency Information
    emergency_contact_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Emergency Contact Name")
    )
    emergency_contact_relationship = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("Emergency Contact Relationship")
    )
    emergency_contact_phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name=_("Emergency Contact Phone")
    )

    # Disability Information
    disability_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("Type of Disability")
    )
    disability_details = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Disability Details")
    )
    assistive_devices = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Assistive Devices")
    )
    special_requirements = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Special Requirements")
    )
    care_instructions = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Care Instructions")
    )

    # Housing Information
    housing_status = models.CharField(
        max_length=20,
        choices=[
            ("Owned", _("Owned")),
            ("Rented", _("Rented")),
            ("Shared", _("Shared"))
        ],
        null=True,
        blank=True,
        verbose_name=_("Housing Status")
    )

    # Additional Information
    languages_spoken = models.TextField(null=True, blank=True, verbose_name=_("Languages Spoken"))
    hobbies = models.TextField(null=True, blank=True, verbose_name=_("Hobbies"))
    transportation = models.CharField(
        max_length=100,
        choices=[
            ("Own Car", _("Own Car")),
            ("Public Transport", _("Public Transport")),
            ("Needs Assistance", _("Needs Assistance"))
        ],
        null=True,
        blank=True,
        verbose_name=_("Transportation")
    )
    professional_development_log = models.TextField(null=True, blank=True, verbose_name=_("Professional Development Log"))
    personal_development_plan = models.TextField(null=True, blank=True, verbose_name=_("Personal Development Plan"))
    strengths = models.TextField(null=True, blank=True, verbose_name=_("Strengths"))
    weaknesses = models.TextField(null=True, blank=True, verbose_name=_("Weaknesses"))
    technological_proficiency = models.TextField(null=True, blank=True, verbose_name=_("Technological Proficiency"))

    # File Uploads
    profile_image = models.ImageField(upload_to="teacher_profiles/", null=True, blank=True, verbose_name=_("Profile Image"))

    def __str__(self):
        return self.full_name or _("Teacher")

    class Meta:
        verbose_name = _("Teacher")
        verbose_name_plural = _("Teachers")
