# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscripcion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inscripcion_Base',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cedula', models.CharField(max_length=30)),
                ('datos', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.RenameField(
            model_name='actividad',
            old_name='Nombre',
            new_name='nombre',
        ),
    ]
