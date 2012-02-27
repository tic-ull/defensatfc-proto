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

from django import template
from django.template import RequestContext, loader

from defensa import settings


register = template.Library()


@register.filter
def licencia(value):
    return loader.render_to_string('licencia.html', {
        'license_text': settings.DERECHOS[value]['texto'],
        'license_url': settings.DERECHOS[value]['url'],
        'license_image': settings.DERECHOS[value]['imagen'],
    })

@register.filter
def can_autorizar_proyecto(user, proyecto):
    return user.can_autorizar_proyecto(proyecto)

    
@register.filter
def can_calificar_proyecto(user, proyecto):
    return user.can_calificar_proyecto(proyecto)


@register.filter
def can_archivar_proyecto(user, proyecto):
    return user.can_archivar_proyecto(proyecto)
