# -*- coding: utf-8 -*-
from iso691 import ISO691_1


PLANTILLA_NOMBRE_COMPLETO = '%(apellidos)s, %(nombre)s'

DOMINIO_CORREO_ALUMNO = 'ull.edu.es'
DOMINIO_CORREO_TUTOR = 'ull.es'

SELECCION_TIPO_DOCUMENTO = (
    ('ANEXO',   'Anexo'),
    ('MEMORIA', 'Memoria'),    
    ('PLANO',   'Plano'),
)

SELECCION_LENGUAJE = ISO691_1
DEFECTO_LENGUAJE = 'es'

SELECCION_FORMATO = (
    ('application/pdf', 'PDF'),
)

SELECCION_DERECHOS = (
    ('CC-BY', 'Creative Commons Reconocimiento 3.0 España'),
    ('CC-BY-SA', 'Creative Commons Reconocimiento-CompartirIgual 3.0 España'),
    ('CC-BY-ND', 'Creative Commons Reconocimiento-SinObraDerivada 3.0 España'),
    ('CC-BY-NC', 'Creative Commons Reconocimiento-NoComercial 3.0 España'),
    ('CC-BY-NC-SA', 'Creative Commons Reconocimiento-NoComercial-CompartirIgual 3.0 España'),
    ('CC-BY-NC-ND', 'Creative Commons Reconocimiento-NoComercial-SinObraDerivada 3.0 España'),
    ('COPYRIGHT', 'Todos los derechos reservados'),
)

TEXTO_DERECHOS = {
    'CC-BY': "Esta obra está bajo una licencia Creative Commons " +
             "Reconocimiento 3.0 España - " +
             "http://creativecommons.org/licenses/by/3.0/es/",
    'CC-BY-SA': "Esta obra está bajo una license Creative Commons " +
                "Reconocimiento-CompartirIgual 3.0 España - " +
                "http://creativecommons.org/licenses/by-sa/3.0/es/",
    'CC-BY-ND': "Esta obra está bajo una licencia Creative Commons " +
                "Reconocimiento-SinObraDerivada 3.0 España - " +
                "http://creativecommons.org/licenses/by-nd/3.0/es/",
    'CC-BY-NC': "Esta obra está bajo una licencia Creative Commons " +
                "Reconocimiento-NoComercial 3.0 España - " +
                "http://creativecommons.org/licenses/by-nc/3.0/es/",
    'CC-BY-NC-SA': "Esta obra está bajo una licencia Creative Commons " +
                   "Reconocimiento-NoComercial-CompartirIgual 3.0 España - "
                   "http://creativecommons.org/licenses/by-nc-sa/3.0/es/",
    'CC-BY-NC-ND': "Esta obra está bajo una licencia Creative Commons " +
                   "Reconocimiento-NoComercial-SinObraDerivada 3.0 España - " +
                   "http://creativecommons.org/licenses/by-nc-nd/3.0/es/",
    'COPYRIGHT': "Esta obra está protegida por derechos de autor. " +
                 "Todos los derechos reservados",
}

SELECCION_CALIFICACION = (
    ('SS', 'Suspenso'),
    ('AP', 'Aprobado'),
    ('NT', 'Notable'),
    ('SB', 'Sobresaliente'),
    ('MH', 'Matrícula de honor'),
)

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
