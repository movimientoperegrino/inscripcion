#encoding=utf8
from django.db import models
from fobi.models import FormEntry
from django.utils import timezone
# Create your models here.

class Parametro(models.Model):
    clave = models.CharField(max_length=100)
    valor = models.TextField()

    def __str__(self):
        return self.clave

class TipoActividad(models.Model):
    nombre =  models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Lugar(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    url = models.URLField(blank=True)

    def __str__(self):
        return self.nombre

class Actividad(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    tipo = models.ForeignKey(TipoActividad, blank=True, null=True, verbose_name="Tipo de actividad", on_delete=models.CASCADE)
    lugar = models.ForeignKey(Lugar, blank=True, null=True, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    costo = models.CharField(max_length=100)
    requisitos = models.TextField()
    fechaInicio = models.DateTimeField(verbose_name="Fecha de inicio")
    fechaFin = models.DateTimeField(verbose_name="Fecha de finalización")
    fechaApertura = models.DateTimeField(verbose_name="Fecha de apertura")
    fechaCierre = models.DateTimeField(verbose_name="Fecha de cierre")
    fechaCreacion = models.DateTimeField(auto_now=True)
    cantidadTitulares = models.PositiveIntegerField(verbose_name="Cantidad de Titulares")
    cantidadSuplentes = models.PositiveIntegerField(verbose_name="Cantidad de Suplentes")
    nombreContacto = models.CharField(max_length=100, verbose_name="Nombre de contacto")
    emailContacto = models.CharField(verbose_name="Email de contacto", max_length=300)
    ACTIVO = 'A'
    INACTIVO = 'I'
    FINALIZADO = 'F'
    ESTADO_OPCIONES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
        (FINALIZADO, 'Finalizado'),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_OPCIONES, default=INACTIVO)
    formDinamico = models.ForeignKey(FormEntry, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.nombre


class InscripcionBase(models.Model):
    puesto = models.PositiveIntegerField()
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=30, verbose_name="Cédula")
    celular = models.CharField(max_length=30)
    mail = models.EmailField()
    datos = models.TextField(null=True, blank=True)
    actividad = models.ForeignKey(Actividad, blank=True, null=True, on_delete=models.CASCADE)
    fechaInscripcion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de inscripción")

    def __str__(self):
        return self.nombre + " " + self.apellido