import os
import django
import pandas as pd

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')
django.setup()

# استيراد النموذج الخاص بك
from students.models import Disability

# مسار ملف CSV
file_path = r'students/disabilities_list.csv'

try:
    # قراءة ملف CSV بدون عناوين، مع تحديد اسم للعمود الوحيد
    df = pd.read_csv(file_path, encoding='utf-8', header=None, names=["Disability"])

    # إزالة الصفوف الفارغة تمامًا
    df = df.dropna(subset=["Disability"])

    disabilities_to_create = []
    
    # التكرار عبر صفوف ملف CSV
    for index, row in df.iterrows():
        try:
            disability_name = str(row['Disability']).strip()

            # التأكد من أن الاسم ليس فارغًا بعد التنظيف
            if disability_name and not Disability.objects.filter(name=disability_name).exists():
                disabilities_to_create.append(Disability(name=disability_name, description=""))
            else:
                print(f"⚠️ الإعاقة موجودة مسبقاً: {disability_name if disability_name else '(غير معروفة)'}")
        except Exception as row_error:
            print(f"❌ خطأ في السطر {index + 1}: {row_error}")

    # إدخال جميع الإعاقات الجديدة دفعة واحدة لتحسين الأداء
    if disabilities_to_create:
        Disability.objects.bulk_create(disabilities_to_create)
        print(f"✅ تمت إضافة {len(disabilities_to_create)} إعاقات جديدة بنجاح!")
    else:
        print("ℹ️ لم يتم إضافة أي إعاقات جديدة.")
        
except FileNotFoundError:
    print(f"❌ الملف {file_path} غير موجود. تأكد من المسار.")
except Exception as e:
    print(f"❌ حدث خطأ غير متوقع: {e}")
