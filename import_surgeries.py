import os
import django

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')
django.setup()

import csv
from students.models import Surgery  # Import the correct model

# CSV file path
file_path = 'students/surgeries.csv'

# Read data from the CSV file and load it into the database
with open(file_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    
    for row in reader:
        surgery_name = row[0].strip()  # Remove extra whitespace
        
        # Ensure that the surgery is not duplicated
        if not Surgery.objects.filter(name=surgery_name).exists():
            Surgery.objects.create(name=surgery_name)  # No date is set
            print(f"Surgery added: {surgery_name}")
        else:
            print(f"Surgery already exists: {surgery_name}")
