# -*- coding: utf-8 -*-
from datetime import date

from django.db import models
from django.contrib import auth
import os


import re

from subirproyectos import settings, validators
from subirproyectos.alfresco import Alfresco


SELECCION_ESTADO = (
    ('SOL', 'Solicitado'),
    ('REV', 'Revisado'),
    ('CAL', 'Calificado'),
    ('ARC', 'Archivado'),
)


class Centro(models.Model):
    nombre = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title


class Titulacion(models.Model):
    nombre = models.CharField(max_length=200)
    centro = models.ForeignKey(Centro)
    alfresco_uuid = models.CharField(max_length=36) # TODO: Validar: 0123456789ABCDEFabcdef

    def __unicode__(self):
        return self.title


class Contenido(models.Model):
    # dublin core
    title = models.CharField(max_length=200, verbose_name="título")
    format = models.CharField(max_length=30, choices=settings.SELECCION_FORMATO)
    description = models.TextField(verbose_name="descripción")
    type = models.CharField(max_length=30, choices=settings.SELECCION_TIPO_DOCUMENTO, default=settings.SELECCION_TIPO_DOCUMENTO[0][0])
    language = models.CharField(max_length=2, choices=settings.SELECCION_LENGUAJE, verbose_name="idioma")
    # relation: sólo se incluirá en los metados del documento en el repositorio
    # TODO: Consultar sobre publisher, identifier, URI

    # internos
    alfresco_uuid = models.CharField(max_length=36)     # TODO: Validar: 0123456789ABCDEFabcdef

    class Meta:
        abstract = True
        permissions = (
            ('puede_archivar', 'Puede revisar y archivar un trabajo'),
        )

    def __unicode__(self):
        return self.title

    def save_to_alfresco(self, cml, force_insert=False, force_update=False):
        if force_insert and force_update:
            raise ValueError("Cannot force both insert and updating in model saving.")

        if force_update or not force_insert and self.alfresco_uuid is not None:
            return cml.update(self.alfresco_uuid,
                self._get_alfresco_properties())
        else:
            def create_callback(destination):
                self.alfresco_uuid = destination.uuid
            return cml.create(self.titulacion.alfresco_uuid,
                ALFRESCO_PFC_MODEL_NAMESPACEi % contenido,
                self._get_alfresco_properties(), create_callback)

    def _get_alfresco_properties(self):
        return {
            'cm:name': self.title,
            'dc:title': self.title,
            'dc:format': self.format,
            'dc:description': self.description,
            'dc:type': self.type,
            'dc:languaje': self.languaje,
        }


class Proyecto(Contenido):
    # dublin core
    creator_nombre = models.CharField(max_length=50)
    creator_apellidos = models.CharField(max_length=50)
    creator_email = models.EmailField(max_length=50)    # TODO: Validar el dominio

    # pfc
    niu = models.CharField(max_length=10, verbose_name="NIU", validators=[validators.NIUValidator])
    centro = models.ForeignKey(Centro, verbose_name="centro")
    titulacion = models.ForeignKey(Titulacion, verbose_name="titulación")
    tutor_nombre = models.CharField(max_length=50)
    tutor_apellidos = models.CharField(max_length=50)
    tutor_email = models.EmailField(max_length=50)      # TODO: Validar el dominio
    director_nombre = models.CharField(max_length=50, blank=True, null=True)
    director_apellidos = models.CharField(max_length=50, blank=True, null=True)

    # internos
    estado = models.CharField(max_length=3, choices=SELECCION_ESTADO)

    def __getattr__(self, name):
        parts = name.rsplit('_')
        if len(parts) > 2 and parts[-1] == 'completo':
            campo_nombre = '_'.join(parts[0:-1])
            campo_apellidos = '_'.join(parts[0:-2] + ['apellidos'])
            if campo_nombre in self.__dict__ and campo_apellidos in self.__dict__:
                def nombre_completo():
                    return settings.PLANTILLA_NOMBRE_COMPLETO % {
                        'nombre': self.__dict__[campo_nombre],
                        'apellidos': self.__dict__[campo_apellidos],
                    }
                return nombre_completo

        raise AttributeError("%r object has no attribute %r" %
                             (type(self).__name__, name))

    def _get_alfresco_properties(self):
        properties = super(Proyecto, self)._get_alfresco_properties()
        return properties + {
            'dc:creator': self.creator_nombre_completo(),
            'pfc:niu': self.niu,
            'pfc:centro': self.centro.nombre,
            'pfc:titulacion': self.titulacion.nombre,
            'pfc:tutor': self.tutor_nombre_completo(),
            'pfc:director': self.director_nombre_completo(),
        }


