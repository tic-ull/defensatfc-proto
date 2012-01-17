# -*- coding: utf-8 -*-

from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from subirproyectos import settings, models, validators


class FormularioProyecto(forms.ModelForm):
    # TODO: En clean hay que comprobar que si intrduce el nombre o el apellido
    # del director hay que introducir también el otro.

    DOMINIO_CORREO_TUTOR = '@' + settings.DOMINIO_CORREO_TUTOR

    centro = forms.ModelChoiceField(label="Centro", queryset=models.Centro.objects)
    titulacion = forms.ModelChoiceField(label="Titulación", queryset=models.Titulacion.objects)
    file = forms.FileField(label="Documento de la memoria", validators=[validators.file_format])

    # Sobreescribimos el campo 'tutor_email' para que la comprobación de
    # correo electrónico valido no se haga en el campo del formulario (antes
    # de clean_tutor_email) sino en el campo del modelo
    # (después de clean_tutor_email)
    tutor_email = forms.CharField(max_length=(50 - len(DOMINIO_CORREO_TUTOR)),
                                  label='Correo electrónico del tutor')

    class Meta:
	model = models.Proyecto
	fields = ('title', 'description', 'language', 'file', 'creator_nombre',
            'creator_apellidos', 'niu', 'centro', 'titulacion', 'tutor_nombre',
            'tutor_apellidos', 'tutor_email', 'director_nombre', 'director_apellidos')
        widgets = {
            'title': forms.Textarea(attrs={'cols': 40, 'rows': 3}),
        }

    def append_field_error(self, field, error):
        if field not in self._errors:
            self._errors[field] = forms.util.ErrorList()
	self._errors[field].append(error)

    def append_non_field_error(self, error):
        self.set_error(forms.NON_FIELD_ERRORS, error)

    def clean_tutor_email(self):
        return self.cleaned_data['tutor_email'] + self.DOMINIO_CORREO_TUTOR


class FormularioAnexoFormset(BaseInlineFormSet):

    def add_fields(self, form, index):
	super(FormularioAnexoFormset, self).add_fields(form, index)
	form.fields["file"] = forms.FileField(validators=[validators.file_format])
        form.fields['title'].widget = forms.Textarea(attrs={'cols': 40, 'rows': 3})

AnexoFormSet = inlineformset_factory(models.Proyecto, models.Anexo,
	formset = FormularioAnexoFormset,
        fields = ('title', 'description', 'language', 'type' ),
	extra = 0)


class FormularioAutorizar(forms.ModelForm):
    comentario = forms.CharField(label="Comentario", max_length=500, required=False,
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 5}))

    class Meta:
        model = models.Proyecto
        fields = ('tutor_nombre', 'tutor_apellidos', 'director_nombre', 'director_apellidos')


class FormularioProyectoCalificado(forms.ModelForm):

    class Meta:
	model = models.ProyectoCalificado
	fields = ('fecha_defensa',  'calificacion_numerica', 'modalidad', 'tribunal_presidente_nombre', 'tribunal_presidente_apellidos', 
	'tribunal_secretario_nombre', 'tribunal_secretario_apellidos')	
	
VocalesFormSet = inlineformset_factory(models.ProyectoCalificado, models.TribunalVocal, extra=1)    


class FormularioProyectoArchivado(forms.ModelForm):

    class Meta:
	model = models.ProyectoArchivado
	fields = ('title', 'creator_nombre', 'creator_apellidos' ,'description', 'language', 'subject',  'rights', 'coverage')	
	
