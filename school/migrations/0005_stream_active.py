# Generated by Django 3.1.4 on 2023-03-24 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0004_auto_20230323_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='stream',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
