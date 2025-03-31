import csv
import uuid
import random
from datetime import datetime
from django.core.management.base import BaseCommand
from faker import Faker
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

class Command(BaseCommand):
    help = "Generate highly accurate student data CSV with advanced predictive analysis, excluding fields computed automatically (student_id, age, academic performance)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--num',
            type=int,
            default=5000,
            help='Number of student records to generate'
        )

    def handle(self, *args, **options):
        fake = Faker('ar_EG')
        num_records = options['num']
        file_name = "advanced_student_data.csv"

        # قائمة درجات الرؤية؛ لضمان عرضها كنص في Excel
        EYE_VISION = ["6/6", "6/9", "6/12", "6/18", "6/24", "6/36", "6/60", "<6/60"]

        # تعريف رؤوس الأعمدة النهائية بعد إزالة الحقول المحسوبة تلقائيًا:
        # نستبعد "Student id", "Age" و"Academic performance"
        headers = [
            # PERSONAL INFORMATION (14 حقل بدون student_id و age)
            "User", "Full name", "Date of birth", "Gender", "Nationality", "Marital status",
            "Address", "Profile image", "Email", "Mobile", "Spoken language",
            "Emergency contact name", "Emergency Contact", "Enrollment date",
            # GUARDIAN INFORMATION (9 حقل)
            "Guardian name", "Guardian relationship", "Guardian contact", "Guardian address", "Guardian job title",
            "Guardian chronic illnesses", "Guardian employment status", "Guardian monthly income", "Guardian education",
            # ACADEMIC INFORMATION (5 حقل بدون academic performance)
            "Grade level", "Subjects", "Attendance percentage", "Awards", "Seat zone",
            # GRADES (4 حقل)
            "Subject", "Score", "Exam type", "Date recorded",
            # HEALTH INFORMATION (38 حقل)
            "Surgical history", "Has chronic illness", "Chronic illnesses type", "Allergies", "Vaccinations",
            "Eye conditions", "Left Eye Vision", "Right Eye Vision", "Dental Health", "Ear Health", "General health status",
            "Last medical checkup", "Weight", "Height", "Blood type", "Disabilities", "Academic stress", "Motivation",
            "Depression", "Sleep disorder", "Anxiety", "Psychological trauma", "Isolation tendency", "Aggressive behavior",
            "Personal family issues", "Bullying", "Study life balance", "Psychological support", "Psychological notes",
            "Family pressures", "Practices masturbation", "Abuse at home", "Abuse at school",
            "Sexual harassment at home", "Sexual harassment at school", "Alcohol consumption", "Smoking", "Drug use",
            # ECONOMIC SITUATION (29 حقل)
            "Is orphan", "Father occupation", "Mother occupation", "Parents marital status", "Family income level",
            "Income source", "Monthly expenses", "Housing status", "Access to electricity", "Has access to water",
            "Access to internet", "Has private study room", "Number of rooms in home", "Daily food availability",
            "Has school uniform", "Has stationary", "Receives financial aid", "Receives meal assistance",
            "Receives scholarship", "Receives private tutoring", "Daily study hours", "Works after school",
            "Work hours per week", "Responsible for household tasks", "Transportation mode", "Distance to school",
            "Has health insurance", "Household size", "Sibling rank",
            # SOCIAL MEDIA AND TECHNOLOGY (15 حقل)
            "Has phone", "Has laptop", "Has tablet", "Has pc", "Device usage purpose", "Has social media accounts",
            "Daily screen time", "Social media impact on studies", "Content type watched", "Social media impact on sleep",
            "Social media impact on focus", "Plays video games", "Daily gaming hours", "Aware of cybersecurity",
            "Experienced electronic extortion"
        ]

        data_rows = []
        # الميزات المتقدمة لتعلم الآلة:
        # [sleep_hours, daily_study_hours, daily_gaming_hours, content_value, motivation_value, guardian_monthly_income, stability_value, attendance_percentage]
        ml_features = []
        ml_targets = []

        for _ in range(num_records):
            # ----------------------------
            # PERSONAL INFORMATION (نتجاهل student_id وcomputed age)
            # ----------------------------
            user = fake.user_name()
            full_name = fake.name()
            # student_id يُحسب داخلياً ولا يُدرج
            dob = fake.date_of_birth(minimum_age=16, maximum_age=18)
            # computed_age يُحسب داخل النظام، لذا لا ندرجه
            gender = random.choice(["Male", "Female"])
            nationality = fake.country()
            marital_status = "Single"
            address = fake.address().replace("\n", ", ")
            profile_image = fake.image_url()
            email = fake.email()
            mobile = fake.phone_number()
            spoken_language = "Arabic"
            emergency_contact_name = fake.name()
            emergency_contact = fake.phone_number()
            enrollment_date = fake.date_between(start_date='-3y', end_date='today')
            personal_info = [
                user, full_name, dob, gender, nationality, marital_status,
                address, profile_image, email, mobile, spoken_language,
                emergency_contact_name, emergency_contact, enrollment_date
            ]

            # ----------------------------
            # GUARDIAN INFORMATION
            # ----------------------------
            guardian_name = fake.name()
            guardian_relationship = random.choices(["Father", "Mother", "Sibling", "Other"], weights=[40, 40, 10, 10], k=1)[0]
            guardian_contact = fake.phone_number()
            guardian_address = fake.address().replace("\n", ", ")
            guardian_job_title = fake.job()
            guardian_chronic_illnesses = random.choice(["None", "Diabetes", "Hypertension", "Asthma", "Heart Disease"])
            guardian_employment_status = random.choice(["Employed", "Unemployed", "Retired"])
            guardian_monthly_income = round(random.uniform(1000.0, 5000.0), 2)
            guardian_education = random.choice(["Primary", "Secondary", "Bachelor's", "Master's", "PhD"])
            guardian_info = [
                guardian_name, guardian_relationship, guardian_contact, guardian_address, guardian_job_title,
                guardian_chronic_illnesses, guardian_employment_status, guardian_monthly_income, guardian_education
            ]

            # ----------------------------
            # ACADEMIC INFORMATION (نتجاهل academic performance)
            # ----------------------------
            grade_level = random.choice(["Grade 10", "Grade 11", "Grade 12"])
            subjects_list = [
                "Mathematics", "Biology", "Family Education", "Religious Education",
                "History", "Geography", "Art", "Music", "Theater", "English Language",
                "Arabic Language", "German Language", "French Language", "Spanish Language",
                "Civic Education", "Economics", "Literature", "Philosophy",
                "Chemistry", "Physics", "Physical Education"
            ]
            subjects = ", ".join(random.sample(subjects_list, k=random.randint(2, 4)))
            attendance_percentage = round(random.uniform(75, 100), 2)
            awards = random.choice(["Honor Roll", "Excellence Award", "Outstanding Achievement", "None"])
            seat_zone = random.choice(["Front", "Middle", "Back", "Side"])
            academic_info = [grade_level, subjects, attendance_percentage, awards, seat_zone]

            # ----------------------------
            # GRADES (4 حقل)
            # ----------------------------
            grade_subject = random.choice(subjects_list)
            score_placeholder = 0  # ستُحدث لاحقاً بواسطة نموذج ML
            exam_type = random.choice(["Midterm", "Final", "Quiz", "Assignment"])
            date_recorded = fake.date_between(start_date='-1y', end_date='today')
            grades_info = [grade_subject, score_placeholder, exam_type, date_recorded]

            # ----------------------------
            # HEALTH INFORMATION (38 حقل)
            # ----------------------------
            surgical_history = random.choice(["None", "Appendectomy", "Gallbladder removal", "Other surgery"])
            has_chronic_illness = random.choice(["No", "Yes"])
            chronic_illnesses_type = "None" if has_chronic_illness == "No" else random.choice(["Diabetes", "Hypertension", "Asthma", "Heart Disease"])
            allergies = random.choice(["None", "Peanuts", "Shellfish", "Pollen", "Dust", "Other"])
            vaccinations = random.choice(["Up-to-date", "Missing some", "None"])
            eye_conditions = random.choice(["None", "Myopia", "Hyperopia", "Astigmatism", "Cataract", "Other"])
            left_eye_vision = f'="{random.choice(EYE_VISION)}"'
            right_eye_vision = f'="{random.choice(EYE_VISION)}"'
            dental_health = random.choice(["Good", "Fair", "Poor"])
            ear_health = random.choice(["Good", "Fair", "Poor"])
            general_health_status = random.choice(["Excellent", "Good", "Fair", "Poor"])
            last_medical_checkup = fake.date_between(start_date='-2y', end_date='today')
            weight = round(random.uniform(50, 90), 1)
            height = round(random.uniform(155, 185), 1)
            blood_type = random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            disabilities = random.choice(["None", "Visual impairment", "Hearing impairment", "Mobility impairment"])
            academic_stress = random.choice(["Low", "Medium", "High"])
            motivation = random.choice(["Low", "Medium", "High"])
            depression = random.choice(["None", "Mild", "Moderate", "Severe"])
            sleep_disorder = random.choice(["None", "Insomnia", "Sleep apnea"])
            anxiety = random.choice(["None", "Mild", "Moderate", "Severe"])
            psychological_trauma = random.choice(["None", "Past trauma"])
            isolation_tendency = random.choice(["Low", "Medium", "High"])
            aggressive_behavior = random.choice(["None", "Low", "Medium", "High"])
            personal_family_issues = random.choice(["None", "Some issues"])
            bullying = random.choice(["None", "Experienced bullying"])
            study_life_balance = random.choice(["Good", "Average", "Poor"])
            psychological_support = random.choice(["None", "Counseling", "Family support"])
            psychological_notes = fake.sentence(nb_words=6)
            family_pressures = random.choice(["None", "Yes"])
            practices_masturbation = random.choice(["Yes", "No"])
            abuse_at_home = random.choice(["None", "Yes"])
            abuse_at_school = random.choice(["None", "Yes"])
            sexual_harassment_at_home = random.choice(["None", "Yes"])
            sexual_harassment_at_school = random.choice(["None", "Yes"])
            alcohol_consumption = random.choice(["None", "Yes"])
            smoking = random.choice(["None", "Yes"])
            drug_use = random.choice(["None", "Yes"])
            health_info = [
                surgical_history, has_chronic_illness, chronic_illnesses_type, allergies, vaccinations,
                eye_conditions, left_eye_vision, right_eye_vision, dental_health, ear_health, general_health_status,
                last_medical_checkup, weight, height, blood_type, disabilities, academic_stress, motivation,
                depression, sleep_disorder, anxiety, psychological_trauma, isolation_tendency, aggressive_behavior,
                personal_family_issues, bullying, study_life_balance, psychological_support, psychological_notes,
                family_pressures, practices_masturbation, abuse_at_home, abuse_at_school,
                sexual_harassment_at_home, sexual_harassment_at_school, alcohol_consumption, smoking, drug_use
            ]

            # ----------------------------
            # ECONOMIC SITUATION (29 حقل)
            # ----------------------------
            is_orphan = random.choice(["No", "Yes"])
            father_occupation = fake.job()
            mother_occupation = fake.job()
            parents_marital_status = random.choice(["Married", "Divorced", "Widowed"])
            family_income_level = random.choice(["Low", "Middle", "High"])
            income_source = random.choice(["Salary", "Business", "Investments", "Other"])
            monthly_expenses = round(random.uniform(500, 3000), 2)
            housing_status = random.choice(["Owned", "Rented", "Government assistance"])
            access_to_electricity = "Yes"
            has_access_to_water = "Yes"
            access_to_internet = random.choice(["Yes", "No"])
            has_private_study_room = random.choice(["Yes", "No"])
            number_of_rooms_in_home = random.randint(2, 5)
            daily_food_availability = random.choice(["Adequate", "Insufficient"])
            has_school_uniform = "Yes"
            has_stationary = "Yes"
            receives_financial_aid = random.choice(["No", "Yes"])
            receives_meal_assistance = random.choice(["No", "Yes"])
            receives_scholarship = random.choice(["No", "Yes"])
            receives_private_tutoring = random.choice(["Yes", "No"])
            daily_study_hours = round(random.uniform(2, 6), 1)
            works_after_school = random.choice(["No", "Yes"])
            work_hours_per_week = random.randint(1, 10) if works_after_school == "Yes" else 0
            responsible_for_household_tasks = random.choice(["Yes", "No"])
            transportation_mode = random.choice(["Bus", "Car", "Bicycle", "Walking"])
            distance_to_school = round(random.uniform(0.5, 5), 1)
            has_health_insurance = random.choice(["Yes", "No"])
            household_size = random.randint(3, 7)
            sibling_rank = random.randint(1, 3)
            economic_info = [
                is_orphan, father_occupation, mother_occupation, parents_marital_status, family_income_level,
                income_source, monthly_expenses, housing_status, access_to_electricity, has_access_to_water,
                access_to_internet, has_private_study_room, number_of_rooms_in_home, daily_food_availability,
                has_school_uniform, has_stationary, receives_financial_aid, receives_meal_assistance,
                receives_scholarship, receives_private_tutoring, daily_study_hours, works_after_school,
                work_hours_per_week, responsible_for_household_tasks, transportation_mode, distance_to_school,
                has_health_insurance, household_size, sibling_rank
            ]

            # ----------------------------
            # SOCIAL MEDIA AND TECHNOLOGY (15 حقل)
            # ----------------------------
            has_phone = random.choice(["Yes", "No"])
            has_laptop = random.choice(["Yes", "No"])
            has_tablet = random.choice(["Yes", "No"])
            has_pc = random.choice(["Yes", "No"])
            device_usage_purpose = random.choice(["Education", "Entertainment", "Both"])
            has_social_media_accounts = random.choice(["Yes", "No"])
            daily_screen_time = round(random.uniform(1, 4), 1)
            if has_phone == "No" and has_laptop == "No" and has_tablet == "No" and has_pc == "No":
                daily_screen_time = 0
                device_usage_purpose = "None"
            if access_to_internet == "No":
                has_social_media_accounts = "No"
                daily_screen_time = 0
                device_usage_purpose = "None"
            if has_social_media_accounts == "Yes":
                social_media_impact_on_studies = random.choice(["Positive", "Negative", "None"])
                social_media_impact_on_sleep = random.choice(["Positive", "Negative", "None"])
                social_media_impact_on_focus = random.choice(["Positive", "Negative", "None"])
                content_type_watched = random.choice(["Educational", "Entertainment", "News", "Mixed"])
                experienced_electronic_extortion = random.choice(["No", "Yes"])
            else:
                social_media_impact_on_studies = "None"
                social_media_impact_on_sleep = "None"
                social_media_impact_on_focus = "None"
                content_type_watched = "None"
                experienced_electronic_extortion = "No"
            plays_video_games = random.choice(["Yes", "No"])
            daily_gaming_hours = round(random.uniform(0.5, 2), 1) if plays_video_games == "Yes" else 0
            aware_of_cybersecurity = random.choice(["Yes", "No"])
            social_media_info = [
                has_phone, has_laptop, has_tablet, has_pc, device_usage_purpose, has_social_media_accounts,
                daily_screen_time, social_media_impact_on_studies, content_type_watched, social_media_impact_on_sleep,
                social_media_impact_on_focus, plays_video_games, daily_gaming_hours, aware_of_cybersecurity,
                experienced_electronic_extortion
            ]

            # ----------------------------
            # العوامل المتقدمة لتعلم الآلة
            # (العوامل: ساعات النوم، ساعات الدراسة، ساعات الألعاب، قيمة المحتوى، قيمة الدافع، دخل الوصي، قيمة الاستقرار، نسبة الحضور)
            # ----------------------------
            sleep_hours = round(random.uniform(5, 9), 1)
            # تحويل "motivation" إلى قيمة رقمية: Low=1, Medium=2, High=3
            motivation_value = {"Low": 1, "Medium": 2, "High": 3}.get(motivation, 2)
            # تحويل "content_type_watched" إلى قيمة رقمية
            content_value = {"Educational": 1, "Entertainment": 0, "News": 0.5, "Mixed": 0.75, "None": 0}.get(content_type_watched, 0)
            # تحويل "family_income_level" إلى قيمة رقمية تعبر عن الاستقرار: Low=1, Middle=2, High=3
            stability_value = {"Low": 1, "Middle": 2, "High": 3}.get(family_income_level, 2)

            advanced_feature = [
                sleep_hours,
                daily_study_hours,
                daily_gaming_hours,
                content_value,
                motivation_value,
                guardian_monthly_income,
                stability_value,
                attendance_percentage
            ]

            noise = np.random.normal(0, 2)
            true_score = (50 +
                          2 * (sleep_hours - 7) +
                          5 * (daily_study_hours - 4) -
                          3 * (daily_gaming_hours) +
                          4 * content_value +
                          2 * (motivation_value - 2) +
                          0.005 * (guardian_monthly_income - 3000) +
                          3 * (stability_value - 2) +
                          0.5 * (attendance_percentage - 75) +
                          noise)

            ml_features.append(advanced_feature)
            ml_targets.append(true_score)

            # ----------------------------
            # بناء الصف النهائي بترتيب الحقول
            # ----------------------------
            row = personal_info + guardian_info + academic_info + grades_info + health_info + economic_info + social_media_info
            data_rows.append(row)

        # تحويل الميزات والأهداف إلى مصفوفات وتوحيدها
        X = np.array(ml_features)
        y = np.array(ml_targets)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # تدريب نموذج Ridge Regression لتوليد درجات دقيقة
        model = Ridge(alpha=1.0)
        model.fit(X_scaled, y)
        predicted_scores = model.predict(X_scaled)

        # تحديث حقل "Score" في كل صف
        # حسب ترتيب الصف: personal_info (14) + guardian_info (9) + academic_info (5) = 28،
        # ثم grades_info: "Subject", "Score", "Exam type", "Date recorded" => Score هو العنصر الثاني (فهرسه = 1)
        # إذن موقع Score في الصف النهائي = 28 + 1 = 29
        for i, row in enumerate(data_rows):
            row[29] = round(predicted_scores[i], 2)

        # كتابة ملف CSV النهائي
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(data_rows)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully generated {num_records} student records with advanced ML predictions in '{file_name}'"
        ))
