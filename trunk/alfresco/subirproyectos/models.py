# -*- coding: utf-8 -*-

from django.core.validators import MaxLengthValidator
from django.db import models
from django.contrib import auth

from subirproyectos import settings, validators
from subirproyectos.alfresco import Alfresco

from datetime import date

import os
import re


SELECCION_ESTADO = (
    ('SOL', 'Solicitada la defensa'),
    ('REC', 'Rechazado'),
    ('AUT', 'Autorizado'),
    ('CAL', 'Calificado'),
    ('ARC', 'Archivado'),
)


class AlfrescoPFCModel(models.Model):
    NAMESPACES = Alfresco.NAMESPACES
    NAMESPACES['pfc'] = settings.ALFRESCO_PFC_MODEL_NAMESPACE 

    class Meta:
        abstract = True

    def get_alfresco_properties(self):
        properties = self._get_alfresco_properties()
        items = list(properties.items())
        for i, item in enumerate(items):
            (namespace, sep, name) = item[0].partition(':')
            if sep and namespace in self.NAMESPACES:
                items[i] = (self.NAMESPACES[namespace] % name, item[1])
        return dict(items)

    def _get_alfresco_properties(self):
        return {}


class Centro(AlfrescoPFCModel):
    nombre = models.CharField(max_length=200)
    codigo_centro = models.CharField(max_length=200)
    alfresco_uuid = models.CharField(max_length=36, blank = 'true', null = 'true', validators=[validators.UUIDValidator])

    def __unicode__(self):
        return self.nombre
    
    def _get_alfresco_properties(self):
        return {
            'cm:name': self.nombre,
	    'pfc:codigoCentro' : self.codigo_centro,
    }    


class Titulacion(AlfrescoPFCModel):
    nombre = models.CharField(max_length=200)
    centro = models.ForeignKey(Centro)
    codigo_plan = models.CharField(max_length=200)
    anyo_comienzo_plan = models.IntegerField()
    titulacion_vigente = models.BooleanField()
    alfresco_uuid = models.CharField(max_length=36, blank = 'true', null = 'true', validators=[validators.UUIDValidator])

    def __unicode__(self):
        return self.nombre

    def _get_alfresco_properties(self):
        return {
            'cm:name': self.nombre,
	    'pfc:codigoPlan' : self.codigo_plan,
	    'pfc:anyoComienzoPlan' : self.anyo_comienzo_plan,
	    'pfc:titulacionVigente' : self.titulacion_vigente
        }    


class Contenido(AlfrescoPFCModel):
    # dublin core
    title = models.CharField(max_length=200, verbose_name="título")
    format = models.CharField(max_length=30, choices=settings.SELECCION_FORMATO)
    description = models.TextField(verbose_name="descripción", validators=[MaxLengthValidator(1000)])
    type = models.CharField(max_length=30, choices=settings.SELECCION_TIPO_DOCUMENTO, default=settings.DEFECTO_TIPO_DOCUMENTO)
    language = models.CharField(max_length=2, choices=settings.SELECCION_LENGUAJE, verbose_name="idioma", default=settings.DEFECTO_LENGUAJE)
    # relation: sólo se incluirá en los metados del documento en el repositorio
    # TODO: Consultar sobre publisher, identifier, URI

    # internos
    alfresco_uuid = models.CharField(max_length=36, validators=[validators.UUIDValidator])

    class Meta:
        abstract = True
        permissions = (
            ('puede_archivar', 'Puede revisar y archivar un trabajo'),
        )

    def __unicode__(self):
        return self.title

    def type_detallado(self):
        return [value for key, value in settings.SELECCION_TIPO_DOCUMENTO if key == self.type][0]

    def language_detallado(self):
        return [value for key, value in settings.SELECCION_LENGUAJE if key == self.language][0]

    def save_to_alfresco(self, parent_uuid, cml, force_insert=False, force_update=False):
        if force_insert and force_update:
            raise ValueError("Cannot force both insert and updating in model saving.")

	if force_update or not force_insert and self.alfresco_uuid:
            return cml.update(self.alfresco_uuid,
                self.get_alfresco_properties())
        else:
            def create_callback(result):
                self.alfresco_uuid = result.destination.uuid
            return cml.create(parent_uuid,
                settings.ALFRESCO_PFC_MODEL_NAMESPACE % 'contenido',
                self.get_alfresco_properties(), create_callback)

    def _get_alfresco_properties(self):
        return {
            'cm:name': self.title,
            'cm:title': self.title,
            'cm:format': self.format,
            'cm:description': self.description,
            'cm:type': self.type,
            'cm:language': self.language,
        }


