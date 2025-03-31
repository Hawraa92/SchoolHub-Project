import os
import django
import csv
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')
django.setup()

from students.models import Vaccination

file_path = r'C:\Users\laptop\Desktop\school_management_system\students\vaccines.csv'

def convert_date_format(date_str):
    try:
        return datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
    except ValueError:
        print(f"the format of date in wrong   : {date_str}")
        return None

try:
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            vaccine_name = row[0].strip()
            raw_date = row[1].strip()
            status = row[2].strip()
            notes = row[3].strip()

            date_administered = convert_date_format(raw_date)

            if date_administered is None:
                print(f"تم تخطي السجل بسبب خطأ في التاريخ: {row}")
                continue

            if not Vaccination.objects.filter(name=vaccine_name, date_administered=date_administered).exists():
                Vaccination.objects.create(
                    name=vaccine_name,
                    date_administered=date_administered,
                    status=status,
                    notes=notes
                )
                print(f"تمت إضافة التطعيم: {vaccine_name}")
            else:
                print(f"التطعيم موجود مسبقاً: {vaccine_name}")
except FileNotFoundError:
    print(f"الملف {file_path} غير موجود. تأكد من المسار.")
except Exception as e:
    print(f"حدث خطأ: {e}")
