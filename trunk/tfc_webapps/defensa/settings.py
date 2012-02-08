# -*- coding: utf-8 -*-
from iso639 import ISO639_1


PLANTILLA_NOMBRE_COMPLETO = '%(apellidos)s, %(nombre)s'


DOMINIO_CORREO_ALUMNO = 'ull.edu.es'
DOMINIO_CORREO_TUTOR = 'ull.es'


TIPO_DOCUMENTO_SELECCION = (
    ('anexo',   u'Anexo'),
    ('memoria', u'Memoria'),
    ('plano',   u'Plano'),
)
TIPO_DOCUMENTO_DEFECTO = 'anexo'


LENGUAJE_SELECCION = sorted(ISO639_1, key=lambda lang: lang[1])
LENGUAJE_DEFECTO = 'es'


FORMATO_SELECCION = (
    ('application/pdf', 'PDF'),
)


DERECHOS_SELECCION = (
    ('CC-BY', u'Creative Commons Reconocimiento 3.0 España'),
    ('CC-BY-SA', u'Creative Commons Reconocimiento-CompartirIgual 3.0 España'),
    ('CC-BY-ND', u'Creative Commons Reconocimiento-SinObraDerivada 3.0 España'),
    ('CC-BY-NC', u'Creative Commons Reconocimiento-NoComercial 3.0 España'),
    ('CC-BY-NC-SA', u'Creative Commons Reconocimiento-NoComercial-CompartirIgual 3.0 España'),
    ('CC-BY-NC-ND', u'Creative Commons Reconocimiento-NoComercial-SinObraDerivada 3.0 España'),
    ('COPYRIGHT', u'Todos los derechos reservados'),
)


TEXTO_DERECHOS = {
    'CC-BY': u"Esta obra está bajo una licencia Creative Commons " +
             u"Reconocimiento 3.0 España - " +
             u"http://creativecommons.org/licenses/by/3.0/es/",
    'CC-BY-SA': u"Esta obra está bajo una license Creative Commons " +
                u"Reconocimiento-CompartirIgual 3.0 España - " +
                u"http://creativecommons.org/licenses/by-sa/3.0/es/",
    'CC-BY-ND': u"Esta obra está bajo una licencia Creative Commons " +
                u"Reconocimiento-SinObraDerivada 3.0 España - " +
                u"http://creativecommons.org/licenses/by-nd/3.0/es/",
    'CC-BY-NC': u"Esta obra está bajo una licencia Creative Commons " +
                u"Reconocimiento-NoComercial 3.0 España - " +
                u"http://creativecommons.org/licenses/by-nc/3.0/es/",
    'CC-BY-NC-SA': u"Esta obra está bajo una licencia Creative Commons " +
                   u"Reconocimiento-NoComercial-CompartirIgual 3.0 España - "
                   u"http://creativecommons.org/licenses/by-nc-sa/3.0/es/",
    'CC-BY-NC-ND': u"Esta obra está bajo una licencia Creative Commons " +
                   u"Reconocimiento-NoComercial-SinObraDerivada 3.0 España - " +
                   u"http://creativecommons.org/licenses/by-nc-nd/3.0/es/",
    'COPYRIGHT': u"Esta obra está protegida por derechos de autor. " +
                 u"Todos los derechos reservados",
}


CALIFICACION_SELECCION = (
    ('suspenso', u'Suspenso'),
    ('aprobado', u'Aprobado'),
    ('notable', u'Notable'),
    ('sobresaliente', u'Sobresaliente'),
    ('matricula', u'Matrícula de honor'),
)


DESCARGAR_CONTENIDO_FILENAME = 'memoria-%s.pdf'
DESCARGAR_ANEXO_FILENAME = 'anexo_%2d-%s.pdf'


# Correos de notificación
FROM_EMAIL = "noreply@ull.es"
ASUNTO_PROYECTO_SOLICITADO = u"Solicitud de defensa de trabajo fin de carrera"
ASUNTO_PROYECTO_AUTORIZADO_ALUMNO = u"La defensa de su trabajo fin de carrera ha sido autorizada"
ASUNTO_PROYECTO_RECHAZADO_ALUMNO = u"La defensa de su trabajo fin de carrera ha sido rechazada"
ASUNTO_PROYECTO_AUTORIZADO_TUTOR = u"Éxito autorizando la defensa de un trabajo de fin de carrera"
ASUNTO_PROYECTO_CALIFICADO = u"Trabajo fin de carrera calificado pendiente de archivo"


# Configuración de alfresco
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
