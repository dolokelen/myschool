# Generated by Django 4.2.7 on 2023-11-14 06:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0041_student_is_transfer_student_student_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.CharField(max_length=7)),
                ('end_time', models.CharField(max_length=7)),
                ('week_days', models.CharField(max_length=6)),
            ],
            options={
                'unique_together': {('start_time', 'end_time', 'week_days')},
            },
        ),
        migrations.CreateModel(
            name='ClassRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('dimension', models.CharField(max_length=150)),
                ('create_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='classrooms', to='school.building')),
            ],
        ),
    ]
