from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
form django.views.defaults import page_not_found

from defensa import models

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('defensa.views',
    url(r'^/$', 'index'),
    url(r'^/titulacion/find-by-centro/$', 'filter', {
        'model_class': models.Titulacion,
        'field_name': 'centro',
    }),
    url(r'^/solicitar/$', 'solicitar_defensa'),
    url(r'^/(?P<id>\d+)/$', 'solicitud_mostrar', name='proyecto_view'),
    url(r'^/(?P<id>\d+)/contenido/$', 'descargar_proyecto'),
    url(r'^/(?P<id>\d+)/anexo/(?P<anexo_id>\d+)/', page_not_found, name='anexo_view'),
    url(r'^/(?P<id>\d+)/anexo/(?P<anexo_id>\d+)/contenido/$', 'descargar_anexo'),
    url(r'^/(?P<id>\d+)/autorizar/$', 'autorizar_defensa'),
    url(r'^/(?P<id>\d+)/autorizacion/$', 'descargar_autorizacion'),
    url(r'^/(?P<id>\d+)/calificar/$', 'calificar_proyecto'),
    url(r'^/(?P<id>\d+)/archivar/$', 'archivar_proyecto'),
    url(r'^/autorizar/$', 'lista_autorizar'),
    url(r'^/calificar/$', 'lista_calificar'),
    url(r'^/archivar/$', 'lista_archivar'),
)
