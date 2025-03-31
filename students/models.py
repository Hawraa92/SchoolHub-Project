"""
SchoolHub – School Management System Models

This file contains models covering health, academic, social, and economic aspects of students.
"""

import uuid
import logging
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
from django.apps import apps

from teachers.models import Teacher  # Teacher is used in the Grade model for recording the examiner

# استيراد دالة التشفير للحقول الحساسة
from encrypted_fields import fields

logger = logging.getLogger(__name__)

# =============================================================================
# Constants and Choices
# =============================================================================

# Eye Health Choices
LEFT_EYE_VISION = [
    ("6/6", "Normal vision (6/6 - 20/20)"),
    ("6/9", "Good vision (6/9 - 20/30)"),
    ("6/12", "Moderate vision (6/12 - 20/40)"),
    ("6/18", "Mild vision issues (6/18 - 20/60)"),
    ("6/24", "Poor vision (6/24 - 20/80)"),
    ("6/36", "Severe vision impairment (6/36 - 20/120)"),
    ("6/60", "Very severe impairment (6/60 - 20/200)"),
    ("<6/60", "Blind or near blind (<6/60)"),
]
RIGHT_EYE_VISION = LEFT_EYE_VISION[:]  # نفس الاختيارات للعين اليمنى

# Income Source Choices
class IncomeSourceChoices(models.TextChoices):
    SALARY = "Salary", "Salary"
    BUSINESS = "Business", "Business"
    AID = "Aid", "Aid"
    OTHER = "Other", "Other"

# Social Media Choices
class SocialMediaChoices(models.TextChoices):
    FACEBOOK = "Facebook", "Facebook"
    INSTAGRAM = "Instagram", "Instagram"
    TWITTER = "Twitter", "Twitter"
    SNAPCHAT = "Snapchat", "Snapchat"
    TIKTOK = "TikTok", "TikTok"
    OTHER = "Other", "Other"

# Device Usage Purpose Choices
class DeviceUsagePurposeChoices(models.TextChoices):
    EDUCATION = "Education", "Education"
    ENTERTAINMENT = "Entertainment", "Entertainment"
    GAMING = "Gaming", "Gaming"
    WORK = "Work", "Work"
    OTHER = "Other", "Other"

# Grade Thresholds and GPA Values
GRADE_THRESHOLDS = {
    "A": 90,
    "B": 80,
    "C": 70,
    "D": 60,
    "F": 0,
}
SORTED_GRADE_THRESHOLDS = sorted(GRADE_THRESHOLDS.items(), key=lambda item: item[1], reverse=True)

GPA_VALUES = {
    "A": Decimal("4.0"),
    "B": Decimal("3.0"),
    "C": Decimal("2.0"),
    "D": Decimal("1.0"),
    "F": Decimal("0.0"),
}

# Other Choices
class GenderChoices(models.TextChoices):
    MALE = "Male", "Male"
    FEMALE = "Female", "Female"

class MaritalStatusChoices(models.TextChoices):
    SINGLE = "Single", "Single"
    MARRIED = "Married", "Married"
    OTHER = "Other", "Other"

class GuardianRelationshipChoices(models.TextChoices):
    FATHER = "Father", "Father"
    MOTHER = "Mother", "Mother"
    SIBLING = "Sibling", "Sibling"
    OTHER = "Other", "Other"

class EmploymentStatusChoices(models.TextChoices):
    EMPLOYED = "Employed", "Employed"
    UNEMPLOYED = "Unemployed", "Unemployed"
    RETIRED = "Retired", "Retired"

class EducationChoices(models.TextChoices):
    ILLITERATE = "Illiterate", "Illiterate"
    PRIMARY = "Primary", "Primary Education"
    SECONDARY = "Secondary", "Secondary Education"
    BACHELORS = "Bachelor's", "Bachelor's Degree"
    MASTERS = "Master's", "Master's Degree"
    PHD = "PhD", "PhD"

class ExamTypeChoices(models.TextChoices):
    MIDTERM = "Midterm", "Midterm Exam"
    FINAL = "Final", "Final Exam"
    QUIZ = "Quiz", "Quiz"
    ASSIGNMENT = "Assignment", "Assignment"
    OTHER = "Other", "Other"

