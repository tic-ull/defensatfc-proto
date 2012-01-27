# -*- coding: utf-8 -*-
#  Gestión de Proyectos Fin de Carrera de la Universidad de La Laguna
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

from django.core.template import loader

import wkhtmltox
import tempfile


def render_to_pdf(template_name, *args, **kwargs):

    # renderizar la plantilla y guardar el resultado en el directorio temporal
    html_content = tempfile.NamedTemporaryFile(mode='w', prefix='django-html-')
    html_content.write(loader.render_to_string(template_name, *args, **kwargs))
    html_content.close()

    # convertir el contenio en HTML a PDF
    pdf_content = tempfile.NamedTemporaryFile(mode='r', prefix='django-html-')
    pdf = wkhtmltox.Pdf()
    pdf.set_global_setting('out', pdf_content.name)
    pdf.add_page({'page': html_content.name})
    pdf.convert()

    return pdf_content

    
def render_to_response(*args, **kwargs):
    return HttpResponse(render_to_pdf(*args, **kwargs),
                        mimetype='application/pdf')
