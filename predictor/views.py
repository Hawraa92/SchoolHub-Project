import os
import joblib

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Q
from django.core.paginator import Paginator

from students.models import Student

# Path to the serialized model
MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    'predictor', 'ml_models', 'student_performance_model.pkl'
)

def load_model():
    """
    Attempt to load the prediction model from disk.
    """
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"[MODEL LOAD ERROR] {e}")
        return None

@login_required
@user_passes_test(lambda u: u.is_staff or u.groups.filter(name='Teachers').exists())
def performance_dashboard(request):
    """
    Renders the student performance dashboard, with server-side search and pagination.
    """
    model = load_model()
    if model is None:
        return render(request, "predictor/error.html", {
            "message": "The prediction model could not be loaded."
        })

    # 1) Read search query and build base queryset
    q = request.GET.get('q', '').strip()
    qs = (
        Student.objects
        .select_related('economic_situation', 'health_information', 'tech_and_social')
        .annotate(avg_score=Avg('grades__score'))
    )
    if q:
        qs = qs.filter(full_name__icontains=q)

    # 2) Paginate the queryset: 20 students per page
    paginator   = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    # 3) Build feature matrix for current page only
    features = []
    for student in page_obj:
        econ   = getattr(student, 'economic_situation', None)
        health = getattr(student, 'health_information', None)
        tech   = getattr(student, 'tech_and_social', None)

        features.append([
            student.attendance_percentage or 0.0,
            student.avg_score           or 0.0,
            getattr(econ, 'daily_study_hours', 0.0),
            1 if econ and econ.has_private_study_room else 0,
            1 if econ and econ.has_stationery else 0,
            1 if econ and econ.receives_private_tutoring else 0,
            1 if econ and econ.works_after_school else 0,
            float(getattr(econ, 'family_income_level', 0.0)),
            # housing_status one-hot
            1 if econ and econ.housing_status == "Owned" else 0,
            1 if econ and econ.housing_status == "Rented" else 0,
            1 if econ and econ.housing_status == "Temporary Shelter" else 0,
            1 if econ and econ.housing_status == "None" else 0,
            # health fields
            1 if health and health.motivation == "High" else 0,
            1 if health and health.depression else 0,
            1 if health and health.academic_stress == "High" else 0,
            1 if health and health.study_life_balance == "Good" else 0,
            1 if health and health.family_pressures == "High" else 0,
            1 if health and health.sleep_disorder == "High" else 0,
            # tech fields
            getattr(tech, 'daily_screen_time', 0.0),
            1 if tech and tech.plays_video_games else 0,
            getattr(tech, 'daily_gaming_hours', 0.0),
            1 if tech and tech.social_media_impact_on_studies == "Negative" else 0,
            1 if tech and tech.content_type_watched == "Gaming" else 0,
            1 if tech and tech.content_type_watched == "Educational" else 0,
            1 if tech and tech.content_type_watched == "Entertainment" else 0,
            1 if tech and tech.content_type_watched == "News" else 0,
        ])

    # 4) Batch predict for the current page
    try:
        preds_encoded = model.predict(features)
    except Exception as e:
        print(f"[PREDICTION ERROR] Batch predict failed: {e}")
        preds_encoded = [None] * len(features)

    categories = ["Average", "Excellent", "Good", "Needs Improvement", "Very Good"]

    # 5) Assemble results
    results = []
    for student, code in zip(page_obj, preds_encoded):
        label = (
            categories[code]
            if code is not None and 0 <= code < len(categories)
            else "Error"
        )
        results.append({
            "student": student,
            "predicted_performance": label
        })

    # 6) Render template with context
    return render(request, "predictor/performance_dashboard.html", {
        "results":  results,
        "page_obj": page_obj,
        "total":    qs.count(),
        "query":    q,
    })
