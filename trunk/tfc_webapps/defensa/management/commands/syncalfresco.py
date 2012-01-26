# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from defensa import settings, models
from defensa.alfresco import *

class Command(NoArgsCommand):
    help = 'Sincroniza los centros y titulaciones de la BD con los centros y titulaciones de Alfresco'

    def handle(self, *args, **options):
        centros = models.Centro.objects.filter(alfresco_uuid = "").order_by('nombre')
        if centros.count() == 0:
            return

	cml = Alfresco().cml()
	num_centros = 0
	for centro in centros:
            def create_callback(result):
                centro.alfresco_uuid = result.destination.uuid
                centro.save()
                num_centros = num_centros + 1
	    properties_centro = centro.get_alfresco_properties()
	    cml.create (settings.ALFRESCO_PFC_FOLDER_UUID,
                        settings.ALFRESCO_PFC_MODEL_NAMESPACE % "centro",
                        properties_centro, create_callback)
	cml.do()

	cml = Alfresco().cml()
	num_titulaciones = 0
	titulaciones = centro.titulacion_set.filter(alfresco_uuid = "").order_by('nombre')
	for titulacion in titulaciones:
            def create_callback(result):
                titulacion.alfresco_uuid = result.destination.uuid
                titulacion.save()
                num_titulaciones = num_titulaciones + 1
	    properties_titulacion = titulacion.get_alfresco_properties()
	    cml.create (titulacion.centro.alfresco_uuid,
                        ALFRESCO_PFC_MODEL_NAMESPACE % "titulacion",
                        properties_titulacion, create_callback)
	cml.do()

	self.stdout.write('Se han actualizado %s centros\n' % num_centros)
	self.stdout.write('Se han actualizado %s titulaciones\n' % num_titulaciones)

