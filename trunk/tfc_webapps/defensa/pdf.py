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

from django.http import HttpResponse
from django.template import RequestContext, loader

from defensa import settings

from cStringIO import StringIO
from z3c.rml import rml2pdf


def render_to_pdf(template_name, dictionary=None, context_instance=None):

    # Sobreescribir la ruta de los archivos estáticos para que la ruta sea local
    STATIC_URL = getattr(settings, 'PDF_STATIC_URL', None)
    if STATIC_URL:
        if dictionary is None:
            dictionary = {}
        dictionary['STATIC_URL'] = STATIC_URL
    
    # Renderizar la plantilla RML y convertir el contenido a PDF
    rml = loader.render_to_string(template_name, dictionary=dictionary,
        context_instance=context_instance)
    return rml2pdf.parseString(rml)

 
def render_to_response(*args, **kwargs):
    return HttpResponse(render_to_pdf(*args, **kwargs),
        content_type='application/pdf')

