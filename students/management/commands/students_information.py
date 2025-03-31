import uuid
import pandas as pd
from decimal import Decimal
from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps

from accounts.models import User
from students.models import (
    Student, HealthInformation, EconomicSituation,
    SocialMediaAndTechnology, Grade, Subject, ChronicIllness,
)

class Command(BaseCommand):
    help = 'Import complete student data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV file to be imported'
        )

    def str_to_bool(self, s):
        """تحويل النص إلى قيمة منطقية"""
        if isinstance(s, str):
            return s.strip().lower() in ['yes', 'true', '1']
        return bool(s)

    def parse_date(self, date_str):
        """تحويل النص إلى تاريخ باستخدام pandas"""
        try:
            ts = pd.to_datetime(date_str, errors='coerce')
            return ts.date() if pd.notnull(ts) else None
        except Exception:
            return None

    def parse_decimal(self, value):
        """تحويل القيمة إلى Decimal"""
        try:
            return Decimal(value) if value else None
        except Exception:
            return None

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        self.stdout.write(self.style.NOTICE(f"Starting import from {file_path}"))

        try:
            df = pd.read_csv(file_path)
            # إزالة الصفوف المكررة بناءً على عمود البريد الإلكتروني
            df.drop_duplicates(subset=['Email'], inplace=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading CSV file: {e}"))
            return

        total_rows = df.shape[0]
        success_count = 0
        error_count = 0

        for index, row in df.iterrows():
            self.stdout.write(f"Processing row {index+1} of {total_rows}...")
            try:
                with transaction.atomic():
                    # الحصول على بيانات المستخدم
                    username = row.get('User')
                    email = row.get('Email', f"{username}@example.com")
                    if not username:
                        raise ValueError("Username is missing")

                    user, _ = User.objects.get_or_create(
                        username=username,
                        defaults={'email': email}
                    )

                    # تجاهل قيمة "Student id" الموجودة في الملف وتوليد uuid جديد
                    student_uuid = uuid.uuid4()

                    # إنشاء الطالب دون تضمين academic_performance
                    student = Student(
                        user=user,
                        full_name=str(row.get('Full name', '')).strip(),
                        enrollment_date=self.parse_date(row.get('Enrollment date')),
                        date_of_birth=self.parse_date(row.get('Date of birth')),
                        gender=row.get('Gender'),
                        nationality=row.get('Nationality'),
                        marital_status=row.get('Marital status'),
                        address=row.get('Address'),
                        email=email,
                        mobile=row.get('Mobile'),
                        spoken_language=row.get('Spoken language', 'Arabic'),
                        emergency_contact_name=row.get('Emergency contact name'),
                        emergency_contact=row.get('Emergency Contact'),
                        guardian_name=row.get('Guardian name'),
                        guardian_relationship=row.get('Guardian relationship'),
                        guardian_contact=row.get('Guardian contact'),
                        guardian_address=row.get('Guardian address'),
                        guardian_job_title=row.get('Guardian job title'),
                        guardian_employment_status=row.get('Guardian employment status'),
                        guardian_monthly_income=(self.parse_decimal(row.get('Guardian monthly income'))
                                                   if row.get('Guardian monthly income') else None),
                        guardian_education=row.get('Guardian education'),
                        grade_level=row.get('Grade level'),
                        attendance_percentage=float(row.get('Attendance percentage')) if row.get('Attendance percentage') else 0.0,
                        awards=row.get('Awards'),
                        seat_zone=row.get('Seat zone', 'Middle')
                    )
                    student.save()  # حفظ الطالب أولًا للحصول على Primary Key

                    # حساب الأداء الأكاديمي بعد حفظ الطالب
                    try:
                        student.performance_score = calculate_student_performance(student)
                    except Exception:
                        student.performance_score = Decimal("0.00")
                    student.save()  # حفظ الأداء الأكاديمي بعد حسابه

                    # إضافة المواد الدراسية (Subjects)
                    subjects_str = row.get('Subjects')
                    if isinstance(subjects_str, str) and subjects_str.strip():
                        for subj_name in subjects_str.split(','):
                            subj_name = subj_name.strip()
                            if subj_name:
                                subj, _ = Subject.objects.get_or_create(name=subj_name)
                                student.subjects.add(subj)

                    # إضافة الأمراض المزمنة للوصي إذا كانت متوفرة وغير "none"
                    guardian_illnesses = row.get('Guardian chronic illnesses', '')
                    if isinstance(guardian_illnesses, str) and guardian_illnesses.lower() != 'none':
                        for illness_name in guardian_illnesses.split(','):
                            illness_name = illness_name.strip()
                            if illness_name:
                                illness, _ = ChronicIllness.objects.get_or_create(name=illness_name)
                                student.guardian_chronic_illnesses.add(illness)

                    # إضافة درجة في مادة معينة (Grade) إذا توفرت بيانات المادة والدرجة
                    if pd.notnull(row.get('Subject')) and pd.notnull(row.get('Score')):
                        subject_name = row.get('Subject')
                        subj, _ = Subject.objects.get_or_create(name=subject_name)
                        Grade.objects.create(
                            student=student,
                            subject=subj,
                            score=self.parse_decimal(row.get('Score')),
                            exam_type=row.get('Exam type'),
                            date_recorded=self.parse_date(row.get('Date recorded'))
                        )

                    # إنشاء سجل المعلومات الصحية (HealthInformation)
                    HealthInformation.objects.create(
                        student=student,
                        has_chronic_illness=self.str_to_bool(row.get('has chronic illness')),
                        left_eye_vision=row.get('Left eye vision'),
                        right_eye_vision=row.get('Right eye vision'),
                        dental_health=row.get('Dental Health'),
                        ear_health=row.get('Ear Health'),
                        general_health_status=row.get('General health status'),
                        last_medical_checkup=self.parse_date(row.get('Last medical checkup')),
                        weight=float(row.get('Weight')) if row.get('Weight') else None,
                        height=float(row.get('Height')) if row.get('Height') else None,
                        blood_type=row.get('Blood type'),
                        academic_stress=row.get('Academic stress'),
                        motivation=row.get('Motivation'),
                        depression=self.str_to_bool(row.get('Depression')),
                        sleep_disorder=row.get('Sleep disorder'),
                        anxiety=self.str_to_bool(row.get('Anxiety')),
                        psychological_trauma=self.str_to_bool(row.get('Psychological trauma')),
                        isolation_tendency=self.str_to_bool(row.get('Isolation tendency')),
                        aggressive_behavior=self.str_to_bool(row.get('Aggressive behavior')),
                        personal_family_issues=self.str_to_bool(row.get('Personal family issues')),
                        bullying=self.str_to_bool(row.get('Bullying')),
                        study_life_balance=row.get('Study life balance'),
                        psychological_support=self.str_to_bool(row.get('Psychological support')),
                        psychological_notes=row.get('Psychological notes'),
                        family_pressures=row.get('Family pressures'),
                        practices_masturbation=self.str_to_bool(row.get('Practices masturbation')),
                        abuse_at_home=self.str_to_bool(row.get('Abuse at home')),
                        abuse_at_school=self.str_to_bool(row.get('Abuse at school')),
                        sexual_harassment_at_home=self.str_to_bool(row.get('Sexual harassment at home')),
                        sexual_harassment_at_school=self.str_to_bool(row.get('Sexual harassment at school')),
                        alcohol_consumption=self.str_to_bool(row.get('Alcohol consumption')),
                        smoking=self.str_to_bool(row.get('Smoking')),
                        drug_use=self.str_to_bool(row.get('Drug use'))
                    )

                    # إنشاء سجل الحالة الاقتصادية (EconomicSituation)
                    EconomicSituation.objects.create(
                        student=student,
                        is_orphan=self.str_to_bool(row.get('is orphan')),
                        father_occupation=row.get('Father occupation'),
                        mother_occupation=row.get('Mother occupation'),
                        parents_marital_status=row.get('Parents marital status'),
                        family_income_level=(self.parse_decimal(row.get('Family income level'))
                                        if row.get('Family income level') else None),
                        income_source=row.get('Income source'),
                        monthly_expenses=(self.parse_decimal(row.get('Monthly expenses'))
                                            if row.get('Monthly expenses') else None),
                        housing_status=row.get('Housing status'),
                        access_to_electricity=self.str_to_bool(row.get('Access to electricity')),
                        has_access_to_water=self.str_to_bool(row.get('Has access to water')),
                        access_to_internet=self.str_to_bool(row.get('Access to internet')),
                        has_private_study_room=self.str_to_bool(row.get('Has private study room')),
                        number_of_rooms_in_home=int(row.get('Number of rooms in home')) if row.get('Number of rooms in home') else None,
                        daily_food_availability=self.str_to_bool(row.get('Daily food availability')),
                        has_school_uniform=self.str_to_bool(row.get('Has school uniform')),
                        has_stationery=self.str_to_bool(row.get('Has stationary')),
                        receives_financial_aid=self.str_to_bool(row.get('Receives financial aid')),
                        receives_meal_assistance=self.str_to_bool(row.get('Receives meal assistance')),
                        receives_scholarship=self.str_to_bool(row.get('Receives scholarship')),
                        receives_private_tutoring=self.str_to_bool(row.get('Receives private tutoring')),
                        daily_study_hours=float(row.get('Daily study hours')) if row.get('Daily study hours') else 0.0,
                        works_after_school=self.str_to_bool(row.get('Works after school')),
                        work_hours_per_week=float(row.get('Work hours per week')) if row.get('Work hours per week') else 0.0,
                        responsible_for_household_tasks=self.str_to_bool(row.get('Responsible for household tasks')),
                        transportation_mode=row.get('Transportation mode'),
                        distance_to_school=float(row.get('Distance to school')) if row.get('Distance to school') else None,
                        has_health_insurance=self.str_to_bool(row.get('Has health insurance')),
                        household_size=int(row.get('Household size')) if row.get('Household size') else 1,
                        sibling_rank=int(row.get('Sibling rank')) if row.get('Sibling rank') else None
                    )

                    # إنشاء سجل وسائل التواصل الاجتماعي والتكنولوجيا (SocialMediaAndTechnology)
                    SocialMediaAndTechnology.objects.create(
                        student=student,
                        has_phone=self.str_to_bool(row.get('Has phone')),
                        has_laptop=self.str_to_bool(row.get('Has laptop')),
                        has_tablet=self.str_to_bool(row.get('Has tablet')),
                        has_pc=self.str_to_bool(row.get('Has pc')),
                        device_usage_purpose=row.get('Device usage purpose'),
                        has_social_media_accounts=self.str_to_bool(row.get('Has social media accounts')),
                        daily_screen_time=float(row.get('Daily screen time')) if row.get('Daily screen time') else 0.0,
                        social_media_impact_on_studies=row.get('Social media impact on studies'),
                        content_type_watched=row.get('Content type watched'),
                        social_media_impact_on_sleep=row.get('Social media impact on sleep'),
                        social_media_impact_on_focus=row.get('Social media impact on focus'),
                        plays_video_games=self.str_to_bool(row.get('Plays video games')),
                        daily_gaming_hours=float(row.get('Daily gaming hours')) if row.get('Daily gaming hours') else 0.0,
                        aware_of_cybersecurity=self.str_to_bool(row.get('Aware of cybersecurity')),
                        experienced_electronic_extortion=self.str_to_bool(row.get('Experienced electronic extortion'))
                    )

                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Imported student: {student.full_name}"))

            except Exception as e:
                error_count += 1
                self.stderr.write(self.style.ERROR(f"Error processing row {index+1}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Data import completed: {success_count} successes, {error_count} errors out of {total_rows} rows"
        ))
