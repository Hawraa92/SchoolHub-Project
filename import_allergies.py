import os
import django

# إعداد البيئة
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')
django.setup()

import csv
from students.models import Allergy

# مسار ملف CSV
file_path = 'students/allergies.csv'

# قراءة البيانات من ملف CSV وتحميلها إلى قاعدة البيانات
with open(file_path, mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        allergy_name = row[0].strip()  # إزالة المسافات الزائدة
        if not Allergy.objects.filter(name=allergy_name).exists():
            Allergy.objects.create(name=allergy_name)
            print(f"تمت إضافة الحساسية: {allergy_name}")
        else:
            print(f"الحساسية موجودة مسبقًا: {allergy_name}")
