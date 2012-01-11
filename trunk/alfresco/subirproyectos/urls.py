from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.views.generic.simple import redirect_to

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
    url(r'^/(?P<id>\d+)/mostrar/$', 'mostrar'),
    url(r'^/(?P<id>\d+)/$', redirect_to, {'url': '/%(id)s/mostrar'}),
    url(r'^/solicitar_defensa/$', 'solicitar_defensa'),
    url(r'^/mostrarlistatutor/$', 'mostrarlistatutor'),
    url(r'^/mostrarlistabiblioteca/$', 'mostrarlistabiblioteca'),
    url(r'^/(?P<id>\d+)/archivar_proyecto_biblioteca/$', 'archivar_proyecto_biblioteca'),
    url(r'^/(?P<id>\d+)/calificar_proyecto_tutor/$', 'calificar_proyecto_tutor'),
    url(r'^/revisar/$', 'revisar'),
    url(r'^/rechazar/$', 'rechazar'),
)
