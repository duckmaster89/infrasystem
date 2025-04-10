# Generated by Django 5.1.7 on 2025-04-02 23:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it_infra_system', '0023_proyecto_uso_red'),
    ]

    operations = [
        migrations.AddField(
            model_name='vlan',
            name='proyecto',
            field=models.ForeignKey(blank=True, help_text='Proyecto asociado a la VLAN', null=True, on_delete=django.db.models.deletion.SET_NULL, to='it_infra_system.proyecto'),
        ),
    ]
