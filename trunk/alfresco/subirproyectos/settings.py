# -*- encoding: utf-8 -*-


LIBRARY_STAFF = {
  '1' : (
     'manolo',
     'juan',
     ),
  'Escuela Tecnica Superior de Ingenieria Civil e Industrial' : (
     'pedro',
     'gomez',
     ),
  }
  
FACULTY_STAFF = {
  '1' : (
     'reyes',
     'pepe',
     ),
  'Escuela Tecnica Superior de Ingenieria Civil e Industrial' : (
     'carl',
     'timo',
     ),
  }
  
  
CENTRO = (
    ('1', 'Escuela Tecnica Superior de Ingenieria Informatica'),
    ('2', 'EScuela Tecnica Superior de Ingenieria Industrial'),
)

TITULACION = (
    ('1', 'Ingenieria Informatica'),
    ('2', 'Ingenieria Tecnica Industrial Mecanica'),
    ('3', 'Ingenieria Tecnica Industrial Electronica'),
    ('4', 'Ingenieria en Automatica y Electronica Industrial'),
    ('5', 'Ingenieria Tecnica de Obras Publicas especialidad Hidrologia'),
    #('6', 'Master en Ingenieria Informatica'),
)


TUTOR = {
  'rufino': 'Rufino Perez Reyes',
  'reinaldo': 'Reinaldo de la Cruz',
  'jmluis': 'Jose Luis de la Torre'
}

FACULTY_TUTOR = {
  '1' : (
     'rufino',
     'reinaldo'
     ),
  '2' : (
     'jmluis',
     ),
  }

CENTRO_RUTA = {
    '1' : 'cm:Escuela Técnica Superior de Ingeniería Informática',
    '2' : 'cm:Escuela Técnica Superior de Ingeniería Civil e Industrial',
}

TITULACION_RUTA = {
    '1' : 'cm:P080 Ingeniero en Informática',
    '2' : 'cm:P082 Ingeniero Técnico Industrial, Especialidad en Mecánica',
    '3' : 'cm:P083 Ingeniero Técnico Industrial, Especialidad en Electrónica Industrial',
    '4' : 'cm:P108 Ingeniero en Automática y Electrónica Industrial',
    '5' : 'cm:P092 Ingeniero Técnico de Obras Públicas, Especialidad en Hidrología',
    #'6' : 'cm:M521 Máster en Ingeniería Informática Aplicada a la Industrria, a la Ingeniería del Software y a los Sistemas y Tecnologías de la Información'
}


ALFRESCO_URL_AUTH_SERVICE = 'http://localhost:1080/alfresco/wsdl/authentication-service.wsdl'


#ALFRESCO_URL_AUTH_SERVICE = 'http://gestdoc.ccti.ull.es:8080/alfresco/wsdl/authentication-service.wsdl'

#url = 'http://localhost:8080/alfresco/wsdl/authentication-service.wsdl'

ALFRESCO_URL_RESPOSITORY_SERVICE = 'http://localhost:1080/alfresco/wsdl/repository-service.wsdl'

#ALFRESCO_URL_RESPOSITORY_SERVICE = 'http://gestdoc.ccti.ull.es:8080/alfresco/wsdl/repository-service.wsdl'

#ALFRESCO_URL_PUT = 'http://gestdoc.ccti.ull.es:8080/alfresco/upload/workspace/SpacesStore/'


#ALFRESCO_URL_PUT = 'http://localhost:8088/alfresco/upload/workspace/SpacesStore/'

ALFRESCO_URL_PUT = 'http://localhost:1081/alfresco/upload/workspace/SpacesStore/'

ALFRESCO_URL_DOWN = 'http://localhost:1081/alfresco/download/attach/workspace/SpacesStore/'




#url_repository = 'http://localhost:8080/alfresco/wsdl/repository-service.wsdl'

#ALFRESCO_USERNAME = 'admin'

#ALFRESCO_PASSWORD = 'admin'

ALFRESCO_USERNAME = 'alfrescoproyfincar'

ALFRESCO_PASSWORD = 'M4cvB73'