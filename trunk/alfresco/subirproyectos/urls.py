from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

from subirproyectos import models

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('subirproyectos.views',
    url(r'^/$', 'index'),
    url(r'^/titulacion/find-by-centro/$', 'filter', {
        'model_class': models.Titulacion,
        'field_name': 'centro',
    }),
    url(r'^/solicitar_defensa$', 'solicitar_defensa'),
    url(r'^/(?P<id>\d+)/mostrar$', 'solicitud_mostrar'),
    url(r'^/(?P<id>\d+)/contenido$', 'descargar_contenido'),
    url(r'^/(?P<id>\d+)/anexo/(?P<anexo_id>\d+)$', 'descargar_anexo'),
    url(r'^/(?P<id>\d+)/autorizar$', 'autorizar_defensa'),
    url(r'^/(?P<id>\d+)/calificar$', 'calificar_proyecto'),
    url(r'^/(?P<id>\d+)/archivar$', 'archivar_proyecto'),
    url(r'^/proyectos/autorizar$', 'lista_autorizar'),
    url(r'^/proyectos/calificar$', 'lista_calificar'),
    url(r'^/proyectos/archivar$', 'listar_archivar'),
)
