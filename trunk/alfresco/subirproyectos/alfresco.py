# -*- encoding: utf-8 -*-

from suds.client import Client
from suds.wsse import *
from datetime import datetime, timedelta
import logging
import put
from subirproyectos.settings import *
import suds

logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO)

def is_ascii(s):
    return all(ord(c) < 128 for c in s)
    

def encode(s):
  encoded_str = ''
  for carac in s:
    if is_ascii(carac):
      if (carac == ' ') or (carac == ','):
	encoded_str += "_x%04x_" % ord(carac)
      else:
	encoded_str += carac    
    else:
      encoded_str += "_x%04x_" % ord(carac)
  return encoded_str





class Alfresco:
    def __init__(self, username= ALFRESCO_USERNAME, password= ALFRESCO_PASSWORD):
	#url = 'http://localhost:8080/alfresco/wsdl/authentication-service.wsdl'
	
	#t = suds.transport.http.HttpTransport()
	#proxy = urllib2.ProxyHandler({'http': 'http://localhost:1080'})
	#opener = urllib2.build_opener(proxy)
	#t.urlopener = opener
	
	d = dict(http='localhost:1080')
	client = Client(ALFRESCO_URL_AUTH_SERVICE, proxy= d)
	print client
	self.client = client
	#client.set_options(proxy=d)
	login_res = client.service.startSession(username, password)  
	self.ticket = login_res['ticket']
	security = Security()
	token = UsernameToken(username, self.ticket)
	timestamp = Timestamp ()
	security.tokens.append(timestamp)
	security.tokens.append(token)
        self.security = security

    def subir_pfc (self, f, p):
	#url_repository = 'http://localhost:8080/alfresco/wsdl/repository-service.wsdl'
	d = dict(http='localhost:1080')
	client_repository = Client(ALFRESCO_URL_RESPOSITORY_SERVICE, proxy= d)
	client_repository.set_options(wsse=self.security)
	print client_repository
	cml = client_repository.factory.create('ns0:CML')
	print cml
	
	create = client_repository.factory.create('ns0:create')
	print create
    
	create.id = '1'
    
	parent_reference = client_repository.factory.create('ns2:ParentReference')

	parent_reference.associationType = '{http://www.alfresco.org/model/content/1.0}contains'
	parent_reference.childName = '{http://www.alfresco.org/model/content/1.0}' + p.title
	#path = '/app:company_home/cm:TFC/cm:Escuela Técnica Superior de Ingeniería Informática/cm:P080 Ingeniero en Informática'
	path = '/app:company_home/cm:TFC/' + CENTRO_RUTA[p.centro] + '/' + TITULACION_RUTA[p.titulacion] 
	enc_path = unicode(path, 'utf-8')
	final_path = encode(enc_path)	
	
	
	parent_reference.path = final_path 
	store = client_repository.factory.create('ns2:Store')
	store.scheme = 'workspace'
	store.address = 'SpacesStore'
	parent_reference.store = store
	create.parent = parent_reference
	create.type = '{http://www.alfresco.org/model/content/1.0}folder'
	named_value = client_repository.factory.create('ns2:NamedValue')
	print named_value
	named_value.name = '{http://www.alfresco.org/model/content/1.0}name'
	named_value.value =  p.title
	named_value.isMultiValue = False
	create.property.append(named_value)	
	
	
	
	
	cml.create.append  (create)
	
	
	create = client_repository.factory.create('ns0:create')
	print create
    
	create.id = '2'
    
	parent_reference = client_repository.factory.create('ns2:ParentReference')

	parent_reference.associationType = '{http://www.alfresco.org/model/content/1.0}contains'
	parent_reference.childName = '{http://www.alfresco.org/model/content/1.0}' + f.name
	#path = u'/app:company_home/cm:TFC/cm:Escuela Técnica Superior de Ingeniería Informática/cm:P080 Ingeniero en Informática/cm:' + p.title
	path = '/app:company_home/cm:TFC/' + unicode(CENTRO_RUTA[p.centro], 'utf8') + '/' + unicode(TITULACION_RUTA[p.titulacion], 'utf-8') + '/cm:' + p.title 
	#enc_path = unicode(path, 'utf-8')
	final_path = encode(path)	
	
	
	parent_reference.path = final_path 
	store = client_repository.factory.create('ns2:Store')
	store.scheme = 'workspace'
	store.address = 'SpacesStore'
	parent_reference.store = store
	create.parent = parent_reference
	create.type = '{http://www.alfresco.org/model/content/1.0}content'
	named_value = client_repository.factory.create('ns2:NamedValue')
	print named_value
	named_value.name = '{http://www.alfresco.org/model/content/1.0}name'
	named_value.value = f.name
	named_value.isMultiValue = False
	create.property.append(named_value)
	

	
	
	print create
	cml.create.append  (create)



        ##ASPECTO PFC
	#addAspectpfc = client_repository.factory.create('ns0:addAspect')
	#print addAspectpfc
	#addAspectpfc.aspect = '{http://www.ull.es/2010/06/28/pfc.xsd}metadatosTFC'
	#addAspectpfc.where_id = '1'
	##metadato pfc:centro
        #centro = client_repository.factory.create('ns2:NamedValue')
	#centro.name = 'pfc:centro'
	#centro.value = p.centro
	#centro.isMultiValue = False
	#addAspectpfc.property.append(centro)	
	##metadato pfc:titulacion
        #titulacion = client_repository.factory.create('ns2:NamedValue')
	#titulacion.name = 'pfc:titulacion'
	#titulacion.value = p.titulacion
	#titulacion.isMultiValue = False
	#addAspectpfc.property.append(titulacion)	
	##metadato pfc:niu
        #niu = client_repository.factory.create('ns2:NamedValue')
	#niu.name = 'pfc:niu'
	#niu.value = p.niu
	#niu.isMultiValue = False
	#addAspectpfc.property.append(niu)	
        ##metadato pfc:tutor
        #tutor = client_repository.factory.create('ns2:NamedValue')
	#tutor.name = 'pfc:tutor'
	#tutor.value = p.tutor
	#tutor.isMultiValue = False
	#addAspectpfc.property.append(tutor)	
    
        #print addAspectpfc
        #cml.addAspect.append (addAspectpfc)
        
        ##ASPECTO DUBLIN CORE
        #addAspectdc = client_repository.factory.create('ns0:addAspect')
	#print addAspectdc
	#addAspectdc.aspect = '{http://www.ull.es/2010/06/28/pfc.xsd}dublin'
	#addAspectdc.where_id = '1'
	##metadato dublin title
        #title = client_repository.factory.create('ns2:NamedValue')
	#title.name = 'pfc:title'
	#title.value = p.title
	#title.isMultiValue = False
	#addAspectdc.property.append(title)
	##metadato dublin creator
	#creator = client_repository.factory.create('ns2:NamedValue')
	#creator.name = 'pfc:creator'
	#creator.value = p.creator
	#creator.isMultiValue = False
	#addAspectdc.property.append(creator)
	##metadato dublin description
	#description = client_repository.factory.create('ns2:NamedValue')
	#description.name = 'pfc:description'
	#description.value = p.description
	#description.isMultiValue = False
	#addAspectdc.property.append(description)
	##metadato dublin language
        #language = client_repository.factory.create('ns2:NamedValue')
	#language.name = 'pfc:language'
	#language.value = p.language
	#language.isMultiValue = False
	#addAspectdc.property.append(language)
    
        #print addAspectdc
        #cml.addAspect.append (addAspectdc)
    
    
	results = client_repository.service.update(cml)    
	print results
	
	url = ALFRESCO_URL_PUT + results[1].destination.uuid + '/' + f.name + '?ticket=' + self.ticket
        #url = 'http://127.0.0.1:8080/alfresco/upload/workspace/SpacesStore/' + results[0].destination.uuid + self.ticket
        #url = 'http://localhost:8080/alfresco/upload/test.pdf?ticket=' + login_res['ticket']
        print url
        put.putfile(f, url)
        return results[0].destination.uuid
        
    def addMetadata (self, p):
      	d = dict(http='localhost:1080')
	client_repository = Client(ALFRESCO_URL_RESPOSITORY_SERVICE, proxy= d)
	client_repository.set_options(wsse=self.security)
	cml = client_repository.factory.create('ns0:CML')
	addAspectpfc = client_repository.factory.create('ns0:addAspect')
	#print addAspectpfc
	addAspectpfc.aspect = '{http://www.ull.es/2010/06/28/pfc.xsd}metadatosTFC'
	predicate = client_repository.factory.create('ns2:Predicate')
	reference = client_repository.factory.create('ns2:Reference')
	store = client_repository.factory.create('ns2:Store')
	store.scheme = 'workspace'
	store.address = 'SpacesStore'
	reference.uuid = p.uuid
	reference.store = store
	#node.reference = reference
	predicate.nodes = reference
	addAspectpfc.where = predicate
	#metadato pfc:centro
        centro = client_repository.factory.create('ns2:NamedValue')
	centro.name = 'pfc:centro'
	centro.value = p.centro
	centro.isMultiValue = False
	addAspectpfc.property.append(centro)	
	#metadato pfc:titulacion
        titulacion = client_repository.factory.create('ns2:NamedValue')
	titulacion.name = 'pfc:titulacion'
	titulacion.value = p.titulacion
	titulacion.isMultiValue = False
	addAspectpfc.property.append(titulacion)	
	#metadato pfc:niu
        niu = client_repository.factory.create('ns2:NamedValue')
	niu.name = 'pfc:niu'
	niu.value = p.niu
	niu.isMultiValue = False
	addAspectpfc.property.append(niu)	
        #metadato pfc:tutor
        tutor = client_repository.factory.create('ns2:NamedValue')
	tutor.name = 'pfc:tutor'
	tutor.value = p.tutor
	tutor.isMultiValue = False
	addAspectpfc.property.append(tutor)
	#metadato pfc:calificacion
        calificacion = client_repository.factory.create('ns2:NamedValue')
	calificacion.name = 'pfc:calificacion'
	calificacion.value = p.calificacion
	calificacion.isMultiValue = False
	addAspectpfc.property.append(calificacion)
	#metadatos pfc:fechaLectura
        fecha = client_repository.factory.create('ns2:NamedValue')
	fecha.name = 'pfc:fechaLectura'
	fecha.value = p.fecha
	fecha.isMultiValue = False
	addAspectpfc.property.append(fecha)	
	#metadatos pfc:presidente
        presidente = client_repository.factory.create('ns2:NamedValue')
	presidente.name = 'pfc:presidenteTribunal'
	presidente.value = p.tribunal_presidente
	presidente.isMultiValue = False
	addAspectpfc.property.append(presidente)
	#metadatos pfc:secretario
        secretario = client_repository.factory.create('ns2:NamedValue')
	secretario.name = 'pfc:secretarioTribunal'
	secretario.value = p.tribunal_secretario
	secretario.isMultiValue = False
	addAspectpfc.property.append(secretario)
	#metadatos pfc:vocales
        vocales = client_repository.factory.create('ns2:NamedValue')
	vocales.name = 'pfc:vocales'
	vocales.value = p.tribunal_vocal
	#secretario.isMultiValue = False
	addAspectpfc.property.append(vocales)
	
	cml.addAspect.append (addAspectpfc)
	
	addAspectdc = client_repository.factory.create('ns0:addAspect')
	#print addAspectdc
	addAspectdc.aspect = '{http://www.ull.es/2010/06/28/pfc.xsd}dublin'
	predicate = client_repository.factory.create('ns2:Predicate')
	reference = client_repository.factory.create('ns2:Reference')
	store = client_repository.factory.create('ns2:Store')
	store.scheme = 'workspace'
	store.address = 'SpacesStore'
	reference.uuid = p.uuid
	reference.store = store
	#node.reference = reference
	predicate.nodes = reference
	addAspectdc.where = predicate
        title = client_repository.factory.create('ns2:NamedValue')
	title.name = 'pfc:title'
	title.value = p.title
	title.isMultiValue = False
	addAspectdc.property.append(title)
	#metadato dublin creator
	creator = client_repository.factory.create('ns2:NamedValue')
	creator.name = 'pfc:creator'
	creator.value = p.creator
	creator.isMultiValue = False
	addAspectdc.property.append(creator)
	#metadato dublin description
	description = client_repository.factory.create('ns2:NamedValue')
	description.name = 'pfc:description'
	description.value = p.description
	description.isMultiValue = False
	addAspectdc.property.append(description)
	#metadato dublin language
        language = client_repository.factory.create('ns2:NamedValue')
	language.name = 'pfc:language'
	language.value = p.language
	language.isMultiValue = False
	addAspectdc.property.append(language)
	#metadato dublin coverage
        #coverage = client_repository.factory.create('ns2:NamedValue')
	#coverage.name = 'pfc:coverage'
	#coverage.value = p.language
	#coverage.isMultiValue = False
	#addAspectdc.property.append(coverage)	
        #subject = client_repository.factory.create('ns2:NamedValue')
	#subject.name = 'pfc:subject'
	#coverage.value = p.subject
	#coverage.isMultiValue = False
	#addAspectdc.property.append(coverage)	
        #rigths = client_repository.factory.create('ns2:NamedValue')
	#rights.name = 'pfc:rights'
	#rights.value = p.rights
	#rights.isMultiValue = False
	#addAspectdc.property.append(rigths)		
	
	cml.addAspect.append (addAspectdc)
	
	
	results = client_repository.service.update(cml) 
	
        
    def url_bajar_pfc (self, uuid):
	#return 'http://127.0.0.1:8080/alfresco/download/attach/workspace/SpacesStore/' + uuid + '/myfile.pdf?alf_ticket=' + self.ticket
	return ALFRESCO_URL_DOWN + uuid + '/myfile.pdf?ticket=' + self.ticket
	
	
    def terminar_sesion (self):
        self.client.service.endSession(self.ticket)