# Generated by Django 4.2.7 on 2023-11-14 07:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0042_classtime_classroom'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classroom',
            old_name='create_at',
            new_name='created_at',
        ),
    ]
