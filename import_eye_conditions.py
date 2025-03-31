import os
import django

# إعداد البيئة الصحيحة
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')

django.setup()

import csv
from students.models import EyeCondition

# تحديد المسار الكامل لملف CSV
file_path = r'students/eye_conditions.csv'

# قراءة البيانات من ملف CSV
with open(file_path, mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        condition_name = row[0].strip()  # إزالة المسافات الزائدة
        if not EyeCondition.objects.filter(name=condition_name).exists():
            EyeCondition.objects.create(name=condition_name)
            print(f"تمت إضافة الحالة: {condition_name}")
        else:
            print(f"الحالة موجودة مسبقًا: {condition_name}")