class SemesterChoices(models.TextChoices):
    FALL = "Fall", "Fall Semester"
    SPRING = "Spring", "Spring Semester"
    SUMMER = "Summer", "Summer Semester"

class ImpactChoices(models.TextChoices):
    POSITIVE = "Positive", "Positive"
    NEGATIVE = "Negative", "Negative"
    NEUTRAL = "Neutral", "Neutral"
    NONE = "None", "None"

class ContentTypeChoices(models.TextChoices):
    EDUCATIONAL = "Educational", "Educational"
    ENTERTAINMENT = "Entertainment", "Entertainment"
    GAMING = "Gaming", "Gaming"
    NEWS = "News", "News"
    SPORTS = "Sports", "Sports"
    OTHER = "Other", "Other"

class TransportationModeChoices(models.TextChoices):
    WALKING = "Walking", "Walking"
    BICYCLE = "Bicycle", "Bicycle"
    PUBLIC_TRANSPORT = "Public Transport", "Public Transport"
    PRIVATE_CAR = "Private Car", "Private Car"
    SCHOOL_BUS = "School Bus", "School Bus"
    MOTORBIKE = "Motorbike", "Motorbike"
    NONE = "None", "None"

class HousingStatusChoices(models.TextChoices):
    OWNED = "Owned", "Owned"
    RENTED = "Rented", "Rented"
    SHARED = "Shared", "Shared"
    TEMPORARY = "Temporary Shelter", "Temporary Shelter"
    NONE = "None", "None"

# =============================================================================
# Custom QuerySet for Student
# =============================================================================
class StudentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

# =============================================================================
# Public Health Models
# =============================================================================
class Surgery(models.Model):
    """Represents a surgical procedure."""
    name = models.CharField(max_length=255, unique=True, help_text="Name of the surgery")
    date = models.DateField(null=True, blank=True, help_text="Date of the surgery (optional)")

    class Meta:
        verbose_name = "Surgery"
        verbose_name_plural = "Surgeries"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.name} ({self.date})" if self.date else self.name

class ChronicIllness(models.Model):
    """Represents a chronic illness."""
    name = models.CharField(max_length=100, unique=True, help_text="Name of the chronic illness")

    class Meta:
        verbose_name = "Chronic Illness"
        verbose_name_plural = "Chronic Illnesses"

    def __str__(self):
        return self.name

class EyeCondition(models.Model):
    """Represents an eye condition."""
    name = models.CharField(max_length=100, unique=True, help_text="Name of the eye condition")

    class Meta:
        verbose_name = "Eye Condition"
        verbose_name_plural = "Eye Conditions"

    def __str__(self):
        return self.name

class Allergy(models.Model):
    """Represents a specific allergy."""
    ALLERGY_TYPES = [
        ("Food", "Food"),
        ("Medication", "Medication"),
        ("Environmental", "Environmental"),
    ]
    name = models.CharField(max_length=100, unique=True, help_text="Name of the allergy")
    allergy_type = models.CharField(max_length=100, choices=ALLERGY_TYPES, default="Food", help_text="Type of allergy")

    class Meta:
        verbose_name = "Allergy"
        verbose_name_plural = "Allergies"

    def __str__(self):
        return f"{self.name} ({self.get_allergy_type_display()})"

class Vaccination(models.Model):
    """Represents a vaccination record."""
    VACCINATION_STATUS = [
        ("Completed", "Completed"),
        ("Pending", "Pending"),
    ]
    name = models.CharField(max_length=100, unique=True, help_text="Name of the vaccination")
    date_administered = models.DateField(help_text="Vaccination date")
    status = models.CharField(max_length=100, choices=VACCINATION_STATUS, default="Pending", help_text="Vaccination status")
    notes = models.TextField(null=True, blank=True, help_text="Additional notes about the vaccination")

    class Meta:
        verbose_name = "Vaccination"
        verbose_name_plural = "Vaccinations"
        ordering = ["-date_administered"]

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

# =============================================================================
# Academic Models
# =============================================================================
class Subject(models.Model):
    """Represents an academic subject."""
    name = models.CharField(max_length=100, unique=True, help_text="Name of the subject")
    description = models.TextField(null=True, blank=True, help_text="Subject description")
    credit_hours = models.PositiveSmallIntegerField(default=1, help_text="Number of credit hours for the subject")

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        return self.name

