# -*- coding: utf-8 -*-
from django.conf import settings

from iso639 import ISO639_1
from itertools import chain, groupby

import os


NOMBRE_COMPLETO_PLANTILLA = '%(apellidos)s, %(nombre)s'


DOMINIO_CORREO_ALUMNO = 'ull.edu.es'
DOMINIO_CORREO_TUTOR = 'ull.es'


LENGUAJE_SELECCION = sorted(ISO639_1, key=lambda lang: lang[1])
LENGUAJE_DEFECTO = 'es'


PUBLISHER_DEFECTO = u"Universidad de La Laguna"


TIPO_DOCUMENTO_TRABAJO_SELECCION = (
    ('memoria_tfc',     u'Memoria de trabajo fin de carrera'),
)
MEMORIA_TFC_TIPO_DOCUMENTO = 'memoria_tfc'


TIPO_DOCUMENTO_ANEXO_SELECCION = (
    ('articulo',        u'Artículo'),
    ('datos',           u'Conjunto de datos'),
    ('dibujo',          u'Dibujo'),
    ('diagrama',        u'Diagrama'),
    ('diseño_grafico',  u'Diseño gráfico'),
    ('documento',       u'Documento'),
    ('informe',         u'Informe'),
    ('mapa',            u'Mapa'),
    ('memoria',         u'Memoria'),
    ('pintura',         u'Pintura'),
    ('plano',           u'Plano'),
    ('software',        u'Software'),
    ('sonido',          u'Sonido'),
    ('video',           u'Vídeo'),
)


# Todos deben tener al menos un término de DCMI
# http://dublincore.org/documents/dcmi-type-vocabulary/
TIPO_DOCUMENTO_TO_DUBLIN_CORE = {
    'articulo':        ('Text', u'Artículo'),
    'datos':           ('Dataset', u'Conjunto de datos'),
    'dibujo':          ('Image', 'StillImage', u'Dibujo'),
    'diagrama':        ('Image', 'StillImage', u'Diagrama'),
    'diseño_grafico':  ('Image', 'StillImage', u'Diseño gráfico'),
    'documento':       ('Text', u'Documento'),
    'informe':         ('Text', u'Informe'),
    'mapa':            ('Image', 'StillImage', 'Text', u'Mapa'),
    'memoria_tfc':     ('Text', u'Memoria TFC'),
    'memoria':         ('Text', u'Memoria'),
    'pintura':         ('Image', 'StillImage', u'Pintura'),
    'plano':           ('Image', 'StillImage', 'Text', u'Plano'),
    'software':        ('Software'),
    'sonido':          ('Sound', u'Sonido'),
    'video':           ('Image', 'MovingImage', u'Vídeo'),
}

TIPO_DOCUMENTO_TO_FORMATO = {
    'articulo':        ('application/pdf'),
    'datos':           (),
    'dibujo':          (),
    'diagrama':        (),
    'diseño_grafico':  (),
    'documento':       ('application/pdf'),
    'informe':         ('application/pdf'),
    'mapa':            (),
    'memoria_tfc':     ('application/pdf'),
    'memoria':         ('application/pdf'),
    'pintura':         (),
    'plano':           (),
    'software':        ('application/x-zip-compressed'),
    'sonido':          (),
    'video':           (),
}

FORMATO_SELECCION = (
    ('application/pdf', 'PDF'),
    ('application/x-zip-compressed', 'ZIP'),
)


MODALIDAD_SELECCION = (
    ('TFC', u'Trabajo fin de carrera'),
)
MODALIDAD_DEFECTO = 'TFC'


DERECHOS_SELECCION = (
    ('CC-BY', u'Creative Commons Reconocimiento 3.0 España'),
    ('CC-BY-SA', u'Creative Commons Reconocimiento-CompartirIgual 3.0 España'),
    ('CC-BY-ND', u'Creative Commons Reconocimiento-SinObraDerivada 3.0 España'),
    ('CC-BY-NC', u'Creative Commons Reconocimiento-NoComercial 3.0 España'),
    ('CC-BY-NC-SA', u'Creative Commons Reconocimiento-NoComercial-CompartirIgual 3.0 España'),
    ('CC-BY-NC-ND', u'Creative Commons Reconocimiento-NoComercial-SinObraDerivada 3.0 España'),
    ('COPYRIGHT', u'Todos los derechos reservados'),
)

