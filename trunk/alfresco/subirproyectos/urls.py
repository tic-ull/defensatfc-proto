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
    (r'^/validar_biblioteca/$', 'validar_biblioteca'),
    (r'^/validar_tutor/$', 'validar_tutor'),
    (r'^/validar/$', 'validar'),
    (r'^/rechazar/$', 'rechazar'),
)
