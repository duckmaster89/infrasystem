# Generated by Django 5.1.7 on 2025-03-19 13:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AMBIENTE',
            fields=[
                ('id_ambiente', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_ambiente', models.CharField(max_length=100)),
                ('descripcion_ambiente', models.TextField(blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('user_create', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