# =============================================================================
# Disability Model
# =============================================================================
class Disability(models.Model):
    """Represents a disability or special need."""
    name = models.CharField(max_length=100, unique=True, help_text="Name of the disability or special need")
    description = models.TextField(null=True, blank=True, help_text="A brief description of the disability (optional)")

    class Meta:
        verbose_name = "Disability"
        verbose_name_plural = "Disabilities"

    def __str__(self):
        return self.name

# =============================================================================
# Student Model
# =============================================================================
class Student(models.Model):
    """Represents a student with personal, academic, and guardian information."""
    GRADE_LEVEL_CHOICES = [
        ("Grade 10", "Grade 10"),
        ("Grade 11", "Grade 11"),
        ("Grade 12", "Grade 12"),
    ]
    ACADEMIC_PERFORMANCE_CHOICES = [
        ("Excellent", "Excellent"),
        ("Very Good", "Very Good"),
        ("Good", "Good"),
        ("Average", "Average"),
        ("Needs Improvement", "Needs Improvement"),
    ]

    # Basic Information
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )
    full_name = models.CharField(max_length=255)
    student_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False,
                                  verbose_name="Student ID",
                                  help_text="Unique identifier for the student")
    enrollment_date = models.DateField()
    subjects = models.ManyToManyField(Subject, blank=True, related_name="students")
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=100, choices=GenderChoices.choices)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    marital_status = models.CharField(max_length=100, choices=MaritalStatusChoices.choices, null=True, blank=True)
    address = models.TextField()
    profile_image = models.ImageField(upload_to="student_profiles/", null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    mobile = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    spoken_language = models.CharField(max_length=100, default="English")
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True,
                                              help_text="Full name of the emergency contact")
    emergency_contact = models.CharField(max_length=100, help_text="Emergency contact number")

    # Guardian Information
    guardian_name = models.CharField(max_length=100, default="Unknown Guardian", help_text="Guardian's full name")
    guardian_relationship = models.CharField(max_length=100, choices=GuardianRelationshipChoices.choices)
    guardian_contact = models.CharField(max_length=100)
    guardian_address = models.TextField(null=True, blank=True, help_text="Guardian's home address")
    guardian_job_title = models.CharField(max_length=100, null=True, blank=True, help_text="Guardian's job title")
    guardian_chronic_illnesses = models.ManyToManyField(ChronicIllness, blank=True,
                                                        related_name="guardians",
                                                        help_text="Guardian's chronic illnesses")
    guardian_employment_status = models.CharField(max_length=100, choices=EmploymentStatusChoices.choices,
                                                  default=EmploymentStatusChoices.EMPLOYED,
                                                  help_text="Guardian's employment status")
    guardian_monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                                  help_text="Guardian's monthly income")
    guardian_education = models.CharField(max_length=100, choices=EducationChoices.choices,
                                          default=EducationChoices.ILLITERATE,
                                          help_text="Guardian's educational attainment")

    # Academic Information
    grade_level = models.CharField(max_length=100, choices=GRADE_LEVEL_CHOICES, null=True, blank=True)
    attendance_percentage = models.FloatField(default=0.0)
    academic_performance = models.CharField(max_length=100, choices=ACADEMIC_PERFORMANCE_CHOICES,
                                            null=True, blank=True,
                                            help_text="Student's academic performance")
    awards = models.TextField(null=True, blank=True)
    seat_zone = models.CharField(max_length=10,
                                 choices=[("Front", "Front"), ("Middle", "Middle"), ("Back", "Back"), ("Side", "Side")],
                                 default="Middle",
                                 help_text="Student's seating position")
    is_active = models.BooleanField(default=True, verbose_name="Active",
                                    help_text="Indicates if the student is active (soft delete)")

    objects = StudentQuerySet.as_manager()

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Student"
        verbose_name_plural = "Students"
        indexes = [models.Index(fields=["email", "mobile"])]

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        today = date.today()
        if self.date_of_birth:
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def is_orphan(self):
        """Return True if the student is marked as orphan in their economic situation."""
        return getattr(self, 'economic_situation', None) and self.economic_situation.is_orphan

    def save(self, *args, **kwargs):
        """
        في هذا التعديل، نتأكد من حفظ جميع الحقول دائماً،
        ونحدّث الأداء الأكاديمي قبل الحفظ.
        """
        # حساب الأداء الأكاديمي قبل الحفظ
        self.academic_performance = self.calculate_academic_performance()

        # حفظ جميع الحقول (حتى تاريخ الميلاد وتاريخ الالتحاق)
        super().save(*args, **kwargs)

        # معالجة الصورة إذا وجدت
        if self.profile_image:
            try:
                img = Image.open(self.profile_image.path)
                if img.height > 300 or img.width > 300:
                    img.thumbnail((300, 300))
                    img.save(self.profile_image.path)
            except Exception:
                logger.exception("Error processing profile image for student: %s", self.full_name)

    def get_average_score(self):
        """Calculate the weighted average score from the Grade model."""
        grades_qs = self.grades.all().select_related('subject')
        total_weight = 0
        total = 0
        for grade in grades_qs:
            credit = grade.subject.credit_hours
            total += grade.score * credit
            total_weight += credit
        return float(total / total_weight) if total_weight else 0.0

    def get_family_income_level_category(self):
        """Convert family income to a category (Low, Middle, High)."""
        if not hasattr(self, 'economic_situation') or not self.economic_situation.family_income_level:
            return "Low"
        income = float(self.economic_situation.family_income_level)
        if income < 500:
            return "Low"
        elif income < 2000:
            return "Middle"
        else:
            return "High"

    def calculate_academic_performance(self):
        """
        Calculate academic performance using a weighted formula.
        Factors: attendance, average score, study hours, motivation, stress,
                 gaming, social media, content, income, pressures.
        """
        norm_attendance = self.attendance_percentage / 100.0
        norm_score = self.get_average_score() / 100.0

        if hasattr(self, 'economic_situation') and self.economic_situation:
            norm_study = min(float(self.economic_situation.daily_study_hours or 0) / 10, 1)
        else:
            norm_study = 0

        if hasattr(self, 'health_information') and self.health_information:
            motivation = {"Low": 0, "Moderate": 0.5, "High": 1}.get(self.health_information.motivation, 0)
            stress = {"Low": 0, "Moderate": 0.5, "High": 1}.get(self.health_information.academic_stress, 0)
            pressures = {"None": 1, "Low": 0.75, "Moderate": 0.5, "High": 0.25}.get(
                self.health_information.family_pressures, 1
            )
        else:
            motivation = 0
            stress = 1
            pressures = 1

        if hasattr(self, 'tech_and_social') and self.tech_and_social:
            norm_gaming = min(float(self.tech_and_social.daily_gaming_hours or 0) / 5, 1)
            sm_value = {"Negative": 1, "Neutral": 0.5, "Positive": 0, "None": 0}.get(
                self.tech_and_social.social_media_impact_on_studies, 0
            )
            content_mapping = {
                "Educational": 1, "News": 0.8, "Sports": 0.7, "Entertainment": 0.5,
                "Gaming": 0.3, "Other": 0.6, "None": 0
            }
            content_value = content_mapping.get(self.tech_and_social.content_type_watched, 0)
        else:
            norm_gaming = 1
            sm_value = 0
            content_value = 0

        income_category = self.get_family_income_level_category()
        income_mapping = {"Low": 0, "Middle": 0.5, "High": 1}
        income_value = income_mapping.get(income_category, 0)

        weights = {
            "attendance": 0.20,
            "score": 0.35,
            "study": 0.15,
            "motivation": 0.10,
            "stress": 0.05,         # used as (1 - stress)
            "gaming": 0.05,         # used as (1 - norm_gaming)
            "social_media": 0.03,   # used as (1 - sm_value)
            "content": 0.03,
            "income": 0.02,
            "pressures": 0.02,
        }

        performance = (
            weights["attendance"] * norm_attendance +
            weights["score"] * norm_score +
            weights["study"] * norm_study +
            weights["motivation"] * motivation +
            weights["stress"] * (1 - stress) +
            weights["gaming"] * (1 - norm_gaming) +
            weights["social_media"] * (1 - sm_value) +
            weights["content"] * content_value +
            weights["income"] * income_value +
            weights["pressures"] * pressures
        )
        performance_score = performance * 100

        if performance_score >= 80:
            return "Excellent"
        elif performance_score >= 65:
            return "Good"
        elif performance_score >= 50:
            return "Average"
        else:
            return "Needs Improvement"

    def generate_report_data(self):
        """
        Returns a dictionary of report data for automatic report generation.
        """
        return {
            "Name": self.full_name,
            "Age": self.age,
            "Grade Level": self.grade_level,
            "Academic Performance": self.academic_performance,
            "Enrollment Date": str(self.enrollment_date),
            "Attendance": f"{self.attendance_percentage}%",
        }

