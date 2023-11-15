# Generated by Django 4.2.7 on 2023-11-14 14:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0043_rename_create_at_classroom_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2)),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sections', to='school.classroom')),
                ('classtime', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sections', to='school.classtime')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sections', to='school.course')),
            ],
            options={
                'unique_together': {('classroom', 'classtime'), ('name', 'course')},
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.CharField(choices=[('P', 'P'), ('A', 'A'), ('E', 'E'), ('T', 'T')], max_length=1)),
                ('comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attendances', to='school.course')),
                ('school_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='school.schoolyear')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attendances', to='school.section')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='school.semester')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attendances', to='school.student')),
            ],
        ),
    ]
