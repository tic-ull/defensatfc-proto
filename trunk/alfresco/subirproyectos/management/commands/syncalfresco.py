# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from subirproyectos.models import Centro, Titulacion
from subirproyectos.alfresco import *
from subirproyectos.settings import TFC_UUID

class Command(NoArgsCommand):
    help = 'Sincroniza los centros y titulaciones de la BD con los centros y titulaciones de Alfresco'

    def handle(self, *args, **options):
        centros = Centro.objects.filter(alfresco_uuid = "")
        #centros = Centro.objects.all() 
        #TODO si no hay centros, no hacer login en alfresco, añadir type a settings
	cml = Alfresco().cml()
	for centro in centros:
	    properties_centro = {
	    'cm:name': centro.nombre,
	    '{http://www.alfresco.org/model/content/1.0}name' : centro.nombre,
	    'pfc:codigoCentro' : centro.codigo_centro,	  
	    }
	    cml.create (TFC_UUID, "{http://www.ull.es/2011/10/04/pfc.xsd}centro", properties_centro)
	    e = Centro.objects.get(nombre = centro.nombre)
	    titulaciones = e.titulacion_set.filter(alfresco_uuid = "")
	    #for titulacion in titulaciones:
	      #properties_titulacion = {
	    #'cm:name': titulacion.nombre,
	    #'{http://www.alfresco.org/model/content/1.0}name' : titulacion.nombre,
	    #'pfc:codigoPlan' : titulacion.codigo_plan,
	    #'pfc:anyoComienzoPlan' : titulacion.anyo_comienzo_plan,
	    #'pfc:titulacionVigente' : titulacion_vigente	
	     #}
	     #cml.create (TFC_UUID, "{http://www.ull.es/2011/10/04/pfc.xsd}titulacion", properties_titulacion)
	    
	    #centro.alfresco_uuid = results[0].destination.uuid
	    #centro.save()
	results = cml.do()
	cml = Alfresco().cml()
	ncentros = 0
	for centro in centros:
	  centro.alfresco_uuid = results[ncentros].destination.uuid
	  ncentros = ncentros + 1
	  centro.save()
	Centros_totales  = Centro.objects.all() 
	for centro in Centros_totales:  
	  #e = Centro.objects.get(nombre = centro.nombre)
	  titulaciones = centro.titulacion_set.filter(alfresco_uuid = "").order_by('nombre')
	  for titulacion in titulaciones:
	    properties_titulacion = {
	    'cm:name': titulacion.nombre,
	    '{http://www.alfresco.org/model/content/1.0}name' : titulacion.nombre,
	    'pfc:codigoPlan' : titulacion.codigo_plan,
	    'pfc:anyoComienzoPlan' : titulacion.anyo_comienzo_plan,
	    'pfc:titulacionVigente' : titulacion.titulacion_vigente	
	    }
	    cml.create (centro.alfresco_uuid, "{http://www.ull.es/2011/10/04/pfc.xsd}titulacion", properties_titulacion)
	results = cml.do()
	ntitulaciones = 0
        for centro in Centros_totales:
       	  titulaciones = centro.titulacion_set.filter(alfresco_uuid = "")
	  for titulacion in titulaciones:
	    titulacion.alfresco_uuid = results[ntitulaciones].destination.uuid
	    titulacion.save ()
	    ntitulaciones = ntitulaciones + 1
	    
	self.stdout.write('Se han actualizado %s centros\n' % ncentros)
	self.stdout.write('Se han actualizado %s titulaciones\n' % ntitulaciones)
    
	    