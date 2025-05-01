"""
SchoolHub – School Management System Models (Optimized Version)

This file contains models covering health, academic, social, and economic aspects of students.
Unused fields have been removed from HealthInformation, retaining only the fields required for detailed analysis.
"""

import uuid
import logging
from datetime import date, datetime
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator
from django.apps import apps
from PIL import Image

from teachers.models import Teacher  # Used in the Grade model

logger = logging.getLogger(__name__)

# =============================================================================
# Constants and Choices
# =============================================================================

class GenderChoices(models.TextChoices):
    MALE = "Male", "Male"
    FEMALE = "Female", "Female"

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

class DeviceUsagePurposeChoices(models.TextChoices):
    EDUCATION = "Education", "Education"
    ENTERTAINMENT = "Entertainment", "Entertainment"
    GAMING = "Gaming", "Gaming"
    WORK = "Work", "Work"
    OTHER = "Other", "Other"

class IncomeSourceChoices(models.TextChoices):
    SALARY = "Salary", "Salary"
    BUSINESS = "Business", "Business"
    AID = "Aid", "Aid"
    OTHER = "Other", "Other"

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

# A custom QuerySet for Student
class StudentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

# =============================================================================
# Optional Models
# =============================================================================

class ChronicIllness(models.Model):
    """Represents a chronic illness."""
    name = models.CharField(max_length=100, unique=True, help_text="Name of the chronic illness")

    class Meta:
        verbose_name = "Chronic Illness"
        verbose_name_plural = "Chronic Illnesses"

    def __str__(self):
        return self.name

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

