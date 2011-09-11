from django.db import models
from subirproyectos.settings import *

class Proyecto(models.Model):
    #dublin core
    title = models.CharField(max_length=200)
    creator = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    type = models.CharField(max_length=200, blank=True, null=True)
    format = models.CharField(max_length=200, blank=True, null=True)
    language = models.CharField(max_length=200)
    relation = models.CharField(max_length=500, blank=True, null=True)
    subject = models.CharField(max_length=500, blank=True, null=True)
    coverage = models.CharField(max_length=500, blank=True, null=True)
    rights = models.CharField(max_length=500, blank=True, null=True)
    
    #pfc
    niu = models.CharField(max_length=15)
    tutor = models.CharField(max_length=200)
    centro = models.CharField(max_length=200, choices=CENTRO)
    titulacion = models.CharField(max_length=200, choices=TITULACION)
    universidad = models.CharField(max_length=200)
    fecha = models.DateField(blank=True, null=True)
    calificacion = models.FloatField(blank=True, null=True)
    modalidad = models.CharField(max_length=200, blank=True)
    tribunal_presidente = models.CharField(max_length=500, blank=True, null=True)
    tribunal_secretario = models.CharField(max_length=500, blank=True, null=True)
    tribunal_vocal = models.CharField(max_length=500, blank=True, null=True)

    #internos
    uuid = models.CharField(max_length=200)
    estado = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title

    
class Anexo(models.Model):
    proyecto = models.ForeignKey('Proyecto')
    title = models.CharField(max_length=200)
    format = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500)
    type = models.CharField(max_length=200, blank=True, null=True)
    relation = models.CharField(max_length=500, blank=True, null=True)
    uuid = models.CharField(max_length=200)
    def __unicode__(self):
        return self.title
