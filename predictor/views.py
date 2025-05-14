import os
import joblib

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Q
from django.core.paginator import Paginator

from students.models import Student

# ——— Load model once —————————————————————————————
MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    'predictor', 'ml_models', 'student_performance_model.pkl'
)
MODEL = joblib.load(MODEL_PATH)

CATEGORIES = ["Average", "Excellent", "Good", "Needs Improvement", "Very Good"]

def prepare_features(student):
    econ   = getattr(student, 'economic_situation', None)
    health = getattr(student, 'health_information', None)
    tech   = getattr(student, 'tech_and_social', None)

    return [
        # Attendance & avg score
        student.attendance_percentage or 0.0,
        getattr(student, 'avg_score', 0.0),

        # Economic
        econ.daily_study_hours if econ else 0.0,
        1 if econ and econ.has_private_study_room else 0,
        1 if econ and econ.has_stationery else 0,
        1 if econ and econ.receives_private_tutoring else 0,
        1 if econ and econ.works_after_school else 0,
        float(econ.family_income_level or 0.0) if econ else 0.0,
        1 if econ and econ.housing_status == "Owned" else 0,
        1 if econ and econ.housing_status == "Rented" else 0,
        1 if econ and econ.housing_status == "Temporary Shelter" else 0,
        1 if econ and econ.housing_status == "None" else 0,

        # Health
        1 if health and health.motivation == "High" else 0,
        1 if health and health.depression else 0,
        1 if health and health.academic_stress == "High" else 0,
        1 if health and health.study_life_balance == "Good" else 0,
        1 if health and health.family_pressures == "High" else 0,
        1 if health and health.sleep_disorder == "High" else 0,

        # Tech & Social
        tech.daily_screen_time if tech else 0.0,
        1 if tech and tech.plays_video_games else 0,
        tech.daily_gaming_hours if tech else 0.0,
        1 if tech and tech.social_media_impact_on_studies == "Negative" else 0,
        1 if tech and tech.content_type_watched == "Gaming" else 0,
        1 if tech and tech.content_type_watched == "Educational" else 0,
        1 if tech and tech.content_type_watched == "Entertainment" else 0,
        1 if tech and tech.content_type_watched == "News" else 0,
    ]

@login_required
@user_passes_test(lambda u: u.is_staff or u.groups.filter(name='Teachers').exists())
def performance_dashboard(request):
    q = request.GET.get('q', '').strip()

    # 1) Build base queryset and annotate avg_score
    students = Student.objects.select_related(
        'economic_situation', 'health_information', 'tech_and_social'
    ).annotate(
        avg_score=Avg('grades__score')
    )

    # 2) Apply search filter if provided
    if q:
        students = students.filter(
    Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(full_name__icontains=q)
)

    # 3) Prepare features & predict for all matched students
    feature_list = [prepare_features(s) for s in students]
    student_map  = list(students)
    try:
        preds = MODEL.predict(feature_list)
    except Exception as e:
        print(f"[PREDICTION ERROR] {e}")
        preds = [None] * len(student_map)

    # 4) Build a lookup of student.id → category
    prediction_dict = {
        stu.id: CATEGORIES[code] if code is not None and 0 <= code < len(CATEGORIES) else "Error"
        for stu, code in zip(student_map, preds)
    }

    # 5) Paginate the full list
    paginator   = Paginator(student_map, 20)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    # 6) Build results for this page
    results = [
        {
            "student": student,
            "predicted_performance": prediction_dict.get(student.id, "Not Available")
        }
        for student in page_obj
    ]

    return render(request, "predictor/performance_dashboard.html", {
        "results": results,
        "page_obj": page_obj,
        "q": q,
    })
