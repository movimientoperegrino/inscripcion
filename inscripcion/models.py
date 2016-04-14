from django.db import models
from fobi.models import FormEntry
# Create your models here.

class Actividad(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre *")

    detalle = models.ForeignKey(FormEntry, blank=True, null=True)

    def __unicode__(self):
        return self.nombre


class InscripcionBase(models.Model):
    #nombre = models.CharField(max_length=100, verbose_name="Nombre")
    #apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=30)
    datos = models.TextField(null=True,blank=True)
    actividad = models.ForeignKey(Actividad, blank=True, null=True)

    def __unicode__(self):
        return self.cedula