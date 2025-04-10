# Generated by Django 5.1.7 on 2025-03-21 14:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it_infra_system', '0011_vlan'),
    ]

    operations = [
        migrations.AddField(
            model_name='vlan',
            name='ambiente',
            field=models.ForeignKey(help_text='Ambiente al que pertenece la VLAN', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vlans', to='it_infra_system.ambiente'),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='cloud',
            field=models.ForeignKey(help_text='Cloud al que pertenece la VLAN', on_delete=django.db.models.deletion.CASCADE, related_name='vlans', to='it_infra_system.cloud'),
        ),
    ]
