from django import forms
from django.forms.formsets import BaseFormSet 
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from subirproyectos.settings import *
from subirproyectos.models import *
from subirproyectos import validators


#class FormularioProyecto(forms.Form):
    #title = forms.CharField(max_length=50)    
    #creator = forms.CharField(max_length=200)
    #description = forms.CharField(max_length=500)
    ##type = models.CharField(max_length=200)
    ##format = models.CharField(max_length=200)
    #language = forms.CharField(max_length=200)
    ##relation = models.CharField(max_length=500)
    #niu = forms.CharField(max_length=15)
    #tutor = forms.CharField(max_length=200)
    ##centro = forms.CharField(max_length=200)
    #centro = forms.ChoiceField(choices=CENTRO)
    #titulacion = forms.ChoiceField(choices=TITULACION)
    ##universidad = forms.CharField(max_length=200)
    #file  = forms.FileField()
    
    
class FormularioProyecto(forms.ModelForm):
  file = forms.FileField(validators=[validators.file_format])
  #def add_fields(self, form, index):
	#super(FormularioAnexoFormset, self).add_fields(form, index)
	#form.fields["file"] = forms.FileField()  
  class Meta:
	model = Proyecto   
	exclude = ('estado', 'tribunal_vocal', 'tribunal_secretario', 'tribunal_presidente', 'modalidad', 'calificacion', 'fecha', 
	'universidad', 'rights', 'coverage', 'subject', 'relation', 'format', 'type', 'alfresco_uuid')

    
class FormularioAnexoFormset (BaseInlineFormSet):
    def add_fields(self, form, index):
	super(FormularioAnexoFormset, self).add_fields(form, index)
	form.fields["file"] = forms.FileField(validators=[validators.file_format])

AnexoFormSet = inlineformset_factory(Proyecto, Anexo, exclude = ('format', 'relation', 'titulacion', 'alfresco_uuid'), formset = FormularioAnexoFormset)    

class FormularioProyectoCalificado(forms.ModelForm):
  class Meta:
	model = ProyectoCalificado
	fields = ('fecha_defensa',  'calificacion_numerica', 'modalidad', 'tribunal_presidente_nombre', 'tribunal_presidente_apellidos', 
	'tribunal_secretario_nombre', 'tribunal_secretario_apellidos')	
	
VocalesFormSet = inlineformset_factory(ProyectoCalificado, TribunalVocal)    

class FormularioLogin(forms.Form):
  username = forms.CharField(max_length=50)
  password = forms.CharField(widget=forms.PasswordInput()) 
  
  
  
  

