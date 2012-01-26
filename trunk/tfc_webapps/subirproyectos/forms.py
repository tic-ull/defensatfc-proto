# -*- coding: utf-8 -*-

from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from subirproyectos import settings, models, validators


def calificacion_valida(calificacion_numerica, calificacion):
    # comprobar calificación y nota numérica
    if calificacion_numerica >= 0.0 and calificacion_numerica <= 4.9:
        if calificacion != 'suspenso':
            return False
    if calificacion_numerica >= 5.0 and calificacion_numerica <= 6.9:
        if calificacion != 'aprobado':
            return False
    if calificacion_numerica >= 7.0 and calificacion_numerica <= 8.9:
        if calificacion != 'notable':
            return False
    if calificacion_numerica >= 9.0 and calificacion_numerica <= 10.0:
        if calificacion not in ('sobresaliente', 'matricula'):
            return False

    return True


class FormularioProyectoBase(forms.ModelForm):
    class Meta:
        model = models.Proyecto

    def append_field_error(self, field, error):
        if field not in self._errors:
            self._errors[field] = forms.util.ErrorList()
        self._errors[field].append(error)

    def append_non_field_error(self, error):
        self.set_error(forms.NON_FIELD_ERRORS, error)


class FormularioProyecto(FormularioProyectoBase):
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

    def clean(self):
        data = self.cleaned_data

        # comprobar nombre y apellidos del director
        if data['director_apellidos'] and not data['director_nombre']:
            self.append_field_error('director_nombre', """
                Si desea indicar un director debe proporcionar tanto el
                nombre como los apellidos.""")
        if data['director_nombre'] and not data['director_apellidos']:
            self.append_field_error('director_apellidos', """
                Si desea indicar un director debe proporcionar tanto el
                nombre como los apellidos.""")

        return data

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
        fields = ('tutor_nombre', 'tutor_apellidos', 'director_nombre',
            'director_apellidos')


class FormularioProyectoCalificado(FormularioProyectoBase):
    def __init__(self, *args, **kwargs):
	super(FormularioProyectoCalificado, self).__init__(*args, **kwargs)
        self.fields['fecha_defensa'].required = True
        self.fields['calificacion_numerica'].required = True
        self.fields['calificacion'].required = True
        self.fields['modalidad'].required = True
        self.fields['tribunal_presidente_nombre'].required = True
        self.fields['tribunal_presidente_apellidos'].required = True
        self.fields['tribunal_secretario_nombre'].required = True
        self.fields['tribunal_secretario_apellidos'].required = True

    class Meta:
	model = models.Proyecto
	fields = ('fecha_defensa', 'calificacion_numerica', 'calificacion',
            'modalidad', 'tribunal_presidente_nombre',
            'tribunal_presidente_apellidos', 'tribunal_secretario_nombre',
            'tribunal_secretario_apellidos')

    def clean(self):
        data = self.cleaned_data

        if not calificacion_valida(data['calificacion_numerica'], data['calificacion']):
            self.append_field_error('calificacion',
                u"La calificación y la nota numérica no coinciden")

        return data

VocalesFormSet = inlineformset_factory(models.Proyecto, models.TribunalVocal, extra=1)    


class FormularioProyectoArchivado(forms.ModelForm):
    def __init__(self, *args, **kwargs):
	super(FormularioProyectoArchivado, self).__init__(*args, **kwargs)
	#duda, los que no son nullables?
        self.fields['rights'].required = True      
        self.fields['coverage'].required = True    
        self.fields['subject'].required = True               

    class Meta:
	model = models.Proyecto
	fields = ('title', 'creator_nombre', 'creator_apellidos',
            'description', 'language', 'subject',  'rights', 'coverage')

