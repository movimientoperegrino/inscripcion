# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscripcion', '0002_auto_20160409_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscripcion_base',
            name='actividad',
            field=models.ForeignKey(blank=True, to='inscripcion.Actividad', null=True),
        ),
    ]
