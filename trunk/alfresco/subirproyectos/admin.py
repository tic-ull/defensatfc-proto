# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin

from subirproyectos import models
from subirproyectos import forms


class ProyectoAdminForm(forms.FormularioProyectoBase):
    class Meta:
        model = models.Proyecto

    def clean(self):
	data = super(ProyectoAdminForm, self).clean()
	
	# campos requeridos según el estado
	if 'estado' in data:
            error = u"Este campo es obligatorio."
            required_fields = []
            if  data['estado'] in ('calificado', 'archivado') :
                required_fields += ("fecha_defensa", "calificacion_numerica",
                    "calificacion", "modalidad", "tribunal_presidente_nombre",
                    "tribunal_presidente_apellidos", "tribunal_secretario_nombre",
                    "tribunal_secretario_apellidos")

            if data['estado'] == 'archivado':
                required_fields += ("subject", "rights", "coverage")

            for field in required_fields:
                data[field] or self.append_field_error(field, error)

        return data
       

class TribunalVocalInline(admin.TabularInline):
    model = models.TribunalVocal
    verbose_name = "Vocal tribunal"
    verbose_name_plural = "Vocales tribunal"


class ProyectoAdmin(admin.ModelAdmin):
    form = ProyectoAdminForm
    inlines = [TribunalVocalInline,]

admin.site.register(models.Proyecto, ProyectoAdmin)

admin.site.register(models.Anexo)
admin.site.register(models.Centro)
admin.site.register(models.Titulacion)
admin.site.register(models.AdscripcionUsuarioCentro) 
