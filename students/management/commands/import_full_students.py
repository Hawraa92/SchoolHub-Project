import csv
import os
from decimal import Decimal
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')
import django
django.setup()

# استيراد النماذج المطلوبة
from accounts.models import User
from students.models import (
    Student,
    Subject,
    Grade,
    HealthInformation,
    EconomicSituation,
    SocialMediaAndTechnology,
)

class Command(BaseCommand):
    help = "Import the first 10 rows from students_cleaned_final.csv into Student and related models."

    def parse_date(self, s):
        """Convert a string in YYYY-MM-DD format to a date object."""
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def parse_decimal(self, s):
        try:
            return Decimal(s)
        except Exception:
            return Decimal("0.0")

    def parse_float(self, s):
        try:
            return float(s)
        except Exception:
            return 0.0

    def str_to_bool(self, s):
        if isinstance(s, str):
            return s.strip().lower() in ['yes', 'true', '1']
        return bool(s)

    def handle(self, *args, **options):
        csv_path = r"C:\Users\Hawraa\Downloads\students_cleaned_final.csv"
        if not os.path.exists(csv_path):
            raise CommandError(f"The file {csv_path} does not exist.")

        # لحل مشكلة التكرار أثناء الاختبار (يتم حذف سجلات الطلاب الحالية)
        Student.objects.all().delete()
        self.stdout.write("All existing Student records have been deleted for testing purposes.")

        with open(csv_path, mode='r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            # الاحتفاظ بأول 10 صفوف فقط للاختبار
            rows = rows[:10]

            success_count = 0
            error_count = 0

            for idx, row in enumerate(rows):
                self.stdout.write(f"Processing row {idx+1}...")
                try:
                    with transaction.atomic():
                        # إنشاء أو جلب المستخدم
                        username = row.get('user', '').strip()
                        if not username:
                            raise ValueError("Missing 'user' field.")
                        email = row.get('email', f"{username}@example.com").strip()
                        user_obj, created = User.objects.get_or_create(
                            username=username,
                            defaults={'email': email}
                        )

                        # معالجة بيانات الطالب
                        enrollment_date = self.parse_date(row.get('enrollment_date', ''))
                        dob = self.parse_date(row.get('date_of_birth', ''))
                        if not enrollment_date or not dob:
                            raise ValueError("Missing enrollment_date or date_of_birth.")
                        gender = row.get('gender', 'Male').strip()
                        student_defaults = {
                            "full_name": row.get('full_name', '').strip(),
                            "enrollment_date": enrollment_date,
                            "date_of_birth": dob,
                            "gender": gender if gender in ["Male", "Female"] else "Male",
                            "nationality": row.get('nationality', 'Not Specified').strip(),
                            "address": row.get('address', 'Not Specified').strip(),
                            "profile_image": row.get('profile_image', '').strip(),
                            "email": email,
                            "mobile": row.get('mobile', '').strip(),
                            "emergency_contact_name": row.get('emergency_contact_name', 'Not Specified').strip(),
                            "emergency_contact": row.get('emergency_contact', 'Not Specified').strip(),
                            "guardian_relationship": row.get('guardian_relationship', 'Other').strip(),
                            "guardian_address": row.get('guardian_address', 'Not Specified').strip(),
                            "guardian_employment_status": row.get('guardian_employment_status', 'Employed').strip(),
                            "guardian_monthly_income": self.parse_decimal(row.get('guardian_monthly_income', '0')),
                            "guardian_education": row.get('guardian_education', 'Not Specified').strip(),
                            "grade_level": row.get('grade_level', '').strip(),
                            "attendance_percentage": self.parse_float(row.get('attendance_percentage', '0')),
                            "awards": row.get('awards', '').strip(),
                            "seat_zone": row.get('seat_zone', 'Middle').strip(),
                        }
                        student_obj, stu_created = Student.objects.update_or_create(
                            user=user_obj,
                            defaults=student_defaults
                        )
                        if stu_created:
                            self.stdout.write(f"Created student: {student_obj.full_name}")
                        else:
                            self.stdout.write(f"Updated student: {student_obj.full_name}")

                        # معالجة المواد الدراسية (subjects)
                        subjects_str = row.get('subjects', '').strip()
                        if subjects_str:
                            student_obj.subjects.clear()
                            for subj_name in subjects_str.split(','):
                                subj_name = subj_name.strip()
                                if subj_name:
                                    subj_obj, _ = Subject.objects.get_or_create(name=subj_name)
                                    student_obj.subjects.add(subj_obj)

                        # معالجة الدرجات بصيغة "subject:score;subject:score;..."
                        grades_str = row.get('grades', '').strip()
                        if grades_str:
                            for grade_item in grades_str.split(';'):
                                if ':' in grade_item:
                                    subj, score = grade_item.split(':', 1)
                                    subj = subj.strip()
                                    score = self.parse_decimal(score.strip())
                                    if subj:
                                        subj_obj, _ = Subject.objects.get_or_create(name=subj)
                                        Grade.objects.create(
                                            student=student_obj,
                                            subject=subj_obj,
                                            score=score
                                        )

                        # معالجة HealthInformation
                        raw_family_pressures = row.get('family_pressures', '').strip()
                        if raw_family_pressures.lower() in ["", "not specified"]:
                            raw_family_pressures = "None"
                        health_defaults = {
                            "has_chronic_illness": self.str_to_bool(row.get('has_chronic_illness', '')),
                            "general_health_status": row.get('general_health_status', 'good').strip(),
                            "last_medical_checkup": self.parse_date(row.get('last_medical_checkup', '')),
                            "weight": self.parse_float(row.get('weight', '0')),
                            "height": self.parse_float(row.get('height', '0')),
                            "academic_stress": row.get('academic_stress', 'Moderate').strip(),
                            "motivation": row.get('motivation', 'Moderate').strip(),
                            "depression": self.str_to_bool(row.get('depression', '')),
                            "sleep_disorder": row.get('sleep_disorder', 'None').strip(),
                            "study_life_balance": row.get('study_life_balance', 'Needs Improvement').strip(),
                            "family_pressures": raw_family_pressures,
                        }
                        HealthInformation.objects.update_or_create(
                            student=student_obj,
                            defaults=health_defaults
                        )

                        # معالجة EconomicSituation
                        econ_defaults = {
                            "is_orphan": self.str_to_bool(row.get('is_orphan', '')),
                            "father_occupation": row.get('father_occupation', '').strip(),
                            "mother_occupation": row.get('mother_occupation', '').strip(),
                            "parents_marital_status": row.get('parents_marital_status', '').strip(),
                            "family_income_level": self.parse_decimal(row.get('family_income_level', '0')),
                            "income_source": row.get('income_source', 'Other').strip(),
                            "monthly_expenses": self.parse_decimal(row.get('monthly_expenses', '0')),
                            "housing_status": row.get('housing_status', '').strip(),
                            "access_to_electricity": self.str_to_bool(row.get('access_to_electricity', '')),
                            "has_access_to_water": self.str_to_bool(row.get('has_access_to_water', '')),
                            "access_to_internet": self.str_to_bool(row.get('access_to_internet', '')),
                            "has_private_study_room": self.str_to_bool(row.get('has_private_study_room', '')),
                            "number_of_rooms_in_home": int(row.get('number_of_rooms_in_home', '0') or 0),
                            "daily_food_availability": self.str_to_bool(row.get('daily_food_availability', '')),
                            "has_school_uniform": self.str_to_bool(row.get('has_school_uniform', '')),
                            "has_stationery": self.str_to_bool(row.get('has_stationery', '')),
                            "receives_scholarship": self.str_to_bool(row.get('receives_scholarship', '')),
                            "receives_private_tutoring": self.str_to_bool(row.get('receives_private_tutoring', '')),
                            "daily_study_hours": self.parse_float(row.get('daily_study_hours', '0')),
                            "works_after_school": self.str_to_bool(row.get('works_after_school', '')),
                            "work_hours_per_week": self.parse_float(row.get('work_hours_per_week', '0')),
                            "responsible_for_household_tasks": self.str_to_bool(row.get('responsible_for_household_tasks', '')),
                            "transportation_mode": row.get('transportation_mode', '').strip(),
                            "distance_to_school": self.parse_float(row.get('distance_to_school', '0')),
                            "has_health_insurance": self.str_to_bool(row.get('has_health_insurance', '')),
                            "household_size": int(row.get('household_size', '1') or 1),
                            "sibling_rank": int(row.get('sibling_rank', '0') or 0),
                        }
                        EconomicSituation.objects.update_or_create(
                            student=student_obj,
                            defaults=econ_defaults
                        )

                        # معالجة SocialMediaAndTechnology
                        raw_smi = row.get('social_media_impact_on_studies', '').strip()
                        if raw_smi.lower() in ["", "not specified"]:
                            raw_smi = "None"
                        raw_ctw = row.get('content_type_watched', '').strip()
                        if raw_ctw.lower() in ["", "not specified"]:
                            raw_ctw = "None"
                        tech_defaults = {
                            "has_electronic_device": self.str_to_bool(row.get('has_electronic_device', '')),
                            "device_usage_purpose": row.get('device_usage_purpose', 'Other').strip(),
                            "has_social_media_accounts": self.str_to_bool(row.get('has_social_media_accounts', '')),
                            "daily_screen_time": self.parse_float(row.get('daily_screen_time', '0')),
                            "social_media_impact_on_studies": raw_smi,
                            "content_type_watched": raw_ctw,
                            "social_media_impact_on_sleep": row.get('social_media_impact_on_sleep', 'None').strip(),
                            "social_media_impact_on_focus": row.get('social_media_impact_on_focus', 'Neutral').strip(),
                            "plays_video_games": self.str_to_bool(row.get('plays_video_games', '')),
                            "daily_gaming_hours": self.parse_float(row.get('daily_gaming_hours', '0')),
                            "aware_of_cybersecurity": self.str_to_bool(row.get('aware_of_cybersecurity', '')),
                            "experienced_electronic_extortion": self.str_to_bool(row.get('experienced_electronic_extortion', '')),
                        }
                        SocialMediaAndTechnology.objects.update_or_create(
                            student=student_obj,
                            defaults=tech_defaults
                        )

                        success_count += 1

                except Exception as e:
                    error_count += 1
                    self.stderr.write(f"Error in row {idx+1}: {e}")

            self.stdout.write(
                f"Import completed: {success_count} rows imported successfully, "
                f"{error_count} rows failed out of {len(rows)} total rows."
            )
