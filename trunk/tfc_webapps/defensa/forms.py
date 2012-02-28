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
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms.models import modelformset_factory

from defensa import settings, models
from defensa.validators import FileFormatValidator


def validar_calificacion(calificacion_numerica, calificacion):
    """Comprobar calificación y nota numérica.

    Función para validar de forma conjunta la calificación y la nota numérica.
    Está en una función a parte para utilizarla tanto desde las vistas como
    desde la interfaz administrativa.
    """
    
    if float(calificacion_numerica) >= 0.0 and float(calificacion_numerica) <= 4.9:
        if calificacion != 'SS':
            return False
    if float(calificacion_numerica) >= 5.0 and float(calificacion_numerica) <= 6.9:
        if calificacion != 'AP':
            return False
    if float(calificacion_numerica) >= 7.0 and float(calificacion_numerica) <= 8.9:
        if calificacion != 'NT':
            return False
    if float(calificacion_numerica) >= 9.0 and float(calificacion_numerica) <= 10.0:
        if calificacion not in ('SB', 'MH'):
            return False

    return True


class FormularioTrabajoBase(forms.ModelForm):
    """Clase base para los formularios de trabajos fin de carrera.

    Esta clase base incluye elementos compartidos tanto por FormularioSolicitud
    utilizado en las vistas como en el formulario TrabajoAdminForm vinculado
    al modelo Trabajo de la interfaz administrativa .
    """

    def append_field_error(self, field, error):
        if field not in self._errors:
            self._errors[field] = forms.util.ErrorList()
        self._errors[field].append(error)

    def append_non_field_error(self, error):
        self.set_error(forms.NON_FIELD_ERRORS, error)

    def clean(self):
        director_apellidos = self.cleaned_data.get('director_apellidos')
        director_nombre = self.cleaned_data.get('director_director')

        # comprobar nombre y apellidos del director
        if director_apellidos and not director_nombre:
            self.append_field_error('director_nombre', u"""
                Si desea indicar un director debe proporcionar tanto el
                nombre como los apellidos.""")
        if director_nombre and not director_apellidos:
            self.append_field_error('director_apellidos', u"""
                Si desea indicar un director debe proporcionar tanto el
                nombre como los apellidos.""")

        return self.cleaned_data


class FormularioSolicitud(FormularioTrabajoBase):
    """Formulario de solicitud de defensa de TFC."""
    
    DOMINIO_CORREO_TUTOR = '@' + settings.DOMINIO_CORREO_TUTOR

    centro = forms.ModelChoiceField(label=u"Centro", queryset=models.Centro.objects)
    titulacion = forms.ModelChoiceField(label=u"Titulación", queryset=models.Titulacion.objects)

    file = forms.FileField(label=u"Documento de la memoria", required=False)
    filename = forms.CharField(widget=forms.HiddenInput, required=False)
    fileid = forms.IntegerField(widget=forms.HiddenInput, required=False)

    # Sobreescribimos el campo 'tutor_email' para que la comprobación de
    # correo electrónico valido no se haga en el campo del formulario (antes
    # de clean_tutor_email) sino en el campo del modelo
    # (después de clean_tutor_email)
    tutor_email = forms.CharField(max_length=(50 - len(DOMINIO_CORREO_TUTOR)),
                                  label=u'Correo electrónico del tutor')

    class Meta:
        model = models.Trabajo
        # El orden es importante
        fields = ('title', 'description', 'language', 'creator_nombre',
            'creator_apellidos', 'niu', 'centro', 'titulacion', 'tutor_nombre',
            'tutor_apellidos', 'tutor_email', 'director_nombre', 'director_apellidos',
            'filename', 'fileid', 'file') 
        widgets = {
            'title': forms.Textarea(attrs={'cols': 40, 'rows': 3}),
        }

    def clean_tutor_email(self):
        return self.cleaned_data['tutor_email'] + self.DOMINIO_CORREO_TUTOR

    def clean_file(self):
        fileobj = self.cleaned_data.get('file')
        fileid = self.cleaned_data.get('fileid')

        tipo = settings.MEMORIA_TFC_TIPO_DOCUMENTO
        if fileid:
            try:
                submitted = models.SubmittedFile.objects.get(id=fileid)
            except models.SubmittedFile.DoesNotExist:
                raise ValidationError(u"Este campo es obligatorio.")
            else:
                FileFormatValidator(submitted, settings.TIPO_DOCUMENTO_TO_FORMATO[tipo])
        elif fileobj:
            FileFormatValidator(fileobj, settings.TIPO_DOCUMENTO_TO_FORMATO[tipo])
            submitted = models.submittedfile_factory(fileobj)
            submitted.save()

            self.data['filename'] = submitted.name
            self.data['fileid'] = submitted.id
        else:
            raise ValidationError(u"Este campo es obligatorio.")

        return submitted


