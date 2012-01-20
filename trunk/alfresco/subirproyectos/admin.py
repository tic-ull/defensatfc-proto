from subirproyectos import models
from django.contrib import admin


admin.site.register(models.Proyecto)
admin.site.register(models.Anexo)
admin.site.register(models.Centro)
admin.site.register(models.Titulacion)
admin.site.register(models.ProyectoCalificado)
admin.site.register(models.ProyectoArchivado)
admin.site.register(models.AdscripcionUsuarioCentro)