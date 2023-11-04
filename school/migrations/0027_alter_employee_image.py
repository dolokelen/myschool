# Generated by Django 4.2.7 on 2023-11-04 01:28

from django.db import migrations, models
import school.validators


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0026_rename_person_employee_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='image',
            field=models.ImageField(upload_to='school/images', validators=[school.validators.validate_file_size]),
        ),
    ]
