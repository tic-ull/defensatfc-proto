# -*- encoding: utf-8 -*-

from django.db import models
from subirproyectos.settings import *
from django.core.validators import RegexValidator
import os


class Proyecto(models.Model):
    #dublin core
    title = models.CharField(max_length=200, verbose_name="título")
    creator = models.CharField(max_length=200, verbose_name="creador")
    description = models.CharField(max_length=500, verbose_name="descripción")
    type = models.CharField(max_length=200, blank=True, null=True)
    format = models.CharField(max_length=200, blank=True, null=True)
    language = models.CharField(max_length=200, verbose_name="idioma")
    relation = models.CharField(max_length=500, blank=True, null=True)
    subject = models.CharField(max_length=500, blank=True, null=True, verbose_name="tema")
    coverage = models.CharField(max_length=500, blank=True, null=True, verbose_name="cobertura")
    rights = models.CharField(max_length=500, blank=True, null=True, verbose_name="derechos")
    
    #pfc
    niu = models.CharField(max_length=15, verbose_name="NIU", validators = [RegexValidator(regex ='alu\d{10}', message='Ej: alu0100353303')])
    tutor = models.CharField(max_length=200, verbose_name="tutor")
    titulacion = models.CharField(max_length=200, choices=TITULACION, verbose_name="titulación")
    centro = models.CharField(max_length=200, choices=CENTRO, verbose_name="centro")
    universidad = models.CharField(max_length=200)
    fecha = models.DateField(blank=True, null=True, verbose_name="fecha defensa")
    calificacion = models.FloatField(blank=True, null=True, verbose_name="calificación")
    modalidad = models.CharField(max_length=200, blank=True)
    tribunal_presidente = models.CharField(max_length=500, blank=True, null=True, verbose_name="presidente del tribunal")
    tribunal_secretario = models.CharField(max_length=500, blank=True, null=True, verbose_name="secretario del tribunal")
    tribunal_vocal = models.CharField(max_length=500, blank=True, null=True, verbose_name="vocal del tribunal")

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
        


