# Generated by Django 3.1.4 on 2024-03-19 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0012_auto_20240319_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentreactivation',
            name='is_permament',
            field=models.BooleanField(default=False),
        ),
    ]
