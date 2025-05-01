import os
import django
import pandas as pd
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')
django.setup()

# Import the necessary models
from teachers.models import Teacher
from accounts.models import User  # Adjust this based on your custom user model
from students.models import Subject  # For subjects (if needed)

# Path to your teacher CSV file
file_path = r'C:\Users\Hawraa\Desktop\school_management_system\students\teachers.csv'

try:
    # Read CSV file using pandas
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # Iterate over rows in the CSV file
    for index, row in df.iterrows():
        username = row['user'].strip()  # e.g. "raffael"
        full_name = row['full_name'].strip()
        dob_str = row['date_of_birth'].strip()  # Expecting "DD/MM/YYYY"
        gender = row['gender'].strip()
        email = row['email'].strip()
        mobile = row['mobile'].strip()
        address = row['address'].strip()
        
        # Convert date from DD/MM/YYYY to a date object
        try:
            dob = datetime.strptime(dob_str, '%d/%m/%Y').date()
        except ValueError:
            print(f"Invalid date format for {full_name}: {dob_str}. Skipping this record.")
            continue
        
        # Get or create the User instance based on username
        try:
            user_instance = User.objects.get(username=username)
        except User.DoesNotExist:
            # Create a new User if not found.
            user_instance = User.objects.create(username=username, email=email)
            user_instance.set_password("defaultpassword")  # Set a default password; update as needed
            user_instance.save()
            print(f"Created new User for: {username}")
        
        # Process subjects_responsible_for: a comma-separated string
        subjects_field = row['subjects_responsible_for']
        if isinstance(subjects_field, str):
            subjects_list = [subject.strip() for subject in subjects_field.split(',')]
        else:
            subjects_list = []
        
        # Check if a teacher with this user already exists
        if not Teacher.objects.filter(user=user_instance).exists():
            # Create the teacher record
            teacher = Teacher.objects.create(
                user=user_instance,
                full_name=full_name,
                date_of_birth=dob,  # Use the converted date
                gender=gender,
                email=email,
                mobile=mobile,
                address=address,
            )
            # Assign subjects if applicable
            for subject_name in subjects_list:
                try:
                    subject_obj = Subject.objects.get(name__iexact=subject_name)
                    teacher.subjects_responsible_for.add(subject_obj)
                except Subject.DoesNotExist:
                    print(f"Subject '{subject_name}' does not exist for teacher {full_name}.")
            print(f"Added teacher: {full_name}")
        else:
            print(f"Teacher with username {username} already exists.")
            
except FileNotFoundError:
    print(f"File not found: {file_path}. Please verify the path.")
except Exception as e:
    print(f"An error occurred: {e}")
