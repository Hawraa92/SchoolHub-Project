# Generated by Django 5.1.5 on 2025-05-03 09:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '0001_initial'),
        ('teachers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teacher_grades', to='teachers.teacher'),
        ),
        migrations.AddField(
            model_name='gradehistory',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='students.grade'),
        ),
        migrations.AddField(
            model_name='gradehistory',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='teachers.teacher'),
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='socialmediaandtechnology',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tech_and_social', to='students.student'),
        ),
        migrations.AddField(
            model_name='healthinformation',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='health_information', to='students.student'),
        ),
        migrations.AddField(
            model_name='grade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='students.student'),
        ),
        migrations.AddField(
            model_name='economicsituation',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='economic_situation', to='students.student'),
        ),
        migrations.AddField(
            model_name='studentperformancetrend',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_trends', to='students.student'),
        ),
        migrations.AddField(
            model_name='student',
            name='subjects',
            field=models.ManyToManyField(blank=True, related_name='students', to='students.subject'),
        ),
        migrations.AddField(
            model_name='grade',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='students.subject'),
        ),
    ]
