# Generated by Django 3.1.4 on 2023-03-25 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0003_auto_20230325_1418'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='translationlocale',
            unique_together={('country', 'language')},
        ),
    ]