class Disability(models.Model):
    """Represents a disability or special need."""
    name = models.CharField(max_length=100, unique=True, help_text="Name of the disability")
    description = models.TextField(null=True, blank=True, help_text="Optional description")

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
    student_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="Student ID",
        help_text="Unique identifier for the student"
    )
    enrollment_date = models.DateField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=100, choices=GenderChoices.choices)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField()
    profile_image = models.ImageField(upload_to="student_profiles/", null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    mobile = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    emergency_contact_name = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="Name of emergency contact"
    )
    emergency_contact = models.CharField(
        max_length=100,
        help_text="Emergency contact number"
    )

    # Guardian Information
    guardian_relationship = models.CharField(
        max_length=100,
        choices=GuardianRelationshipChoices.choices
    )
    guardian_address = models.TextField(null=True, blank=True)
    guardian_employment_status = models.CharField(
        max_length=100,
        choices=EmploymentStatusChoices.choices,
        default=EmploymentStatusChoices.EMPLOYED
    )
    guardian_monthly_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    guardian_education = models.CharField(
        max_length=100,
        choices=EducationChoices.choices,
        default=EducationChoices.ILLITERATE
    )

    # Academic Information
    subjects = models.ManyToManyField(Subject, blank=True, related_name="students")
    grade_level = models.CharField(
        max_length=100, choices=GRADE_LEVEL_CHOICES, null=True, blank=True
    )
    attendance_percentage = models.FloatField(default=0.0)
    academic_performance = models.CharField(
        max_length=100,
        choices=ACADEMIC_PERFORMANCE_CHOICES,
        null=True,
        blank=True
    )
    awards = models.TextField(null=True, blank=True)
    seat_zone = models.CharField(
        max_length=10,
        choices=[("Front", "Front"), ("Middle", "Middle"), ("Back", "Back"), ("Side", "Side")],
        default="Middle"
    )
    is_active = models.BooleanField(default=True)

    objects = StudentQuerySet.as_manager()

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        """Calculate and return the student's age."""
        today = date.today()
        if self.date_of_birth:
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def is_orphan(self):
        """Determine if the student is an orphan based on their economic situation."""
        return getattr(self, 'economic_situation', None) and self.economic_situation.is_orphan

    # -------------------------- UPDATED SAVE() --------------------------
    def save(self, *args, **kwargs):
        # Save the student instance first if creating a new instance to set self.pk.
        creating_new = self.pk is None
        if creating_new:
            super().save(*args, **kwargs)
        # Calculate academic performance using the new weighted formula.
        self.academic_performance, _ = self.calculate_academic_performance()
        # Remove force_insert from kwargs if present to avoid duplicate insertion.
        if 'force_insert' in kwargs:
            kwargs.pop('force_insert')
        # Save again to persist the updated academic performance.
        super().save(*args, **kwargs)
        # Resize profile image if necessary.
        if self.profile_image:
            # Check if the image name starts with "http" (i.e., it's a URL)
            if self.profile_image.name.lower().startswith("http"):
                # Skip image processing if it's a URL.
                pass
            else:
                try:
                    img = Image.open(self.profile_image.path)
                    if img.height > 300 or img.width > 300:
                        img.thumbnail((300, 300))
                        img.save(self.profile_image.path)
                except Exception:
                    logger.exception("Error processing profile image for student: %s", self.full_name)
    # -------------------------------------------------------------------

    def get_average_score(self):
        """Calculate the weighted average score from related Grade objects."""
        grades_qs = self.grades.all().select_related('subject')
        total_weight = 0
        total_score = 0
        for grade in grades_qs:
            credit = grade.subject.credit_hours
            total_score += grade.score * credit
            total_weight += credit
        return float(total_score / total_weight) if total_weight else 0.0

    def get_family_income_level_category(self):
        """Return 'Low', 'Middle', or 'High' based on family income level."""
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
        Calculate academic performance index (0 to 1) and category.
        
        This new formula normalizes academic, psychosocial, technology, and socioeconomic factors,
        applies weighted contributions, and returns a performance category along with the performance index.
        """
        # 1. Normalize core academic metrics
        norm_attendance = self.attendance_percentage / 100.0            # Attendance rate (0 to 1)
        norm_score = self.get_average_score() / 100.0                    # Average score (0 to 1)
        norm_study = (
            min(self.economic_situation.daily_study_hours / 10.0, 1)
            if hasattr(self, 'economic_situation') and self.economic_situation else 0
        )
        
        # 2. Encode psychosocial factors from HealthInformation
        if hasattr(self, 'health_information') and self.health_information:
            motivation_val = {"Low": 0.0, "Moderate": 0.5, "High": 1.0}.get(self.health_information.motivation, 0.5)
            stress_val = {"Low": 0.0, "Moderate": 0.5, "High": 1.0}.get(self.health_information.academic_stress, 0.5)
            depression_val = 0.0 if not self.health_information.depression else 1.0
            balance_val = {"Needs Improvement": 0.0, "Moderate": 0.5, "Good": 1.0}.get(self.health_information.study_life_balance, 0.5)
            pressure_val = {"None": 1.0, "Low": 0.75, "Moderate": 0.5, "High": 0.25}.get(self.health_information.family_pressures, 0.5)
        else:
            motivation_val = 0.5
            stress_val = 0.5
            depression_val = 0.0
            balance_val = 0.5
            pressure_val = 0.5
        
        # 3. Encode technology/social factors from SocialMediaAndTechnology
        if hasattr(self, 'tech_and_social') and self.tech_and_social:
            daily_gaming_hours = self.tech_and_social.daily_gaming_hours
            # If the student does not game, consider negative impact as 0 (beneficial)
            gaming_val = 1 - min(daily_gaming_hours / 5.0, 1.0) if daily_gaming_hours > 0 else 1.0
            sm_impact_val = {"Negative": 1.0, "Neutral": 0.5, "Positive": 0.0}.get(self.tech_and_social.social_media_impact_on_studies, 0.0)
            sm_val = 1 - sm_impact_val  # Invert social media impact: higher negative impact gives a lower value
            content_val = {"Educational": 1.0, "News": 0.8, "Sports": 0.7, "Entertainment": 0.5,
                           "Gaming": 0.3, "Other": 0.6}.get(self.tech_and_social.content_type_watched, 0.0)
        else:
            gaming_val = 1.0
            sm_val = 1.0
            content_val = 0.0
        
        # 4. Encode socioeconomic factor
        income_category = (
            self.get_family_income_level_category()
            if hasattr(self, 'economic_situation') and self.economic_situation else "Low"
        )
        income_val = {"Low": 0.0, "Middle": 0.5, "High": 1.0}.get(income_category, 0.5)
        
        # 5. Weights for each factor (total weights sum to 1.0)
        weights = {
            "attendance": 0.20,
            "score": 0.35,
            "study": 0.10,
            "motivation": 0.10,
            "stress": 0.05,       # Using (1 - stress_val) in calculation (high stress reduces performance)
            "depression": 0.05,   # Absence of depression is beneficial
            "balance": 0.05,
            "pressures": 0.02,
            "gaming": 0.03,       # gaming_val is already inverted (more gaming reduces performance)
            "social_media": 0.02, # Using inverted social media impact (sm_val)
            "content": 0.01,
            "income": 0.02
        }
        
        # 6. Compute performance index (ranging from 0.0 to 1.0)
        perf_index = (
            weights["attendance"] * norm_attendance +
            weights["score"] * norm_score +
            weights["study"] * norm_study +
            weights["motivation"] * motivation_val +
            weights["stress"] * (1 - stress_val) +
            weights["depression"] * (1 - depression_val) +
            weights["balance"] * balance_val +
            weights["pressures"] * pressure_val +
            weights["gaming"] * gaming_val +
            weights["social_media"] * sm_val +
            weights["content"] * content_val +
            weights["income"] * income_val
        )
        
        # 7. Determine performance category based on thresholds
        if perf_index >= 0.80:
            performance_category = "Excellent"
        elif perf_index >= 0.60:
            performance_category = "Average"
        else:
            performance_category = "Needs Improvement"
        return performance_category, perf_index

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
    exam_type = models.CharField(
        max_length=100,
        choices=ExamTypeChoices.choices,
        default=ExamTypeChoices.FINAL
    )
    semester = models.CharField(
        max_length=100,
        choices=SemesterChoices.choices,
        default=SemesterChoices.FALL
    )
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

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        ordering = ["-date_recorded"]

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name}: {self.score}"

    def calculate_grade_metrics(self):
        """Calculate the percentage, grade level, and GPA points based on the score."""
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
        super().save(*args, **kwargs)
        self.update_performance()

    def update_performance(self):
        """Update or create the StudentPerformanceTrend based on this grade."""
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
    reason_for_update = models.CharField(max_length=200, null=True, blank=True, help_text="Reason for grade update")
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        updater = self.updated_by.full_name if self.updated_by else "Unknown Teacher"
        return f"{self.grade.student.full_name} - {self.grade.subject.name} updated by {updater}"

# =============================================================================
# HealthInformation Model (Only Requested Fields)
# =============================================================================

class HealthInformation(models.Model):
    """
    Represents the student's health and psychological information.
    Physical: has_chronic_illness, general_health_status, last_medical_checkup, weight, height.
    Psychological: academic_stress, motivation, depression, sleep_disorder, study_life_balance, family_pressures.
    """
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
    GENERAL_HEALTH_STATUS_CHOICES = [
        ("good", "Good"),
        ("needs follow up", "Needs Follow Up"),
    ]

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="health_information"
    )
    # Physical Health Fields
    has_chronic_illness = models.BooleanField(default=False)
    general_health_status = models.CharField(
        max_length=100,
        choices=GENERAL_HEALTH_STATUS_CHOICES,
        default="good"
    )
    last_medical_checkup = models.DateField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)

    # Psychological/Behavioral Fields
    academic_stress = models.CharField(
        max_length=100,
        choices=STRESS_LEVEL_CHOICES,
        default="Moderate"
    )
    motivation = models.CharField(
        max_length=100,
        choices=STRESS_LEVEL_CHOICES,
        default="Moderate"
    )
    depression = models.BooleanField(default=False)
    sleep_disorder = models.CharField(
        max_length=100,
        choices=SLEEP_DISORDER_CHOICES,
        default="None"
    )
    study_life_balance = models.CharField(
        max_length=100,
        choices=STUDY_LIFE_BALANCE_CHOICES,
        default="Needs Improvement"
    )
    family_pressures = models.CharField(
        max_length=100,
        choices=FAMILY_PRESSURES_CHOICES,
        default="None"
    )

    class Meta:
        verbose_name = "Health Information"
        verbose_name_plural = "Health Information"

    def __str__(self):
        return f"Health Information for {self.student}"

# =============================================================================
# EconomicSituation Model
# =============================================================================

class EconomicSituation(models.Model):
    """Represents the student's economic situation."""
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="economic_situation"
    )
    is_orphan = models.BooleanField(default=False)
    father_occupation = models.CharField(max_length=100, null=True, blank=True)
    mother_occupation = models.CharField(max_length=100, null=True, blank=True)
    parents_marital_status = models.CharField(
        max_length=100,
        choices=[("Married", "Married"), ("Divorced", "Divorced"), ("Separated", "Separated"),
                 ("Widowed", "Widowed"), ("Single", "Single")],
        null=True,
        blank=True,
        help_text="Marital status of the student's parents"
    )
    family_income_level = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    income_source = models.CharField(
        max_length=100,
        choices=IncomeSourceChoices.choices,
        default=IncomeSourceChoices.OTHER
    )
    monthly_expenses = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    housing_status = models.CharField(
        max_length=100,
        choices=HousingStatusChoices.choices,
        null=True,
        blank=True
    )
    access_to_electricity = models.BooleanField(default=True)
    has_access_to_water = models.BooleanField(default=True)
    access_to_internet = models.BooleanField(default=False)
    has_private_study_room = models.BooleanField(default=False)
    number_of_rooms_in_home = models.PositiveIntegerField(null=True, blank=True)
    daily_food_availability = models.BooleanField(default=True)
    has_school_uniform = models.BooleanField(default=True)
    has_stationery = models.BooleanField(default=True)
    receives_scholarship = models.BooleanField(default=False)
    receives_private_tutoring = models.BooleanField(default=False)
    daily_study_hours = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(24.0)])
    works_after_school = models.BooleanField(default=False)
    work_hours_per_week = models.FloatField(null=True, blank=True)
    responsible_for_household_tasks = models.BooleanField(default=False)
    transportation_mode = models.CharField(
        max_length=100,
        choices=TransportationModeChoices.choices,
        null=True,
        blank=True
    )
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
        """Determine if the family is poor based on income and monthly expenses."""
        if self.family_income_level is not None and self.monthly_expenses is not None:
            return self.family_income_level < (self.monthly_expenses * 2)
        return False

