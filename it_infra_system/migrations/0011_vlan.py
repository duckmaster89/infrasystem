# Generated by Django 5.1.7 on 2025-03-21 14:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it_infra_system', '0010_alter_solicitante_id_solicitante'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VLAN',
            fields=[
                ('id_vlan', models.AutoField(primary_key=True, serialize=False)),
                ('numero_vlan', models.IntegerField(help_text='Número de VLAN (1-4094)', unique=True)),
                ('barra_vlan', models.IntegerField(help_text='Máscara de subred en notación CIDR (0-32)')),
                ('segmento_vlan', models.GenericIPAddressField(help_text='Dirección IPv4 del segmento', protocol='IPv4')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('cloud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vlans', to='it_infra_system.cloud')),
                ('user_create', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'VLAN',
                'verbose_name_plural': 'VLANs',
                'ordering': ['numero_vlan'],
            },
        ),
    ]
