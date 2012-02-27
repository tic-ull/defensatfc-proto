# -*- coding: utf-8 -*-
#  Gestión de Trabajos Fin de Carrera de la Universidad de La Laguna
#
#    Copyright (C) 2011-2012 Pedro Cabrera <pdrcabrod@gmail.com>
#                            Jesús Torres  <jmtorres@ull.es>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from django import forms
from django.contrib import admin

from defensa import models
from defensa import forms
from defensa.forms import validar_calificacion


class TrabajoAdminForm(forms.FormularioTrabajoBase):
    class Meta:
        model = models.Trabajo

    def clean(self):
	data = super(TrabajoAdminForm, self).clean()
	
	# campos requeridos según el estado
	if 'estado' in data:
            error = u"Este campo es obligatorio."
            required_fields = []
            if  data['estado'] in ('calificado', 'archivado') :
                required_fields += ("fecha_defensa", "modalidad",
                    "tribunal_presidente_nombre",
                    "tribunal_presidente_apellidos", "tribunal_secretario_nombre",
                    "tribunal_secretario_apellidos")

                if not data['calificacion_numerica']:
                    self.append_field_error('calificacion_numerica', error)
                elif not data['calificacion']:
                    self.append_field_error('calificacion', error)
                elif not validar_calificacion(data['calificacion_numerica'], data['calificacion']):
                    self.append_field_error('calificacion',
                        u"La calificación y la nota numérica no coinciden")

            if data['estado'] == 'archivado':
                required_fields += ("subject", "rights", "coverage")

            for field in required_fields:
                data[field] or self.append_field_error(field, error)

        return data


class TribunalVocalInline(admin.TabularInline):
    model = models.TribunalVocal
    verbose_name = "Vocal tribunal"
    verbose_name_plural = "Vocales tribunal"


class TrabajoAdmin(admin.ModelAdmin):
    form = TrabajoAdminForm
    inlines = [TribunalVocalInline,]

admin.site.register(models.Trabajo, TrabajoAdmin)

admin.site.register(models.Anexo)
admin.site.register(models.Centro)
admin.site.register(models.Titulacion)
admin.site.register(models.AdscripcionUsuarioCentro) 
admin.site.register(models.TribunalVocal)
