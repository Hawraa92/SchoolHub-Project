import os
import django

# إعداد البيئة الصحيحة
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')

django.setup()

import csv
from students.models import ChronicIllness

# تحديد المسار الكامل لملف CSV
file_path = r'students/chronic_illness.csv'

# قراءة البيانات من ملف CSV
with open(file_path, mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        illness_name = row[0].strip()  # إزالة المسافات الزائدة
        if not ChronicIllness.objects.filter(name=illness_name).exists():
            ChronicIllness.objects.create(name=illness_name)
            print(f"تمت إضافة المرض المزمن: {illness_name}")
        else:
            print(f"المرض المزمن موجود مسبقًا: {illness_name}")
