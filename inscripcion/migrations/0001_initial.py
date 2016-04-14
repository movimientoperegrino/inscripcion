# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fobi', '0003_auto_20160414_0054'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100, verbose_name=b'Nombre *')),
                ('descripcion', models.TextField(verbose_name=b'Descripci\xc3\xb3n', blank=True)),
                ('costo', models.CharField(max_length=100)),
                ('requisitos', models.TextField()),
                ('fechaInicio', models.DateTimeField(verbose_name=b'Fecha de inicio')),
                ('fechaFin', models.DateTimeField(verbose_name=b'Fecha de finalizaci\xc3\xb3n')),
                ('fechaApertura', models.DateTimeField(verbose_name=b'Fecha de apertura')),
                ('fechaCierre', models.DateTimeField(verbose_name=b'Fecha de cierre')),
                ('fechaCreacion', models.DateTimeField(auto_now=True)),
                ('cantidadTitulares', models.PositiveIntegerField(verbose_name=b'Cantidad de Titulares')),
                ('cantidadSuplentes', models.PositiveIntegerField(verbose_name=b'Cantidad de Suplentes')),
                ('nombreContacto', models.CharField(max_length=100, verbose_name=b'Nombre de contacto')),
                ('emailContacto', models.CharField(max_length=300, verbose_name=b'Email de contacto')),
                ('estado', models.CharField(default=b'I', max_length=1, choices=[(b'A', b'Activo'), (b'I', b'Inactivo'), (b'F', b'Finalizado')])),
                ('formDinamico', models.ForeignKey(blank=True, to='fobi.FormEntry', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InscripcionBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('cedula', models.CharField(max_length=30)),
                ('celular', models.CharField(max_length=30)),
                ('mail', models.EmailField(max_length=254)),
                ('datos', models.TextField(null=True, blank=True)),
                ('actividad', models.ForeignKey(blank=True, to='inscripcion.Actividad', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lugar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100, verbose_name=b'Nombre *')),
                ('direccion', models.TextField(verbose_name=b'Direcci\xc3\xb3n', blank=True)),
                ('descripcion', models.TextField(verbose_name=b'Descripci\xc3\xb3n', blank=True)),
                ('url', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Parametro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('clave', models.CharField(max_length=100)),
                ('valor', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='actividad',
            name='lugar',
            field=models.ForeignKey(blank=True, to='inscripcion.Lugar', null=True),
        ),
    ]
