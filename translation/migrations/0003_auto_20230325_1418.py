# Generated by Django 3.1.4 on 2023-03-25 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0002_auto_20230325_1404'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='translationlocale',
            options={'ordering': ('-id',)},
        ),
        migrations.RenameField(
            model_name='translationlocale',
            old_name='county',
            new_name='country',
        ),
        migrations.AddField(
            model_name='translationlocale',
            name='version',
            field=models.CharField(default='1', editable=False, max_length=100),
            preserve_default=False,
        ),
    ]