class ProyectoCalificado(Proyecto):
    fecha_defensa = models.DateField(default=date.today(), verbose_name="fecha defensa")
    calificacion_numerica = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="calificación numérica")
    calificacion = models.CharField(max_length=30, choices=settings.SELECCION_CALIFICACION, verbose_name="calificación")     # TODO: Validar
    modalidad = models.CharField(max_length=30) # TODO: Añadir selector de modalidad
    tribunal_presidente_nombre = models.CharField(max_length=50)
    tribunal_presidente_apellidos = models.CharField(max_length=50)
    tribunal_secretario_nombre = models.CharField(max_length=50)
    tribunal_secretario_apellidos = models.CharField(max_length=50)

    def tribunal_vocales(self):
        return [vocal.nombre_completo() for vocal in
            TribunalVocal.objects.filter(proyecto_calificado=self.pk).all()]

    def _get_alfresco_properties(self):
        properties = super(ProyectoCalificado, self)._get_alfresco_properties()
        return properties + {
            'pfc:fechaDefensa': self.fecha_defensa.isoformat(),
            'pfc:calificacion': self.calificacion,
            'pfc:calificacionNumerica': self.calificacionNumerica,
            'pfc:modalidad': self.modalidad,
            'pfc:presidenteTribunal': self.tutor_nombre_completo(),
            'pfc:secretarioTribunal': self.director_nombre_completo(),
            'pfc:vocalesTribunal': self.tribunal_vocales()
        }


class TribunalVocal(models.Model):
    proyecto_calificado = models.ForeignKey(ProyectoCalificado)
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)

    def nombre_completo(self):
        return settings.PLANTILLA_NOMBRE_COMPLETO % {
            'nombre': self.nombre,
            'apellidos': self.apellidos,
        }

    def __unicode__(self):
        return self.nombre_completo()


class ProyectoArchivado(ProyectoCalificado):
    subject = models.CharField(max_length=30, verbose_name="tema")   # TODO: Añadir selector de lista de materias
    rights = models.CharField(max_length=200, choices=settings.SELECCION_DERECHOS, verbose_name="derechos")
    coverage = models.CharField(max_length=200, verbose_name="cobertura") # TODO: Añadir selector de coverage si es posible

    def _get_alfresco_properties(self):
        properties = super(ProyectoArchivado, self)._get_alfresco_properties()
        return properties + {
            'dc:subject': self.subject,
            'dc:rights': settings.TEXTO_DERECHOS[self.rights],
            'dc:coverage': self.coverage,
        }


class Anexo(Contenido):
    proyecto = models.ForeignKey(Proyecto)


def save_proyect_to_alfresco(proyecto, anexos, update_db=False):
    cml = Alfresco().cml()
    proyecto.save_to_alfresco(cml)
    for anexos in args:
        anexos.save_to_alfresco(cml)
    cml.do()

    if update_db:
        proyecto.save()
        for anexos in args:
            anexos.save()


class ULLUser(auth.models.User):
    class Meta:
        proxy = True

    def niu(self):
        m = re.match("alu(?P<niu>\d{10})$", self.username)
        if m is None:
            return None
        else:
            return m.group('niu')

    def is_student(self):
        if re.match("alu\d{10}$", self.username) is None:
            return False
        else: 
            return True

    def has_perm_puede_archivar(self, proyecto):
        if self.has_perm('puede_archivar'):
	        return AdscripcionUsuarioCentro.objects.filter(user=self.pk,
                                        centro=proyecto.centro).exists()
        else:
            return False


class AdscripcionUsuarioCentro(models.Model):
    user = models.ForeignKey(ULLUser, db_index=True)
    centro = models.ForeignKey(Centro, db_index=True)
    notificar_correo = models.BooleanField(default=False)
