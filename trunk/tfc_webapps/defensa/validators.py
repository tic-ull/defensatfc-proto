# -*- encoding: utf-8 -*-
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

import mimetypes
import re

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from defensa import settings

 
def FileFormatValidator(value, choices):
    (format, encoding) = mimetypes.guess_type(value.name)
    if format not in choices:
        raise ValidationError(u'Formato de fichero no admitido para el tipo de documento.')

      
NIUValidator = RegexValidator(regex ='^\d{10}$', message='Ej: 0100353303')

UUIDValidator = RegexValidator(regex ='^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$',
    message='Ej: 550e8400-e29b-41d4-a716-446655440000 ')

EmailCreatorValidator = RegexValidator(regex='@(%s)|(%s)$ ' % (
        re.escape(settings.DOMINIO_CORREO_ALUMNO),
        re.escape(settings.DOMINIO_CORREO_TUTOR)
    ),
    message='Solo se admiten correos ULL')

EmailTutorValidator = RegexValidator(regex='@%s$' %
    re.escape(settings.DOMINIO_CORREO_TUTOR),
    message='Solo se admiten correos ULL')
