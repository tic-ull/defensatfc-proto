# -*- encoding: utf-8 -*-
from django.core.validators import RegexValidator
from subirproyectos.settings import *
from django.core.exceptions import ValidationError



import mimetypes

from subirproyectos import settings

NIUValidator = RegexValidator(regex ='\d{10}', message='Ej: 0100353303')


      
def file_format(value):
    (format, encoding) = mimetypes.guess_type(value.name)
    formats = [mimetype for mimetype, name in SELECCION_FORMATO]
    if format not in formats:
        raise ValidationError('Formato de fichero no válido')
      
UUIDValidator = RegexValidator(regex ='\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', message='Ej: 550e8400-e29b-41d4-a716-446655440000 ')

EmailAluValidator = RegexValidator(regex ='\w+' + DOMINIO_CORREO_ALU, message='Solo se admiten correos ULL')

EmailTutorValidator = RegexValidator(regex ='\w+' + DOMINIO_CORREO_TUTOR, message='Solo se admiten correos ULL')
 