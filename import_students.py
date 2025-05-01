import os
import django
import pandas as pd

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')
django.setup()

# Import models
from students.models import Student
from accounts.models import User

# CSV file path
file_path = r"C:\Users\laptop\Desktop\cleaned_advanced_student_data.csv"

try:
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Convert 'date_of_birth' to the desired format (MM/DD/YYYY -> YYYY-MM-DD)
    # Cast the column to string to avoid errors if some values are floats.
    df['date_of_birth'] = pd.to_datetime(
        df['date_of_birth'].astype(str),
        format="%m/%d/%Y",
        errors='coerce'
    ).dt.strftime('%Y-%m-%d')

    # Upload data to the database
    for _, row in df.iterrows():
        # Search for the user by username (using the 'user' column from CSV)
        user_instance = User.objects.filter(username=row['user']).first()
        if not user_instance:
            # Create a new user if not found
            user_instance = User.objects.create_user(
                username=row['user'],
                email=f"{row['user']}@example.com",  # Temporary or placeholder email
                password='defaultpassword'
            )
            print(f"Created new user: {user_instance.username}")

        # Update or create the student record
        student, created = Student.objects.update_or_create(
            user=user_instance,
            defaults={
                "full_name": row['full_name'],
                "date_of_birth": row['date_of_birth'],
                "gender": row['gender'],
                "nationality": row['nationality'],
                "attendance_percentage": row['attendance_percentage'],
            }
        )
        print(f"✅ {'Added' if created else 'Updated'} student: {student.full_name}")

    print("🎉 Data import completed successfully!")

except FileNotFoundError:
    print(f"❌ File {file_path} not found! Please ensure it is located in the correct path within the 'students' folder.")
except Exception as e:
    print(f"⚠️ An error occurred during data import: {e}")