# =============================================================================
# Health Information Model
# =============================================================================
class HealthInformation(models.Model):
    """Represents the health and psychological information of the student."""
    STRESS_LEVEL_CHOICES = [
        ("Low", "Low"),
        ("Moderate", "Moderate"),
        ("High", "High"),
    ]
    SLEEP_DISORDER_CHOICES = [
        ("None", "None"),
        ("Low", "Low"),
        ("Moderate", "Moderate"),
        ("High", "High"),
    ]
    STUDY_LIFE_BALANCE_CHOICES = [
        ("Needs Improvement", "Needs Improvement"),
        ("Moderate", "Moderate"),
        ("Good", "Good"),
    ]
    FAMILY_PRESSURES_CHOICES = [
        ("None", "None"),
        ("Low", "Low"),
        ("Moderate", "Moderate"),
        ("High", "High"),
    ]

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="health_information"
    )
    surgical_history = models.ManyToManyField("Surgery", blank=True)
    has_chronic_illness = models.BooleanField(default=False, help_text="Indicate if the student has any chronic illness.")
    chronic_illnesses_type = models.ManyToManyField("ChronicIllness", blank=True, help_text="List of chronic illnesses.")
    allergies = models.ManyToManyField("Allergy", blank=True)
    vaccinations = models.ManyToManyField("Vaccination", blank=True)
    eye_conditions = models.ManyToManyField("EyeCondition", blank=True)
    left_eye_vision = models.CharField(max_length=10, choices=LEFT_EYE_VISION, null=True, blank=True)
    right_eye_vision = models.CharField(max_length=10, choices=RIGHT_EYE_VISION, null=True, blank=True)
    DENTAL_HEALTH_CHOICES = [
        ("good", "Good"),
        ("needs follow up", "Needs Follow Up"),
    ]
    dental_health = models.CharField(max_length=100, choices=DENTAL_HEALTH_CHOICES, default="good", null=True, blank=True)
    EAR_HEALTH_CHOICES = [
        ("good", "Good"),
        ("needs follow up", "Needs Follow Up"),
    ]
    ear_health = models.CharField(max_length=100, choices=EAR_HEALTH_CHOICES, default="good", null=True, blank=True)
    GENERAL_HEALTH_STATUS_CHOICES = [
        ("good", "Good"),
        ("needs follow up", "Needs Follow Up"),
    ]
    general_health_status = models.CharField(max_length=100, choices=GENERAL_HEALTH_STATUS_CHOICES, default="good")
    last_medical_checkup = models.DateField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    BLOOD_TYPE_CHOICES = [
        ("O+", "O+"),
        ("O-", "O-"),
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
    ]
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, default="O+")
    disabilities = models.ManyToManyField("Disability", blank=True)
    academic_stress = models.CharField(max_length=100, choices=STRESS_LEVEL_CHOICES, default="Moderate")
    motivation = models.CharField(max_length=100, choices=STRESS_LEVEL_CHOICES, default="Moderate")
    depression = models.BooleanField(default=False)
    sleep_disorder = models.CharField(max_length=100, choices=SLEEP_DISORDER_CHOICES, default="None")
    anxiety = models.BooleanField(default=False)
    psychological_trauma = models.BooleanField(default=False)
    isolation_tendency = models.BooleanField(default=False)
    aggressive_behavior = models.BooleanField(default=False)
    personal_family_issues = models.BooleanField(default=False)
    bullying = models.BooleanField(default=False)
    study_life_balance = models.CharField(max_length=100, choices=STUDY_LIFE_BALANCE_CHOICES, default="Needs Improvement")
    psychological_support = models.BooleanField(default=True)
    psychological_notes = models.TextField(null=True, blank=True)
    family_pressures = models.CharField(max_length=100, choices=FAMILY_PRESSURES_CHOICES, default="None")
    # الحقول الحساسة التي سيتم تشفيرها:
    practices_masturbation = encrypt(models.BooleanField(default=False))
    abuse_at_home = encrypt(models.BooleanField(default=False))
    abuse_at_school = encrypt(models.BooleanField(default=False))
    sexual_harassment_at_home = encrypt(models.BooleanField(default=False))
    sexual_harassment_at_school = encrypt(models.BooleanField(default=False))
    alcohol_consumption = encrypt(models.BooleanField(default=False))
    smoking = encrypt(models.BooleanField(default=False))
    drug_use = encrypt(models.BooleanField(default=False))

    class Meta:
        verbose_name = "Health Information"
        verbose_name_plural = "Health Information"
        ordering = ["student__full_name"]

    def __str__(self):
        return f"Health Information for {self.student}"