DERECHOS = {
    'CC-BY': {
        'texto':  u"Esta obra está bajo una licencia Creative Commons " +
                  u"Reconocimiento 3.0 España",
        'url':    "http://creativecommons.org/licenses/by/3.0/es/",
        'imagen': "http://i.creativecommons.org/l/by/3.0/80x15.png",
    },
    'CC-BY-SA': {
        'texto':  u"Esta obra está bajo una licencia Creative Commons " +
                  u"Reconocimiento-CompartirIgual 3.0 España",
        'url':    "http://creativecommons.org/licenses/by-sa/3.0/es/",
        'imagen': "http://i.creativecommons.org/l/by-sa/3.0/80x15.png",
    },
    'CC-BY-ND': {
        'texto':  u"Esta obra está bajo una licencia Creative Commons " +
                  u"Reconocimiento-SinObraDerivada 3.0 España",
        'url':    "http://creativecommons.org/licenses/by-nd/3.0/es/",
        'imagen': "http://i.creativecommons.org/l/by-nd/3.0/80x15.png",
    },
    'CC-BY-NC': {
        'texto':  u"Esta obra está bajo una licencia Creative Commons " +
                  u"Reconocimiento-NoComercial 3.0 España",
        'url':    "http://creativecommons.org/licenses/by-nc/3.0/es/",
        'imagen': "http://i.creativecommons.org/l/by-nc/3.0/80x15.png",
    },
    'CC-BY-NC-SA': {
        'texto':  u"Esta obra está bajo una licencia Creative Commons " +
                  u"Reconocimiento-NoComercial-CompartirIgual 3.0 España",
        'url':    "http://creativecommons.org/licenses/by-nc-sa/3.0/es/",
        'imagen': "http://i.creativecommons.org/l/by-nc-sa/3.0/80x15.png",
    },
    'CC-BY-NC-ND': {
        'texto':  u"Esta obra está bajo una licencia Creative Commons " +
                  u"Reconocimiento-NoComercial-SinObraDerivada 3.0 España",
        'url':    "http://creativecommons.org/licenses/by-nc-nd/3.0/es/",
        'imagen': "http://i.creativecommons.org/l/by-nc-nd/3.0/80x15.png",
    },
    'COPYRIGHT': {
        'texto':  u"Esta obra está protegida por derechos de autor. " +
                  u"Todos los derechos reservados",
        'url':    "http://es.wikipedia.org/wiki/Derecho_de_autor",
        'imagen': settings.STATIC_URL + "images/copyright.png",
    },
}


CALIFICACION_SELECCION = (
    ('SS', u'Suspenso'),
    ('AP', u'Aprobado'),
    ('NT', u'Notable'),
    ('SB', u'Sobresaliente'),
    ('MH', u'Matrícula de honor'),
)

#Grupos de usuarios
PUEDEN_ARCHIVAR = 'Bibliotecarios'


DESCARGAR_CONTENIDO_FILENAME = 'memoria-%s.pdf'
DESCARGAR_ANEXO_FILENAME = 'anexo_%2d-%s.pdf'
DESCARGAR_AUTORIZACION_FILENAME = 'autorizacion_defensa-%s.pdf'


# Conversión a PDF
if settings.DEBUG:
    PDF_STATIC_URL = ("file://%s/" %
        os.path.join(os.path.normpath(os.path.dirname(__file__)), 'static'))
else:
    PDF_STATIC_URL = "file://" + settings.STATIC_ROOT


# Correos de notificación
FROM_EMAIL = "noreply@ull.es"
ASUNTO_TRABAJO_SOLICITADO = u"Solicitud de defensa de trabajo fin de carrera"
ASUNTO_TRABAJO_AUTORIZADO_ALUMNO = u"La defensa de su trabajo fin de carrera ha sido autorizada"
ASUNTO_TRABAJO_RECHAZADO_ALUMNO = u"La defensa de su trabajo fin de carrera ha sido rechazada"
ASUNTO_TRABAJO_AUTORIZADO_TUTOR = u"Éxito autorizando la defensa de un trabajo de fin de carrera"
ASUNTO_TRABAJO_CALIFICADO = u"Trabajo fin de carrera calificado pendiente de archivo"


# Configuración de alfresco
ALFRESCO_ENABLED = False
ALFRESCO_PROXY_SERVER = {
    'http': 'localhost:1080'
}
ALFRESCO_USERNAME = 'alfrescoproyfincar'
ALFRESCO_PASSWORD = 'M4cvB73'

ALFRESCO_PFC_MODEL_NAMESPACE = '{http://www.ull.es/2011/10/04/pfc.xsd}%s'
ALFRESCO_PFC_FOLDER_UUID = '66fdb019-1500-4fdf-9e76-94d15ef04b55'

ALFRESCO_URL_AUTH_SERVICE = 'http://localhost:1080/alfresco/wsdl/authentication-service.wsdl'
#ALFRESCO_URL_AUTH_SERVICE = 'http://gestdoc.ccti.ull.es:8080/alfresco/wsdl/authentication-service.wsdl'
ALFRESCO_URL_RESPOSITORY_SERVICE = 'http://localhost:1080/alfresco/wsdl/repository-service.wsdl'
#ALFRESCO_URL_RESPOSITORY_SERVICE = 'http://gestdoc.ccti.ull.es:8080/alfresco/wsdl/repository-service.wsdl'
ALFRESCO_URL_PUT = 'http://localhost:1081/alfresco/upload/workspace/SpacesStore/%(uuid)s/%(filename)s?ticket=%(ticket)s'
#ALFRESCO_URL_PUT = 'http://gestdoc.ccti.ull.es:8080/alfresco/upload/workspace/SpacesStore/'
ALFRESCO_URL_DOWN = 'http://localhost:1081/alfresco/download/attach/workspace/SpacesStore/%(uuid)s/%(filename)s?ticket=%(ticket)s'
