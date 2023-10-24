# Generated by Django 4.2.6 on 2023-10-24 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0003_course_semester'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('budget', models.DecimalField(decimal_places=2, max_digits=8)),
                ('duty', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
