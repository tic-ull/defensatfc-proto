from subirproyectos import models
from django.contrib import admin
from django import forms


#admin.site.register(models.Proyecto)

admin.site.register(models.Anexo)
admin.site.register(models.Centro)
admin.site.register(models.Titulacion)
admin.site.register(models.AdscripcionUsuarioCentro)

class ProyectoAdminForm(forms.ModelForm):
    class Meta:
        model = models.Proyecto   
    def clean(self):
	cleaned_data = self.cleaned_data
        estado = cleaned_data.get("estado")
        #calificar
	fecha_defensa = cleaned_data.get("fecha_defensa")
	calificacion_numerica = cleaned_data.get("calificacion_numerica")
	calificacion = cleaned_data.get("calificacion")
	modalidad = cleaned_data.get("modalidad")
	tribunal_presidente_nombre = cleaned_data.get("tribunal_presidente_nombre")
	tribunal_presidente_apellidos = cleaned_data.get("tribunal_presidente_apellidos")
	tribunal_secretario_nombre = cleaned_data.get("tribunal_secretario_nombre")
	tribunal_secretario_apellidos = cleaned_data.get("tribunal_secretario_apellidos")
	#archivar
	subject = cleaned_data.get("subject")
	rights = cleaned_data.get("rights")
	coverage = cleaned_data.get("coverage")
	
	
	#mensaje de error
        msg = u"Este campo es obligatorio."
        if  estado == 'CAL':
            if fecha_defensa == '':
		self._errors["fecha_defensa"] = self.error_class([msg])
		del cleaned_data["fecha_defensa"]
            if calificacion_numerica == '':
		self._errors["calificacion_numerica"] = self.error_class([msg])
		del cleaned_data["calificacion_numerica"]
            if calificacion == '':
		self._errors["calificacion"] = self.error_class([msg])
		del cleaned_data["calificacion"]
            if modalidad == '':
		self._errors["modalidad"] = self.error_class([msg])
		del cleaned_data["modalidad"]		
            if tribunal_presidente_nombre == '':
		self._errors["tribunal_presidente_nombre"] = self.error_class([msg])
		del cleaned_data["tribunal_presidente_nombre"]		
            if tribunal_presidente_apellidos == '':
		self._errors["tribunal_presidente_apellidos"] = self.error_class([msg])
		del cleaned_data["tribunal_presidente_apellidos"]
            if tribunal_secretario_nombre == '':
		self._errors["tribunal_secretario_nombre"] = self.error_class([msg])
		del cleaned_data["tribunal_secretario_nombre"]	
            if tribunal_secretario_nombre == '':
		self._errors["tribunal_secretario_apellidos"] = self.error_class([msg])
		del cleaned_data["tribunal_secretario_apellidos"]
	elif estado == 'ARC':
            if fecha_defensa == '':
		self._errors["fecha_defensa"] = self.error_class([msg])
		del cleaned_data["fecha_defensa"]
            if calificacion_numerica == '':
		self._errors["calificacion_numerica"] = self.error_class([msg])
		del cleaned_data["calificacion_numerica"]
            if calificacion == '':
		self._errors["calificacion"] = self.error_class([msg])
		del cleaned_data["calificacion"]
            if modalidad == '':
		self._errors["modalidad"] = self.error_class([msg])
		del cleaned_data["modalidad"]		
            if tribunal_presidente_nombre == '':
		self._errors["tribunal_presidente_nombre"] = self.error_class([msg])
		del cleaned_data["tribunal_presidente_nombre"]		
            if tribunal_presidente_apellidos == '':
		self._errors["tribunal_presidente_apellidos"] = self.error_class([msg])
		del cleaned_data["tribunal_presidente_apellidos"]
            if tribunal_secretario_nombre == '':
		self._errors["tribunal_secretario_nombre"] = self.error_class([msg])
		del cleaned_data["tribunal_secretario_nombre"]	
            if tribunal_secretario_nombre == '':
		self._errors["tribunal_secretario_apellidos"] = self.error_class([msg])
		del cleaned_data["tribunal_secretario_apellidos"]	  
            if subject == '':
		self._errors["subject"] = self.error_class([msg])
		del cleaned_data["subject"]
            if rights == '':
		self._errors["rights"] = self.error_class([msg])
		del cleaned_data["rights"]
            if coverage == '':
		self._errors["coverage"] = self.error_class([msg])
		del cleaned_data["coverage"]	  	
        return cleaned_data
        

class ProyectoAdmin(admin.ModelAdmin):
    form = ProyectoAdminForm

admin.site.register(models.Proyecto, ProyectoAdmin)

    
