# Generated by Django 3.1.4 on 2024-03-19 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0011_auto_20230407_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='employed_by',
            field=models.CharField(blank=True, max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='status',
            field=models.CharField(choices=[('AE', 'Already Enrolled'), ('NE', 'Newly Enrolled'), ('PE', 'Re-Enrolled')], default='NE', max_length=5),
        ),
    ]
