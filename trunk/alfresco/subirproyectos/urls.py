from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('subirproyectos.views',
    (r'^/$', 'index'),
    (r'^/results/$', 'result'),
    (r'^/solicitar_defensa/$', 'solicitar_defensa'),
    #(r'^/logout_view/$', 'logout_view'),
    (r'^/(?P<id>\d+)/mostrar/$', 'mostrar'),
    (r'^/mostrarlistatutor/$', 'mostrarlistatutor'),
    (r'^/mostrarlistabiblioteca/$', 'mostrarlistabiblioteca'),
    (r'^/(?P<id>\d+)/archivar_proyecto_biblioteca/$', 'archivar_proyecto_biblioteca'),
    (r'^/(?P<id>\d+)/calificar_proyecto_tutor/$', 'calificar_proyecto_tutor'),
    (r'^/revisar/$', 'revisar'),
    (r'^/rechazar/$', 'rechazar'),
)
