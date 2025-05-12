import os
import joblib
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from students.models import Student

MODEL_PATH = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'student_performance_model.pkl')

def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"[MODEL LOAD ERROR] {e}")
        return None

@login_required
@user_passes_test(lambda u: u.is_staff or u.groups.filter(name='Teachers').exists())
def performance_dashboard(request):
    model = load_model()
    if model is None:
        return render(request, "predictor/error.html", {
            "message": "The prediction model could not be loaded. Please check if the file exists on the server."
        })

    students = Student.objects.all()
    results = []

    for student in students:
        economic = getattr(student, 'economic_situation', None)
        health = getattr(student, 'health_information', None)
        tech = getattr(student, 'tech_and_social', None)

        features = [
            student.attendance_percentage or 0.0,
            student.get_average_score() or 0.0,
            economic.daily_study_hours if economic else 0.0,
            1 if economic and economic.has_private_study_room else 0,
            1 if economic and economic.has_stationery else 0,
            1 if economic and economic.receives_private_tutoring else 0,
            1 if economic and economic.works_after_school else 0,
            float(economic.family_income_level) if economic and economic.family_income_level else 0.0,
            1 if economic and economic.housing_status == "Owned" else 0,
            1 if economic and economic.housing_status == "Rented" else 0,
            1 if economic and economic.housing_status == "Temporary Shelter" else 0,
            1 if economic and economic.housing_status == "None" else 0,
            1 if health and health.motivation == "High" else 0,
            1 if health and health.depression else 0,
            1 if health and health.academic_stress == "High" else 0,
            1 if health and health.study_life_balance == "Good" else 0,
            1 if health and health.family_pressures == "High" else 0,
            1 if health and health.sleep_disorder == "High" else 0,
            tech.daily_screen_time if tech else 0.0,
            1 if tech and tech.plays_video_games else 0,
            tech.daily_gaming_hours if tech else 0.0,
            1 if tech and tech.social_media_impact_on_studies == "Negative" else 0,
            1 if tech and tech.content_type_watched == "Gaming" else 0,
            1 if tech and tech.content_type_watched == "Educational" else 0,
            1 if tech and tech.content_type_watched == "Entertainment" else 0,
            1 if tech and tech.content_type_watched == "News" else 0
        ]

        try:
            pred_label_encoded = model.predict([features])[0]
            categories = ["Average", "Excellent", "Good", "Needs Improvement", "Very Good"]
            pred_label = categories[pred_label_encoded]
        except Exception as e:
            print(f"[PREDICTION ERROR] Student ID {student.id}: {e}")
            pred_label = "Error"

        results.append({
            "student": student,
            "predicted_performance": pred_label
        })

    return render(request, "predictor/performance_dashboard.html", {"results": results})
