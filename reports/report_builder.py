from reports.models import Report, ReportCategory
from students.models import Student

class ReportBuilder:
    def __init__(self, student, category):
        self.student = student
        self.category = category

    def build(self):
        """
        Build report data based on the selected category and create a Report.
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
        student = self.student
        return {
            "Guardian Relationship": student.guardian_relationship,
            "Guardian Address": student.guardian_address,
            "Guardian Employment Status": student.guardian_employment_status,
            "Guardian Monthly Income": str(student.guardian_monthly_income or "N/A"),
            "Guardian Education": student.guardian_education,
        }

    def build_health_data(self):
        student = self.student
        if hasattr(student, 'health_information'):
            health = student.health_information
            return {
                "Has Chronic Illness": health.has_chronic_illness,
                "General Health": health.general_health_status,
                "Last Medical Checkup": str(health.last_medical_checkup) if health.last_medical_checkup else "N/A",
                "Weight": health.weight,
                "Height": health.height,
                "Academic Stress": health.academic_stress,
                "Motivation": health.motivation,
                "Depression": health.depression,
                "Sleep Disorder": health.sleep_disorder,
                "Study Life Balance": health.study_life_balance,
                "Family Pressures": health.family_pressures,
            }
        return {"Health Information": "Not Available"}

    def build_academic_data(self):
        student = self.student
        # Since there is no generate_report_data() method in Student,
        # we create our own basic academic summary.
        data = {
            "Grade Level": student.grade_level,
            "Attendance Percentage": f"{student.attendance_percentage}%",
            "Academic Performance": student.academic_performance,
            "Average Score": student.get_average_score(),
        }
        # Include subject names if available.
        data["Subjects"] = [subject.name for subject in student.subjects.all()]
        return data
