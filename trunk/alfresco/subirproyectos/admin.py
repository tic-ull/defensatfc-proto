from subirproyectos.models import Proyecto, Anexo, Centro, Titulacion, ProyectoCalificado, ProyectoArchivado
from django.contrib import admin


admin.site.register(Proyecto)
admin.site.register(Anexo)
admin.site.register(Centro)
admin.site.register(Titulacion)
admin.site.register(ProyectoCalificado)
admin.site.register(ProyectoArchivado)