# Generated by Django 3.1.4 on 2024-05-15 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0002_auto_20230307_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='filter_args',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
    ]
