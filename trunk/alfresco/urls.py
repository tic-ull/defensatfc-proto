from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'alfresco.views.home', name='home'),
    # url(r'^alfresco/', include('alfresco.foo.urls')),
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/subirproyectos/'}),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'subirproyectos/login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^subirproyectos', include('subirproyectos.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
