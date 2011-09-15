from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^subirproyectos', include('subirproyectos.urls')),
    (r'^admin/', include(admin.site.urls))
    #(r'^subirproyectos/$', 'subirproyectos.views.index'),
    #(r'^subirproyectos/results/$', 'subirproyectos.views.result'),
    #(r'^subirproyectos/formulario/$', 'subirproyectos.views.formulario'),
    #(r'^subirproyectos/subir/$', 'subirproyectos.views.subir'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % settings.MEDIA_URL[1:-1],
         'django.views.static.serve',
         {'document_root':  settings.MEDIA_ROOT, 'show_indexes': False}),
    )