class Proyecto(Contenido):
    # dublin core
    creator_nombre = models.CharField(max_length=50, verbose_name= 'nombre del autor')
    creator_apellidos = models.CharField(max_length=50, verbose_name= 'apellidos del autor')
    creator_email = models.EmailField(max_length=50,
                                      verbose_name = 'correo electrónico del autor',
                                      validators=[validators.EmailCreatorValidator])
    # pfc
    niu = models.CharField(max_length=10, verbose_name="NIU", validators=[validators.NIUValidator])
    titulacion = models.ForeignKey(Titulacion, verbose_name="titulación")
    tutor_nombre = models.CharField(max_length=50, verbose_name='nombre del tutor')
    tutor_apellidos = models.CharField(max_length=50, verbose_name='apellidos del tutor')
    tutor_email = models.EmailField(max_length=50,
                                    verbose_name='correo electrónico del tutor',
                                    validators=[validators.EmailTutorValidator],
                                    db_index=True)
    director_nombre = models.CharField(max_length=50, blank=True, null=True,
                                       verbose_name='nombre del director')
    director_apellidos = models.CharField(max_length=50, blank=True, null=True,
                                          verbose_name='apellidos del director')

    # internos
    fecha_subido = models.DateField(auto_now_add = True)
    estado = models.CharField(max_length=3, choices=SELECCION_ESTADO)

    def __getattr__(self, name):
        parts = name.rsplit('_')
        if len(parts) > 2 and parts[-1] == 'completo':
            campo_nombre = '_'.join(parts[0:-1])
            campo_apellidos = '_'.join(parts[0:-2] + ['apellidos'])
            if campo_nombre in self.__dict__ and campo_apellidos in self.__dict__:
                if self.__dict__[campo_nombre] and self.__dict__[campo_apellidos]:
                    def nombre_completo():
                        return settings.PLANTILLA_NOMBRE_COMPLETO % {
                            'nombre': self.__dict__[campo_nombre],
                            'apellidos': self.__dict__[campo_apellidos],
                        }
                else:
                    def nombre_completo():
                        return None
                return nombre_completo

        raise AttributeError("%r object has no attribute %r" %
                             (type(self).__name__, name))

    def estado_detallado(self):
        return [value for key, value in SELECCION_ESTADO if key == self.estado][0]

    @models.permalink
    def get_absolute_url(self):
        return ('proyecto_view', (), {'id': self.id})

    def _get_alfresco_properties(self):
        properties = super(Proyecto, self)._get_alfresco_properties()
        properties['cm:creator'] = self.creator_nombre_completo()
        properties['pfc:niu'] = self.niu
        properties['pfc:centro'] = self.titulacion.centro.nombre
        properties['pfc:titulacion'] = self.titulacion.nombre
        properties['pfc:tutor'] = self.tutor_nombre_completo()
        properties['pfc:director'] = self.director_nombre_completo()
        return properties


class ProyectoCalificado(Proyecto):
    fecha_defensa = models.DateField(default=date.today(), verbose_name="fecha defensa")
    calificacion_numerica = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="calificación numérica")
    calificacion = models.CharField(max_length=30, choices=settings.SELECCION_CALIFICACION, verbose_name="calificación")
    modalidad = models.CharField(max_length=30) # TODO: Añadir selector de modalidad
    tribunal_presidente_nombre = models.CharField(max_length=50)
    tribunal_presidente_apellidos = models.CharField(max_length=50)
    tribunal_secretario_nombre = models.CharField(max_length=50)
    tribunal_secretario_apellidos = models.CharField(max_length=50)
 
    def clean(self):
	if (self.calificacion_numerica >= 0.0) and (self.calificacion_numerica <= 4.9):
            if self.calificacion == 'Suspenso':
		return
	if (self.calificacion_numerica >= 5) and (self.calificacion_numerica <= 6.9):    
	    if self.calificacion == 'Aprobado':
		return
	if (self.calificacion_numerica >= 7) and (self.calificacion_numerica <= 8.9):   
	    if self.calificacion == 'Notable':
		return
	if (self.calificacion_numerica >= 9) and (self.calificacion_numerica <= 10):    
	    if self.calificacion == 'Sobresaliente':	    
		return
	exceptions.ValidationError("La calificación y la nota numérica no coinciden")

    def tribunal_vocales(self):
        return [vocal.nombre_completo() for vocal in
            TribunalVocal.objects.filter(proyecto_calificado=self.pk).all()]

    def _get_alfresco_properties(self):
        properties = super(ProyectoCalificado, self)._get_alfresco_properties()
        properties['pfc:fechaDefensa'] = self.fecha_defensa.isoformat()
        properties['pfc:calificacion'] = self.calificacion
        properties['pfc:calificacionNumerica'] = self.calificacion_numerica
        properties['pfc:modalidad'] = self.modalidad
        properties['pfc:presidenteTribunal'] = self.tutor_nombre_completo()
        properties['pfc:secretarioTribunal'] = self.director_nombre_completo()
        properties['pfc:vocalesTribunal'] = self.tribunal_vocales()
        return properties


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
    subject = models.CharField(max_length=30, verbose_name="tema")
    rights = models.CharField(max_length=200, choices=settings.SELECCION_DERECHOS, verbose_name="derechos")
    coverage = models.CharField(max_length=200, verbose_name="cobertura")

    def _get_alfresco_properties(self):
        properties = super(ProyectoArchivado, self)._get_alfresco_properties()
        properties['cm:subject'] = self.subject
        properties['cm:rights'] = settings.TEXTO_DERECHOS[self.rights]
        properties['cm:coverage'] = self.coverage
        return properties


