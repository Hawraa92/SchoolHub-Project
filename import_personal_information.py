import os
import django
import pandas as pd
from datetime import datetime

# إعداد Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SchoolHub.settings")
django.setup()

# استيراد النماذج
from students.models import Student
from accounts.models import User

# تحديد مسار ملف CSV
file_path = r"C:\Users\Hworaa\Desktop\school_management_system\students\personal_information.csv"

# التحقق من وجود الملف
if not os.path.exists(file_path):
    print(f"❌ الملف غير موجود: {file_path}")
    exit()

# قراءة ملف CSV باستخدام Pandas
df = pd.read_csv(file_path, dtype=str)

# تحويل القيم الفارغة إلى None
df = df.where(pd.notna(df), None)

# معالجة البيانات وإضافتها إلى قاعدة البيانات
for _, row in df.iterrows():
    try:
        # تخطي الصف إذا لم يكن هناك مستخدم مسؤول
        if not row["user"]:
            print(f"⚠️ تخطيت صفًا بدون مستخدم مسؤول.")
            continue  

        # البحث عن المستخدم المسؤول عن إدخال البيانات
        user = User.objects.get(username=row["user"])

        # تحويل التواريخ إلى تنسيق `YYYY-MM-DD`
        date_of_birth = datetime.strptime(row["date_of_birth"], "%d/%m/%Y").strftime("%Y-%m-%d")
        enrollment_date = datetime.strptime(row["enrollment_date"], "%d/%m/%Y").strftime("%Y-%m-%d")

        # إدخال الطالب إلى قاعدة البيانات
        student, created = Student.objects.get_or_create(
            email=row["email"],
            defaults={
                "user": user,
                "full_name": row["full_name"],
                "date_of_birth": date_of_birth,
                "enrollment_date": enrollment_date,
                "gender": row["gender"],
                "nationality": row["nationality"],
                "marital_status": row["marital_status"],
                "address": row["address"],
                "profile_image": row["profile_image"] if row["profile_image"] else "",
                "mobile": row["mobile"],
                "spoken_language": row["spoken_language"],
                "emergency_contact_name": row["emergency_contact_name"],
                "emergency_contact": row["emergency_contact"],
            }
        )

        if created:
            print(f"✅ تمت إضافة الطالب: {row['full_name']}")
        else:
            print(f"⚠️ الطالب موجود مسبقًا: {row['full_name']}")

    except User.DoesNotExist:
        print(f"❌ خطأ: المستخدم '{row['user']}' غير موجود في النظام.")
    except ValueError as ve:
        print(f"❌ خطأ في تنسيق التاريخ للطالب {row['full_name']}: {ve}")
    except Exception as e:
        print(f"❌ خطأ أثناء إدخال {row['full_name']}: {e}")

print("🎯 تم استيراد جميع البيانات بنجاح!")
print(f"📊 إجمالي عدد الطلاب في قاعدة البيانات: {Student.objects.count()}")
