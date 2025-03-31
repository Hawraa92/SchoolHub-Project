# reports/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from students.models import Student
from reports.models import ReportCategory
from .report_builder import ReportBuilder

@receiver(post_save, sender=Student)
def create_student_report(sender, instance, created, **kwargs):
    if created:
        # إنشاء تقرير افتراضي من نوع "المعلومات الشخصية" تلقائيًا عند إضافة الطالب
        builder = ReportBuilder(instance, ReportCategory.PERSONAL)
        builder.build()
