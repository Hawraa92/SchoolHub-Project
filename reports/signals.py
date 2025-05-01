from django.db.models.signals import post_save
from django.dispatch import receiver
from students.models import Student
from reports.models import ReportCategory
from .report_builder import ReportBuilder

@receiver(post_save, sender=Student)
def create_student_report(sender, instance, created, **kwargs):
    if created:
        builder = ReportBuilder(instance, ReportCategory.PERSONAL)
        builder.build()
