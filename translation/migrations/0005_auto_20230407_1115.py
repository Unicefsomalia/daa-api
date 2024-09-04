# Generated by Django 3.1.4 on 2023-04-07 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0004_auto_20230325_1418'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=45, unique=True)),
                ('example', models.JSONField(blank=True, default=True)),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='translationlocale',
            name='country_code',
            field=models.CharField(default='we', max_length=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='translationlocale',
            name='language_code',
            field=models.CharField(default='we', max_length=3),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='translationlocale',
            unique_together={('country_code', 'language_code')},
        ),
        migrations.RemoveField(
            model_name='translationlocale',
            name='country',
        ),
        migrations.RemoveField(
            model_name='translationlocale',
            name='language',
        ),
    ]