# =============================================================================
# SocialMediaAndTechnology Model
# =============================================================================

class SocialMediaAndTechnology(models.Model):
    """Represents the student's usage of electronic devices and social media."""
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='tech_and_social'
    )
    has_electronic_device = models.BooleanField(default=False, help_text="Does the student own an electronic device?")
    device_usage_purpose = models.CharField(
        max_length=100,
        choices=DeviceUsagePurposeChoices.choices,
        default=DeviceUsagePurposeChoices.OTHER,
        help_text="Primary purpose of device usage"
    )
    has_social_media_accounts = models.BooleanField(default=False, help_text="Does the student have social media accounts?")
    daily_screen_time = models.FloatField(default=0.0, help_text="Daily screen time in hours")
    social_media_impact_on_studies = models.CharField(
        max_length=100,
        choices=ImpactChoices.choices,
        default=ImpactChoices.NONE,
        help_text="Impact of social media on studies"
    )
    content_type_watched = models.CharField(
        max_length=100,
        choices=ContentTypeChoices.choices,
        default=ContentTypeChoices.OTHER,
        help_text="Type of content watched"
    )
    social_media_impact_on_sleep = models.CharField(
        max_length=100,
        choices=ImpactChoices.choices,
        default=ImpactChoices.NONE,
        help_text="Impact on sleep"
    )
    social_media_impact_on_focus = models.CharField(
        max_length=100,
        choices=ImpactChoices.choices,
        default=ImpactChoices.NEUTRAL,
        help_text="Impact on focus"
    )
    plays_video_games = models.BooleanField(default=False, help_text="Does the student play video games?")
    daily_gaming_hours = models.FloatField(default=0.0, help_text="Daily gaming hours")
    aware_of_cybersecurity = models.BooleanField(default=False, help_text="Is the student aware of cybersecurity risks?")
    experienced_electronic_extortion = models.BooleanField(default=False, help_text="Has the student experienced electronic extortion?")

    class Meta:
        verbose_name = "Social Media and Technology"
        verbose_name_plural = "Social Media and Technology"
        ordering = ["-id"]

    def __str__(self):
        return f"Social Media and Technology for {self.student.full_name}"

# =============================================================================
# StudentPerformanceTrend Model
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
