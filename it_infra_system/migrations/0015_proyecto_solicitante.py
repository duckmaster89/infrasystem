# Generated by Django 5.1.7 on 2025-03-21 20:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it_infra_system', '0014_status_proyecto'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='solicitante',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='it_infra_system.solicitante'),
        ),
    ]
