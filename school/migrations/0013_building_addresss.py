# Generated by Django 4.2.6 on 2023-10-31 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0012_building_addresss'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='addresss',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='buildings', to='school.addresss'),
        ),
    ]
