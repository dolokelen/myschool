# Generated by Django 4.2.6 on 2023-10-28 03:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0006_semester_latest_semester'),
    ]

    operations = [
        migrations.RenameField(
            model_name='semester',
            old_name='latest_semester',
            new_name='current_semester',
        ),
    ]