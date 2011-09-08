from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('subirproyectos.views',
    (r'^/$', 'index'),
    (r'^/results/$', 'result'),
    (r'^/formulario/$', 'formulario'),
    (r'^/subir/$', 'subir'),
    (r'^/login/$', 'login'),
    #(r'^/logout_view/$', 'logout_view'),
    (r'^/(?P<id>\d+)/mostrar/$', 'mostrar'),
    (r'^/mostrarlistatutor/$', 'mostrarlistatutor'),
    (r'^/mostrarlistabiblioteca/$', 'mostrarlistabiblioteca'),
    (r'^/validar_biblioteca/$', 'validar_biblioteca'),
    (r'^/validar_tutor/$', 'validar_tutor'),
    (r'^/validar/$', 'validar'),
    (r'^/rechazar/$', 'rechazar'),
    
    
    #(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'subirproyectos/index.html'}),


)