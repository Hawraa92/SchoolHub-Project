import os
import django
import pandas as pd

# إعداد البيئة لتحميل إعدادات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')
django.setup()

# استيراد النموذج الخاص بك
from students.models import Subject

# مسار ملف CSV
file_path = r'students/subjects.csv'

try:
    # قراءة ملف CSV باستخدام pandas
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # التكرار عبر صفوف ملف CSV
    for index, row in df.iterrows():
        subject_name = row['name'].strip()
        description = row['description'].strip()

        # التحقق مما إذا كانت المادة موجودة بالفعل
        if not Subject.objects.filter(name=subject_name).exists():
            # إنشاء سجل جديد
            Subject.objects.create(
                name=subject_name,
                description=description
            )
            print(f"تمت إضافة المادة: {subject_name}")
        else:
            print(f"المادة موجودة مسبقاً: {subject_name}")
except FileNotFoundError:
    print(f"الملف {file_path} غير موجود. تأكد من المسار.")
except Exception as e:
    print(f"حدث خطأ: {e}")
