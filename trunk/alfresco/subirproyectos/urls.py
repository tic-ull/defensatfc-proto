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
    url(r'^/proyecto/search-for-solicitado/$',
        'buscar_proyectos_solicitados', {
            'where_search': (
                'title', 'creator_nombre', 'creator_apellidos', 'niu',
    )}),
    url(r'^/proyecto/search-for-autorizados/$',
        'buscar_proyectos_autorizados', {
            'where_search': (
                'title', 'creator_nombre', 'creator_apellidos', 'niu',
    )}),
    url(r'^/proyecto/search-for-calificados/$',
        'buscar_proyectos_calificados', {
            'where_search': (
                'title', 'creator_nombre', 'creator_apellidos', 'niu',
    )}),
    url(r'^/solicitar/$', 'solicitar_defensa'),
    url(r'^/(?P<id>\d+)/$', 'solicitud_mostrar', name='proyecto_view'),
    url(r'^/(?P<id>\d+)/contenido/$', 'descargar_contenido'),
    url(r'^/(?P<id>\d+)/anexo/(?P<anexo_id>\d+)/$', 'descargar_anexo', name='anexo_view'),
    url(r'^/(?P<id>\d+)/autorizar/$', 'autorizar_defensa'),
    url(r'^/(?P<id>\d+)/calificar/$', 'calificar_proyecto'),
    url(r'^/(?P<id>\d+)/archivar/$', 'archivar_proyecto'),
#    url(r'^/autorizar/$', 'lista_autorizar'),
#    url(r'^/calificar/$', 'lista_calificar'),
#    url(r'^/archivar/$', 'listar_archivar'),
)