# =============================================================================
# Economic Situation Model
# =============================================================================
class EconomicSituation(models.Model):
    """Represents the student's economic situation."""
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="economic_situation"
    )
    is_orphan = models.BooleanField(default=False, help_text="Indicates if the student is an orphan.")
    father_occupation = models.CharField(max_length=100, null=True, blank=True)
    mother_occupation = models.CharField(max_length=100, null=True, blank=True)
    parents_marital_status = models.CharField(
        max_length=100,
        choices=[
            ("Married", "Married"),
            ("Divorced", "Divorced"),
            ("Separated", "Separated"),
            ("Widowed", "Widowed"),
            ("Single", "Single")
        ],
        null=True,
        blank=True,
        help_text="Marital status of the student's parents"
    )
    family_income_level = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    income_source = models.CharField(max_length=100, choices=IncomeSourceChoices.choices, default=IncomeSourceChoices.OTHER)
    monthly_expenses = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    housing_status = models.CharField(max_length=100, choices=HousingStatusChoices.choices, null=True, blank=True)
    access_to_electricity = models.BooleanField(default=True)
    has_access_to_water = models.BooleanField(default=True)
    access_to_internet = models.BooleanField(default=False)
    has_private_study_room = models.BooleanField(default=False)
    number_of_rooms_in_home = models.PositiveIntegerField(null=True, blank=True)
    daily_food_availability = models.BooleanField(default=True)
    has_school_uniform = models.BooleanField(default=True)
    has_stationery = models.BooleanField(default=True)
    receives_financial_aid = models.BooleanField(default=False)
    receives_meal_assistance = models.BooleanField(default=False)
    receives_scholarship = models.BooleanField(default=False)
    receives_private_tutoring = models.BooleanField(default=False)
    daily_study_hours = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(24.0)])
    works_after_school = models.BooleanField(default=False)
    work_hours_per_week = models.FloatField(null=True, blank=True)
    responsible_for_household_tasks = models.BooleanField(default=False)
    transportation_mode = models.CharField(max_length=100, choices=TransportationModeChoices.choices, null=True, blank=True)
    distance_to_school = models.FloatField(null=True, blank=True)
    has_health_insurance = models.BooleanField(default=False)
    household_size = models.PositiveIntegerField(default=1)
    sibling_rank = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Economic Situation"
        verbose_name_plural = "Economic Situations"
        ordering = ["-id"]

    def __str__(self):
        return f"Economic Situation for {self.student.full_name}"

    @property
    def is_poor(self):
        if self.family_income_level is not None and self.monthly_expenses is not None:
            return self.family_income_level < (self.monthly_expenses * 2)
        return False

