# Generated by Django 3.1.4 on 2023-04-03 16:01

from django.db import migrations


def update_father_name_from_middle_name(apps, schema_editor):
    Student = apps.get_model("school", "Student")
    students = Student.objects.all()
    for student in students:
        student.father_name = student.middle_name
        student.save()


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0009_auto_20230403_1742"),
    ]

    operations = [
        migrations.RunPython(
            code=update_father_name_from_middle_name,
        )
    ]
