# Generated by Django 5.1.7 on 2025-04-03 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it_infra_system', '0029_vlan_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='control_vlan',
            name='rango_ips_disponibles',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