# =============================================================================
# Social Media and Technology Model
# =============================================================================
class SocialMediaAndTechnology(models.Model):
    """Represents the student's usage of electronic devices and social media."""
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='tech_and_social'
    )
    has_phone = models.BooleanField(default=False)
    has_laptop = models.BooleanField(default=False)
    has_tablet = models.BooleanField(default=False)
    has_pc = models.BooleanField(default=False)
    device_usage_purpose = models.CharField(max_length=100, choices=DeviceUsagePurposeChoices.choices,
                                            default=DeviceUsagePurposeChoices.OTHER)
    has_social_media_accounts = models.BooleanField(default=False)
    daily_screen_time = models.FloatField(default=0.0)
    social_media_impact_on_studies = models.CharField(max_length=100, choices=ImpactChoices.choices,
                                                      default=ImpactChoices.NONE)
    content_type_watched = models.CharField(max_length=100, choices=ContentTypeChoices.choices,
                                            default=ContentTypeChoices.OTHER)
    social_media_impact_on_sleep = models.CharField(max_length=100, choices=ImpactChoices.choices,
                                                    default=ImpactChoices.NONE)
    social_media_impact_on_focus = models.CharField(max_length=100, choices=ImpactChoices.choices,
                                                    default=ImpactChoices.NEUTRAL)
    plays_video_games = models.BooleanField(default=False)
    daily_gaming_hours = models.FloatField(default=0.0)
    aware_of_cybersecurity = models.BooleanField(default=False)
    experienced_electronic_extortion = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Social Media and Technology"
        verbose_name_plural = "Social Media and Technologies"
        ordering = ["-id"]

    def __str__(self):
        return f"Social Media and Technology for {self.student.full_name}"

