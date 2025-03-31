import csv
import random
from datetime import date, datetime
from faker import Faker
import numpy as np

def generate_data(num_records=5000, file_name="advanced_student_data_unique.csv"):
    fake = Faker('en_US')
    # Clear previous unique records (in case fake.unique was used before)
    fake.unique.clear()

    headers = [
        # PERSONAL INFORMATION (from Student)
        "user", "full_name", "date_of_birth", "gender", "nationality", "address",
        "profile_image", "email", "mobile", "emergency_contact_name", "emergency_contact",
        "enrollment_date",

        # GUARDIAN INFORMATION (new fields)
        "guardian_relationship", "guardian_address", "guardian_employment_status",
        "guardian_monthly_income", "guardian_education",

        # ACADEMIC INFORMATION (from Student)
        "grade_level", "subjects", "attendance_percentage", "awards", "seat_zone",

        # GRADES (for all subjects)
        "grades",

        # HEALTH INFORMATION (new fields)
        "has_chronic_illness", "general_health_status", "last_medical_checkup",
        "weight", "height", "academic_stress", "motivation", "depression",
        "sleep_disorder", "study_life_balance", "family_pressures",

        # ECONOMIC SITUATION
        "is_orphan", "father_occupation", "mother_occupation", "parents_marital_status",
        "family_income_level", "income_source", "monthly_expenses", "housing_status",
        "access_to_electricity", "has_access_to_water", "access_to_internet",
        "has_private_study_room", "number_of_rooms_in_home", "daily_food_availability",
        "has_school_uniform", "has_stationery", "receives_scholarship",
        "receives_private_tutoring", "daily_study_hours", "works_after_school",
        "work_hours_per_week", "responsible_for_household_tasks", "transportation_mode",
        "distance_to_school", "has_health_insurance", "household_size", "sibling_rank",

        # SOCIAL MEDIA AND TECHNOLOGY
        "has_electronic_device", "device_usage_purpose", "has_social_media_accounts",
        "daily_screen_time", "social_media_impact_on_studies", "content_type_watched",
        "social_media_impact_on_sleep", "social_media_impact_on_focus", "plays_video_games",
        "daily_gaming_hours", "aware_of_cybersecurity", "experienced_electronic_extortion"
    ]

    # List of subjects
    subjects_list = [
        "Mathematics", "Art", "Physics", "Chemistry",
        "History", "English Language", "Geography", "Biology"
    ]

    # Static lists for some fields
    general_health_status_list = ["good", "needs follow up"]
    stress_levels = ["Low", "Moderate", "High"]
    study_life_balance_levels = ["Needs Improvement", "Moderate", "Good"]
    family_pressures_levels = ["None", "Low", "Moderate", "High"]

    housing_status_choices = ["Owned", "Rented", "Shared", "Temporary Shelter", "None"]
    transportation_choices = ["Bus", "Car", "Bicycle", "Walking", "None"]
    income_source_choices = ["Salary", "Business", "Aid", "Other"]

    # Mapping for approximate student academic performance to select a grade range
    performance_map = {
        "Excellent": (80, 95),
        "Good": (65, 80),
        "Average": (50, 65),
        "Needs Improvement": (30, 50)
    }
    performance_levels = list(performance_map.keys())
    # Probability weights for selecting a performance level
    weights = [0.15, 0.35, 0.35, 0.15]

    data_rows = []

    def default_val(val, default="Not Specified"):
        if val is None or val == "None":
            return default
        return val

    def generate_subject_score(base, std=5):
        score = np.random.normal(loc=base, scale=std)
        return max(0, min(100, round(score, 2)))

    for _ in range(num_records):
        # PERSONAL INFORMATION
        # Using fake.unique ensures values are not repeated within the same generation session
        user = fake.unique.user_name()
        full_name = fake.name()
        dob = fake.date_of_birth(minimum_age=16, maximum_age=18).strftime("%Y-%m-%d")
        gender = random.choice(["Male", "Female"])
        nationality = fake.country()
        address = fake.address().replace("\n", ", ")
        profile_image = fake.image_url()
        email = fake.unique.email()
        mobile = fake.phone_number()
        emergency_contact_name = fake.name()
        emergency_contact = fake.phone_number()
        enrollment_date = fake.date_between(start_date='-3y', end_date='today').strftime("%Y-%m-%d")

        personal_info = [
            default_val(user), default_val(full_name), default_val(dob),
            default_val(gender), default_val(nationality), default_val(address),
            default_val(profile_image), default_val(email), default_val(mobile),
            default_val(emergency_contact_name), default_val(emergency_contact),
            default_val(enrollment_date)
        ]

        # GUARDIAN INFORMATION
        guardian_relationship = random.choice(["Father", "Mother", "Sibling", "Other"])
        guardian_address = fake.address().replace("\n", ", ")
        guardian_employment_status = random.choice(["Employed", "Unemployed", "Retired"])
        guardian_monthly_income = round(random.uniform(1000.0, 5000.0), 2)
        guardian_education = random.choice(["Primary", "Secondary", "Bachelor's", "Master's", "PhD"])
        guardian_info = [
            default_val(guardian_relationship), default_val(guardian_address),
            default_val(guardian_employment_status),
            guardian_monthly_income, default_val(guardian_education)
        ]

        # ACADEMIC INFORMATION
        grade_level = random.choice(["Grade 10", "Grade 11", "Grade 12"])
        subjects_str = ", ".join(subjects_list)
        attendance_percentage = round(random.uniform(75, 100), 2)
        awards = random.choice(["Honor Roll", "Excellence Award", "Outstanding Achievement", "None"])
        seat_zone = random.choice(["Front", "Middle", "Back", "Side"])
        academic_info = [
            default_val(grade_level), default_val(subjects_str),
            attendance_percentage, default_val(awards), default_val(seat_zone)
        ]

        # GRADES: generate a grade for each subject
        perf_level = random.choices(performance_levels, weights=weights, k=1)[0]
        base_min, base_max = performance_map[perf_level]
        base_score = random.uniform(base_min, base_max)
        grades = []
        for subj in subjects_list:
            score = generate_subject_score(base_score, std=5)
            grades.append(f"{subj}:{score}")
        grades_str = "; ".join(grades)

        # HEALTH INFORMATION
        has_chronic_illness = random.choice([True, False])
        general_health_status = random.choice(general_health_status_list)
        last_medical_checkup = fake.date_between(start_date='-2y', end_date='today').strftime("%Y-%m-%d")
        weight_val = round(random.uniform(50, 90), 1)
        height_val = round(random.uniform(155, 185), 1)
        academic_stress = random.choice(stress_levels)
        motivation = random.choice(stress_levels)
        depression = random.choice([True, False])
        sleep_disorder = random.choice(["None", "Low", "Moderate", "High"])
        study_life_balance = random.choice(study_life_balance_levels)
        family_pressures = random.choice(family_pressures_levels)
        health_info = [
            has_chronic_illness, default_val(general_health_status),
            default_val(last_medical_checkup), weight_val, height_val,
            default_val(academic_stress), default_val(motivation), depression,
            default_val(sleep_disorder), default_val(study_life_balance),
            default_val(family_pressures)
        ]

        # ECONOMIC SITUATION
        is_orphan = random.choice([True, False])
        father_occupation = fake.job()
        mother_occupation = fake.job()
        parents_marital_status = random.choice(["Married", "Divorced", "Separated", "Widowed", "Single"])
        family_income_level = round(random.uniform(500, 5000), 2)
        income_source = random.choice(income_source_choices)
        monthly_expenses = round(random.uniform(500, 3000), 2)
        housing_status = random.choice(housing_status_choices)
        access_to_electricity = True
        has_access_to_water = True
        access_to_internet = random.choice([True, False])
        has_private_study_room = random.choice([True, False])
        number_of_rooms_in_home = random.randint(2, 5)
        daily_food_availability = random.choice([True, False])
        has_school_uniform = random.choice([True, False])
        has_stationery = random.choice([True, False])
        receives_scholarship = random.choice([True, False])
        receives_private_tutoring = random.choice([True, False])
        daily_study_hours = round(random.uniform(2, 6), 1)
        works_after_school = random.choice([True, False])
        work_hours_per_week = random.randint(1, 10) if works_after_school else 0
        responsible_for_household_tasks = random.choice([True, False])
        transportation_mode = random.choice(transportation_choices)
        distance_to_school = round(random.uniform(0.5, 5), 1)
        has_health_insurance = random.choice([True, False])
        household_size = random.randint(3, 7)
        sibling_rank = random.randint(1, 3)
        economic_info = [
            is_orphan, default_val(father_occupation), default_val(mother_occupation),
            default_val(parents_marital_status), family_income_level, default_val(income_source),
            monthly_expenses, default_val(housing_status), access_to_electricity,
            has_access_to_water, access_to_internet, has_private_study_room,
            number_of_rooms_in_home, daily_food_availability, has_school_uniform,
            has_stationery, receives_scholarship, receives_private_tutoring,
            daily_study_hours, works_after_school, work_hours_per_week,
            responsible_for_household_tasks, default_val(transportation_mode),
            distance_to_school, has_health_insurance, household_size, sibling_rank
        ]

        # SOCIAL MEDIA AND TECHNOLOGY
        has_electronic_device = random.choice([True, False])
        device_usage_purpose = random.choice(["Education", "Entertainment", "Gaming", "Work", "Other"])
        has_social_media_accounts = random.choice([True, False])
        daily_screen_time = round(random.uniform(1, 4), 1)

        # If there is no electronic device or no internet access, set screen time to 0 and disable social media accounts
        if not has_electronic_device or not access_to_internet:
            daily_screen_time = 0
            device_usage_purpose = "None"
            has_social_media_accounts = False

        if has_social_media_accounts:
            social_media_impact_on_studies = random.choice(["Positive", "Negative", "Neutral", "None"])
            social_media_impact_on_sleep = random.choice(["Positive", "Negative", "Neutral", "None"])
            social_media_impact_on_focus = random.choice(["Positive", "Negative", "Neutral", "None"])
            content_type_watched = random.choice(["Educational", "Entertainment", "News", "Sports", "Gaming", "Other", "None"])
            experienced_electronic_extortion = random.choice([True, False])
        else:
            social_media_impact_on_studies = "None"
            social_media_impact_on_sleep = "None"
            social_media_impact_on_focus = "None"
            content_type_watched = "None"
            experienced_electronic_extortion = False

        plays_video_games = random.choice([True, False])
        daily_gaming_hours = round(random.uniform(0.5, 2), 1) if plays_video_games else 0
        aware_of_cybersecurity = random.choice([True, False])
        social_media_info = [
            has_electronic_device, default_val(device_usage_purpose),
            has_social_media_accounts, daily_screen_time,
            default_val(social_media_impact_on_studies),
            default_val(content_type_watched),
            default_val(social_media_impact_on_sleep),
            default_val(social_media_impact_on_focus),
            plays_video_games, daily_gaming_hours,
            aware_of_cybersecurity, experienced_electronic_extortion
        ]

        # Combine all sections into one row
        row = (
            personal_info + guardian_info + academic_info + [grades_str]
            + health_info + economic_info + social_media_info
        )
        data_rows.append(row)

    # Write all rows to a CSV file
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data_rows)

    print(f"Successfully generated {num_records} student records in '{file_name}'.")

if __name__ == "__main__":
    generate_data(num_records=5000, file_name="student_data.csv")
