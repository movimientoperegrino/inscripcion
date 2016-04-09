# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fobi', '0003_auto_20160409_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Nombre', models.CharField(max_length=100, verbose_name=b'Nombre *')),
                ('detalle', models.ForeignKey(blank=True, to='fobi.FormEntry', null=True)),
            ],
        ),
    ]