# =============================================================================
# Grade Model
# =============================================================================
class Grade(models.Model):
    """Represents a student's grade in a specific subject."""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="grades"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="grades"
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("100.00"))
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade_level = models.CharField(max_length=100, blank=True, help_text="Grade (A, B, C, D, F)")
    exam_type = models.CharField(max_length=100, choices=ExamTypeChoices.choices, default=ExamTypeChoices.FINAL)
    semester = models.CharField(max_length=100, choices=SemesterChoices.choices, default=SemesterChoices.FALL)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_grades"
    )
    date_recorded = models.DateField(auto_now_add=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("1.00"))
    gpa_points = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    is_retake = models.BooleanField(default=False)
    improved_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        ordering = ["-date_recorded"]

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name}: {self.score}"

    def calculate_grade_metrics(self):
        if self.max_score and self.max_score > 0:
            self.percentage = (self.score / self.max_score) * Decimal("100")
        else:
            self.percentage = Decimal("0.00")
        for grade, threshold in SORTED_GRADE_THRESHOLDS:
            if self.percentage >= threshold:
                self.grade_level = grade
                break
        self.gpa_points = GPA_VALUES.get(self.grade_level, Decimal("0.0"))

    def save(self, *args, **kwargs):
        self.calculate_grade_metrics()
        if self.is_retake:
            original_grade = Grade.objects.filter(student=self.student, subject=self.subject, is_retake=False).order_by("-date_recorded").first()
            if original_grade and self.score > original_grade.score:
                self.improved_score = self.score - original_grade.score
        super().save(*args, **kwargs)
        self.update_performance()

    def update_performance(self):
        StudentPerformanceTrend = apps.get_model('students', 'StudentPerformanceTrend')
        grades = self.student.grades.filter(semester=self.semester).aggregate(
            avg_percentage=Avg("percentage"), avg_gpa=Avg("gpa_points")
        )
        StudentPerformanceTrend.objects.update_or_create(
            student=self.student,
            semester=self.semester,
            defaults={
                "average_percentage": grades["avg_percentage"] or 0,
                "gpa": grades["avg_gpa"] or 0,
            }
        )
        self.student.save()

# =============================================================================
# Grade History Model
# =============================================================================
class GradeHistory(models.Model):
    """Records the history of grade updates."""
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="history"
    )
    updated_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    previous_score = models.DecimalField(max_digits=5, decimal_places=2)
    new_score = models.DecimalField(max_digits=5, decimal_places=2)
    reason_for_update = models.CharField(max_length=200, null=True, blank=True,
                                         help_text="Reason for grade update")
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        updater = self.updated_by.full_name if self.updated_by else "Unknown Teacher"
        return f"{self.grade.student.full_name} - {self.grade.subject.name} updated by {updater}"

# =============================================================================
# Student Performance Trend Model
# =============================================================================
class StudentPerformanceTrend(models.Model):
    """Represents the student's performance trend for a specific semester."""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="performance_trends"
    )
    semester = models.CharField(max_length=100, choices=SemesterChoices.choices)
    average_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Student Performance Trend"
        verbose_name_plural = "Student Performance Trends"

    def __str__(self):
        return f"Performance Trend for {self.student.full_name} - {self.semester}"
