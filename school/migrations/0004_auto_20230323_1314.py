# Generated by Django 3.1.4 on 2023-03-23 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0003_auto_20230307_1333'),
    ]

    operations = [
        migrations.RenameField(
            model_name='school',
            old_name='dummy',
            new_name='is_training_school',
        ),
    ]