class FormularioTrabajo(forms.ModelForm):
    """Formulario para editar los metadatos del trabajo fin de carrera."""

    class Meta:
        model = models.Trabajo
        fields = ('title', 'description', 'language')
        widgets = {
            'title': forms.Textarea(attrs={'cols': 40, 'rows': 3}),
        }


class FormularioAnexo(forms.ModelForm):
    """Formulario para editar los metadatos del anexo."""

    title = forms.CharField(label=u"Título",
        widget=forms.Textarea(attrs={'cols': 40, 'rows': 3}))

    class Meta:
        model = models.Anexo
        fields = ('title', 'description', 'language', 'type')

    def clean_type(self):
        data = self.cleaned_data.get('type')

        formatos = settings.TIPO_DOCUMENTO_TO_FORMATO[data['type']]
        FileFormatValidator(self.instance.format, formatos)

        return data


class FormularioSolicitudAnexo(forms.ModelForm):
    """Formulario de anexo adjunto durante la solicitud de defensa del TFC."""

    title = forms.CharField(label=u"Título",
        widget=forms.Textarea(attrs={'cols': 40, 'rows': 3}))

    file = forms.FileField(label=u"Documento del anexo", required=False)
    filename = forms.CharField(widget=forms.HiddenInput, required=False)
    fileid = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = models.Anexo
        # El orden es importante
        fields = ('title', 'description', 'language', 'type', 'filename', 'fileid', 'file')

    def clean_file(self):
        fileobj = self.cleaned_data.get('file')
        fileid = self.cleaned_data.get('fileid')
        tipo = self.cleaned_data.get('type')

        if fileid:
            try:
                submitted = models.SubmittedFile.objects.get(id=fileid)
            except models.SubmittedFile.DoesNotExist:
                raise ValidationError(u"Este campo es obligatorio.")
            else:
                if tipo:
                    formatos = settings.TIPO_DOCUMENTO_TO_FORMATO[tipo]
                    FileFormatValidator(submitted, formatos)
        elif fileobj:
            if tipo:
                formatos = settings.TIPO_DOCUMENTO_TO_FORMATO[tipo]
                FileFormatValidator(fileobj, formatos)

            submitted = models.submittedfile_factory(fileobj)
            submitted.save()

            self.data[self.prefix + '-filename'] = submitted.name
            self.data[self.prefix + '-fileid'] = submitted.id
        else:
            raise ValidationError(u"Este campo es obligatorio.")

        return submitted


AnexoFormSet = inlineformset_factory(models.Trabajo, models.Anexo,
	form = FormularioSolicitudAnexo,
	extra = 0)


class FormularioAutorizar(forms.ModelForm):
    """Formulario de autorización de la defensa de un TFC."""
    
    comentario = forms.CharField(label="Comentario", max_length=500, required=False,
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 5}))

    class Meta:
        model = models.Trabajo
        fields = ('tutor_nombre', 'tutor_apellidos', 'director_nombre',
            'director_apellidos')


class FormularioCalificar(forms.ModelForm):
    """Formulario para calificar la defensa de un TFC."""
    
    def __init__(self, *args, **kwargs):
	super(FormularioCalificar, self).__init__(*args, **kwargs)
        self.fields['fecha_defensa'].required = True
        self.fields['calificacion_numerica'].required = True
        self.fields['calificacion'].required = True
        self.fields['tribunal_presidente_nombre'].required = True
        self.fields['tribunal_presidente_apellidos'].required = True
        self.fields['tribunal_secretario_nombre'].required = True
        self.fields['tribunal_secretario_apellidos'].required = True

    class Meta:
	model = models.Trabajo
	fields = ('fecha_defensa', 'calificacion_numerica', 'calificacion',
            'tribunal_presidente_nombre', 'tribunal_presidente_apellidos',
            'tribunal_secretario_nombre', 'tribunal_secretario_apellidos')

    def clean(self):
        data = super(FormularioCalificar, self).clean()

        if not validar_calificacion(data['calificacion_numerica'], data['calificacion']):
            self.append_field_error('calificacion',
                u"La calificación y la nota numérica no coinciden")

        return data

VocalesFormSet = inlineformset_factory(models.Trabajo, models.TribunalVocal, extra=1)    


class FormularioArchivar(forms.ModelForm):
    """Formulario para archivar un TFC."""
    
    def __init__(self, *args, **kwargs):
	super(FormularioArchivar, self).__init__(*args, **kwargs)
        self.fields['rights'].required = True      
        self.fields['coverage'].required = True    
        self.fields['subject'].required = True               

    class Meta:
	model = models.Trabajo
	fields = ('subject',  'rights', 'coverage')
