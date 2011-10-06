# -*- encoding: utf-8 -*-
from django.core.validators import RegexValidator

import mimetypes

from subirproyectos import settings

NIUValidator = RegexValidator(regex ='alu\d{10}', message='Ej: alu0100353303')

def file_format(value):
    format = mimetypes.guess_type(request.FILES['file'].name)
    formats = [mimetype for mimetype, name in SELECCION_FORMATO]
    if format not in formats:
        raise ValidationError('Formato de fichero no válido' % value)
