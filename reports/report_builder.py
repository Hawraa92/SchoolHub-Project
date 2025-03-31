# reports/report_builder.py

from reports.models import Report, ReportCategory
from students.models import Student

class ReportBuilder:
    def __init__(self, student, category):
        self.student = student
        self.category = category

    def build(self):
        """
        يقوم هذا الميثود بتحديد البيانات المطلوبة بناءً على فئة التقرير وإنشاء التقرير تلقائيًا.
        """
        if self.category == ReportCategory.PERSONAL:
            data = self.build_personal_data()
        elif self.category == ReportCategory.GUARDIAN:
            data = self.build_guardian_data()
        elif self.category == ReportCategory.HEALTH:
            data = self.build_health_data()
        elif self.category == ReportCategory.ACADEMIC:
            data = self.build_academic_data()
        else:
            data = {}

        report = Report.objects.create(
            student=self.student,
            category=self.category,
            report_type="Automatic",
            data=data
        )
        return report

    def build_personal_data(self):
        """
        يجمع بيانات الطالب الشخصية.
        """
        student = self.student
        return {
            "Full Name": student.full_name,
            "Date of Birth": str(student.date_of_birth),
            "Gender": student.gender,
            "Email": student.email,
            "Mobile": student.mobile,
            "Nationality": student.nationality,
            "Address": student.address,
        }

    def build_guardian_data(self):
        """
        يجمع بيانات الوصي الخاصة بالطالب.
        """
        student = self.student
        return {
            "Guardian Name": student.guardian_name,
            "Guardian Relationship": student.guardian_relationship,
            "Guardian Contact": student.guardian_contact,
            "Guardian Address": student.guardian_address,
            "Guardian Job Title": student.guardian_job_title,
            "Guardian Monthly Income": str(student.guardian_monthly_income or "N/A"),
        }

    def build_health_data(self):
        """
        يجمع بيانات الصحة الخاصة بالطالب.
        """
        student = self.student
        if hasattr(student, 'health_information'):
            health = student.health_information
            return {
                "Dental Health": health.dental_health,
                "Ear Health": health.ear_health,
                "General Health": health.general_health_status,
                "Last Medical Checkup": str(health.last_medical_checkup) if health.last_medical_checkup else "N/A",
                "Weight": health.weight,
                "Height": health.height,
                "Blood Type": health.blood_type,
            }
        return {"Health Information": "Not Available"}

    def build_academic_data(self):
        """
        يجمع بيانات الطالب الأكاديمية.
        """
        student = self.student
        data = student.generate_report_data()  # دالة موجودة في موديل Student
        data["Subjects"] = [subject.name for subject in student.subjects.all()]
        data["Attendance"] = f"{student.attendance_percentage}%"
        return data
