from django import forms
from django.forms.formsets import BaseFormSet 
from subirproyectos.settings import *


class FormularioProyecto(forms.Form):
    title = forms.CharField(max_length=50)    
    creator = forms.CharField(max_length=200)
    description = forms.CharField(max_length=500)
    #type = models.CharField(max_length=200)
    #format = models.CharField(max_length=200)
    language = forms.CharField(max_length=200)
    #relation = models.CharField(max_length=500)
    niu = forms.CharField(max_length=15)
    tutor = forms.CharField(max_length=200)
    #centro = forms.CharField(max_length=200)
    centro = forms.ChoiceField(choices=CENTRO)
    titulacion = forms.ChoiceField(choices=TITULACION)
    #universidad = forms.CharField(max_length=200)
    file  = forms.FileField()
    
    
class FormularioAnexo(forms.Form):
    title = forms.CharField(max_length=50) 
    file  = forms.FileField()
    
class FormularioAnexoFormset (BaseFormSet):
    def add_fields(self, form, index):
	super(FormularioAnexoFormset, self).add_fields(form, index)
	form.fields["file"] = forms.FileField()

    

class FormularioLogin(forms.Form):
  username = forms.CharField(max_length=50)
  password = forms.CharField(widget=forms.PasswordInput()) 
