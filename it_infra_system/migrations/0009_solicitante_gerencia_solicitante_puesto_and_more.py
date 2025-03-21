# Generated by Django 5.1.7 on 2025-03-21 02:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it_infra_system', '0008_puesto'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitante',
            name='gerencia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='solicitantes', to='it_infra_system.gerencia'),
        ),
        migrations.AddField(
            model_name='solicitante',
            name='puesto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='solicitantes', to='it_infra_system.puesto'),
        ),
        migrations.AlterField(
            model_name='solicitante',
            name='puesto_solicitante',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
