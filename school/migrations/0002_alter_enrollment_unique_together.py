# Generated by Django 4.2.7 on 2023-11-30 17:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('student', 'course', 'section', 'semester')},
        ),
    ]
