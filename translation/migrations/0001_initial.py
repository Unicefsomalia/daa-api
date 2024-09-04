# Generated by Django 3.1.4 on 2023-03-25 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationLocal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=45, unique=True)),
                ('county', models.CharField(choices=[('SO', 'Somali'), ('KE', 'Kenya')], max_length=5)),
                ('language', models.CharField(choices=[('so', 'Somali'), ('swa', 'Swahili'), ('en', 'English')], max_length=5)),
                ('translations', models.JSONField(blank=True, null=True)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
    ]
