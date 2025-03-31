from django.db import models
from students.models import Student

class ReportStatus(models.TextChoices):
    NEW = "New", "New"
    IN_PROGRESS = "In Progress", "In Progress"
    COMPLETED = "Completed", "Completed"

class ReportCategory(models.TextChoices):
    PERSONAL = "personal", "Personal Information Report"
    GUARDIAN = "guardian", "Guardian Information Report"
    HEALTH = "health", "Health Information Report"
    ACADEMIC = "academic", "Academic Information Report"

class Report(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        help_text="The student to whom this report belongs."
    )
    category = models.CharField(
        max_length=20,
        choices=ReportCategory.choices,
        default=ReportCategory.PERSONAL,
        help_text="Report category (Personal, Guardian, Health, Academic)."
    )
    report_type = models.CharField(
        max_length=50,
        default="Automatic",
        help_text="Type or classification of the report."
    )
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.NEW,
        help_text="Current status of the report."
    )
    generated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time the report was generated."
    )
    data = models.JSONField(
        help_text="Additional report data in a flexible JSON format."
    )

    def __str__(self):
        return f"Report for {self.student.full_name} - {self.get_category_display()}"

# نموذج وهمي لإظهار رابط التقارير في لوحة الإدارة دون إنشاء جدول في قاعدة البيانات
class ReportsDashboard(models.Model):
    """
    Dummy model used to provide a link in Django Admin to the reports dashboard.
    This model does not create a database table.
    """
    class Meta:
        managed = False
        verbose_name = "Reports Dashboard"
        verbose_name_plural = "Reports Dashboard"
