from django import forms
from django.forms.formsets import BaseFormSet 
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from subirproyectos.settings import *
from subirproyectos.models import *
from subirproyectos import validators


class FormularioProyecto(forms.ModelForm):
    file = forms.FileField(label="Documento de la memoria", validators=[validators.file_format])
    
    class Meta:
	model = Proyecto
	exclude = ('estado', 'creator_email', 'type', 'format', 'alfresco_uuid')

    def __init__(self, *args, **kwargs):
	if 'user' in kwargs:
	    self.user = kwargs['user']
	    del kwargs['user']
	else:
	    self.user = None
	super(FormularioProyecto, self).__init__(*args, **kwargs)

    def append_field_error(self, field, error):
        if field not in self._errors:
            self._errors[field] = forms.util.ErrorList()
	self._errors[field].append(error)

    def append_non_field_error(self, error):
        self.set_error(forms.NON_FIELD_ERRORS, error)

    def clean_niu(self):
	if self.user is not None:
	    niu = self.user.niu()
	    if niu is not None and not niu == self.cleaned_data['niu']:
		raise forms.ValidationError('El NIU no parece corresponder al usuario')
	return self.cleaned_data['niu']


class FormularioAnexoFormset (BaseInlineFormSet):
    def add_fields(self, form, index):
	super(FormularioAnexoFormset, self).add_fields(form, index)
	form.fields["file"] = forms.FileField(validators=[validators.file_format])

AnexoFormSet = inlineformset_factory(Proyecto, Anexo,
	formset = FormularioAnexoFormset,
	exclude = ('format', 'relation', 'titulacion', 'alfresco_uuid'),
	extra = 0,
    )


class FormularioProyectoCalificado(forms.ModelForm):
  class Meta:
	model = ProyectoCalificado
	fields = ('fecha_defensa',  'calificacion_numerica', 'modalidad', 'tribunal_presidente_nombre', 'tribunal_presidente_apellidos', 
	'tribunal_secretario_nombre', 'tribunal_secretario_apellidos')	
	
VocalesFormSet = inlineformset_factory(ProyectoCalificado, TribunalVocal)    

class FormularioProyectoArchivado(forms.ModelForm):
  class Meta:
	model = ProyectoArchivado
	fields = ('title', 'creator_nombre', 'creator_apellidos' ,'description', 'language', 'subject',  'rights', 'coverage')	
	
	
class FormularioLogin(forms.Form):
  username = forms.CharField(max_length=50)
  password = forms.CharField(widget=forms.PasswordInput()) 
  
  
  
  

