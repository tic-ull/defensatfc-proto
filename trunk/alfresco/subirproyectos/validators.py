# -*- encoding: utf-8 -*-

import mimetypes
import re

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from subirproyectos import settings

 
def file_format(value):
    (format, encoding) = mimetypes.guess_type(value.name)
    formats = [mimetype for mimetype, name in settings.SELECCION_FORMATO]
    if format not in formats:
        raise ValidationError('Formato de fichero no válido')

      
NIUValidator = RegexValidator(regex ='^\d{10}$', message='Ej: 0100353303')

UUIDValidator = RegexValidator(regex ='^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$',
    message='Ej: 550e8400-e29b-41d4-a716-446655440000 ')

EmailCreatorValidator = RegexValidator(regex='^\w+@(%s)|(%s)$ ' % (
        re.escape(settings.DOMINIO_CORREO_ALUMNO),
        re.escape(settings.DOMINIO_CORREO_TUTOR)
    ),
    message='Solo se admiten correos ULL')

EmailTutorValidator = RegexValidator(regex='^\w+@%s$' %
    re.escape(settings.DOMINIO_CORREO_TUTOR),
    message='Solo se admiten correos ULL')