class Anexo(Contenido):
    proyecto = models.ForeignKey(Proyecto)

    @models.permalink
    def get_absolute_url(self):
        return ('anexo_view', (), {
            'id': self.proyecto.id,
            'anexo_id': self.id,
        })

    # Muchas de las propiedades de los anexos se heredan de las del proyecto
    def _get_alfresco_properties(self):
        properties = self.proyecto._get_alfresco_properties()
        properties.update(super(Anexo, self)._get_alfresco_properties())
        return properties


def save_proyect_to_alfresco(proyecto, anexos,
                             update_relationship=True, update_db=False,
                             proyecto_contenido=None, anexos_contenidos=()):
    """ Salvar toda la información relacionada con un proyecto en el gestor
    documental"""

    cml = Alfresco().cml()

    proyecto.save_to_alfresco(proyecto.titulacion.alfresco_uuid, cml)
    for anexo in anexos:
        anexo.save_to_alfresco(anexo.proyecto.titulacion.alfresco_uuid, cml)
    cml.do()

    if proyecto_contenido is not None:
        Alfresco().upload_content(proyecto.alfresco_uuid, proyecto_contenido)
    for anexo, contenido in zip(anexos, anexos_contenidos):
        Alfresco().upload_content(anexo.alfresco_uuid, contenido)

    if update_relationship and anexos:
        # Si es necesario, hay que salvar la relacion entre los documentos
        cml = Alfresco().cml()
        relation_propname = Alfresco.NAMESPACES['dc'] % 'relation'
        proyecto_relaciones = ['hastPart %s' % anexo.alfreso_uuid for anexo in anexos]
        cml.update(proyecto.alfresco_uuid, {
            relation_propname: proyecto_relaciones
        })
        for anexo in anexos:
            cml.update(anexo.alfresco_uuid, {
                property_relation: 'isPartOf %s' % proyecto.alfresco_uuid
            })
        cml.do()

    if update_db:
        proyecto.save()
        for anexo in anexos:
            anexo.save()


#
# Extendemos auth.models.User con nuevos métodos
#

def user_niu(self):
    m = re.match("alu(?P<niu>\d{10})$", self.username)
    if m is None:
        return None
    else:
        return m.group('niu')

def user_is_tutor(self):
    return Proyecto.objects.filter(tutor_email=self.email).exists()

def user_can_view_proyecto(self, proyecto):
    return (proyecto.creator_email == self.email or
            proyecto.tutor_email == self.email)

def user_can_autorizar_proyecto(self, proyecto):
    return (proyecto.tutor_email == self.email)

auth.models.User.add_to_class('niu', user_niu)
auth.models.User.add_to_class('is_tutor', user_is_tutor)
auth.models.User.add_to_class('can_view_proyecto', user_can_view_proyecto)
auth.models.User.add_to_class('can_autorizar_proyecto', user_can_autorizar_proyecto)


class AdscripcionUsuarioCentro(models.Model):
    user = models.ForeignKey(auth.models.User, db_index=True)
    centro = models.ForeignKey(Centro, db_index=True)
    notificar_correo = models.BooleanField(default=False)
