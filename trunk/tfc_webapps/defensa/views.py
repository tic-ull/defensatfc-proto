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

from django.core.mail import EmailMessage
from django.core.paginator import Paginator, InvalidPage
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission, User, Group
from django.db.models import Q
from django.forms.models import inlineformset_factory, formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect, render, get_object_or_404
from django.template import RequestContext, Context, loader
from django.template.loader import get_template
from django.utils.simplejson import dumps

from defensa import settings, pdf
from defensa.alfresco import Alfresco
from defensa.forms import *
from defensa.models import Trabajo, Anexo, AdscripcionUsuarioCentro

from datetime import date

import mimetypes
import operator
import os.path


BUSQUEDA_CAMPOS = ('title', 'creator_nombre', 'creator_apellidos', 'niu',)
BUSQUEDA_RESULTADOS_POR_PAGINA = 30


def filter(request, model_class, field_name, order_by=None):
    """Vista genérica para facilitar las consultas por AJAX a los modelos."""
    
    query_test = 'q' in request.GET and request.GET['q']
    if not request.user.is_authenticated() or not query_test:
        return HttpResponseNotFound()

    kwargs = {field_name: request.GET['q']}
    query = model_class.objects.filter(**kwargs)
    if order_by is not None:
        query = query.order_by(*order_by)
    results = [{'id': o.id, 'nombre': str(o)} for o in query]
    if not results:
        return HttpResponseNotFound()

    return HttpResponse(content=dumps(results), mimetype='application/json')


def index(request):
    """Página de inicio."""
    
    return render(request, 'index.html')


@login_required
def solicitar_defensa(request):
    """Formulario de solicitud de defensa de un trabajo fin de carrera."""
    
    if request.method == 'POST':
        if request.user.niu() is not None:
            request.POST['niu'] = request.user.niu()
        trabajo_form = FormularioSolicitud(request.POST, request.FILES)
	anexo_formset = AnexoFormSet (request.POST, request.FILES)

	if trabajo_form.is_valid():
	    trabajo = trabajo_form.save(commit=False)
	    anexo_formset = AnexoFormSet (request.POST, request.FILES, instance = trabajo)

        if anexo_formset.is_valid():
            anexos = anexo_formset.save(commit=False)

	if trabajo_form.is_valid() and anexo_formset.is_valid():
	    trabajo.estado = 'solicitado'
	    trabajo.type = settings.MEMORIA_TFC_TIPO_DOCUMENTO
            trabajo.creator_email = request.user.email
	    trabajo.format = mimetypes.guess_type(request.FILES['file'].name)[0]

	    anexos_files = []
            for anexo, form in zip(anexos, anexo_formset.forms):
	        anexo.format = mimetypes.guess_type(form.cleaned_data['file'].name)[0]
		anexos_files.append (form.cleaned_data['file'])
	    trabajo.save_to_alfresco(anexos=anexos,
                                     trabajo_contenido = request.FILES['file'],
				     anexos_contenidos = anexos_files,
				     update_relationship=True)

            # enviar correo al alumno
            plaintext = get_template('solicitar_defensa_email.txt')
            subject = settings.ASUNTO_TRABAJO_SOLICITADO
            from_email = settings.FROM_EMAIL
            to_email = [trabajo.tutor_email]
            c = Context({
                'trabajo': trabajo.title,
                'id': trabajo.id,
                'creator_nombre': trabajo.creator_nombre_completo(),
                'creator_email' : trabajo.creator_email,
                'niu': trabajo.niu,
            })
	    message_content = plaintext.render(c)
	    email = EmailMessage(subject, message_content, from_email, to_email)
	    email.send()

            messages.add_message(request, messages.SUCCESS, """
                <strong>Su solicitud se ha registrado con éxito.</strong> En
                breves instantes se le notificará al tutor que puede revisar
                la solicitud. Recibirá un correo electrónico con más detalles
                en cuanto el tutor autorice la defensa del trabajo.
            """)
	    return redirect(solicitud_mostrar, id=trabajo.id)

    else:
        initial = { 'niu': request.user.niu() }
        trabajo_form = FormularioSolicitud(initial=initial)
        anexo_formset = AnexoFormSet()
    if request.user.niu() is not None:
        trabajo_form.fields['niu'].widget.attrs['disabled'] = True
    return render(request, 'solicitar_defensa.html', {
                        'f': trabajo_form,
                        'a': anexo_formset,
                        'dominio_correo_tutor': settings.DOMINIO_CORREO_TUTOR,
                    })


#
# Vistas para editar trabajos y anexos
#

def editar_trabajo(request, id):
    """Vista para editar los metadatos de un trabajo durante la revisión."""

    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    trabajo = get_object_or_404(Trabajo, id=id)
    if not ((request.user.can_autorizar_trabajo(trabajo) and
            trabajo.estado == 'solicitado') or
            (request.user.can_archivar_trabajo(trabajo) and
            trabajo.estado == 'calificado')):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = FormularioTrabajo(request.POST, instance=trabajo)

        if form.is_valid():
            form.save()

            # if request.is_ajax():
            return render(request, 'trabajo_mostrar.html', {
                                'trabajo': trabajo,
                                'editable': True,
                            })
    else:
        form = FormularioTrabajo(instance=trabajo)

    return render(request, 'trabajo_editar.html', {'form':form})


def editar_anexo(request, id, anexo_id):
    """Vista para editar los metadatos de un anexo durante la revisión."""

    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    trabajo = get_object_or_404(Trabajo, id=id)
    if not ((request.user.can_autorizar_trabajo(trabajo) and
            trabajo.estado == 'solicitado') or
            (request.user.can_archivar_trabajo(trabajo) and
            trabajo.estado == 'calificado')):
        return HttpResponseForbidden()

    anexo = get_object_or_404(trabajo.anexo_set, id=anexo_id)
    if request.method == 'POST':
        form = FormularioAnexo(request.POST, instance=anexo)

        if form.is_valid():
            form.save()

            # if request.is_ajax():
            return render(request, 'anexo_mostrar.html', {
                                'anexo': anexo,
                                'editable': True,
                            })
    else:
        form = FormularioAnexo(instance=anexo)

    return render(request, 'anexo_editar.html', {'form':form})


#
# Vistas para la descarga de contenidos.
#

@login_required
def descargar_trabajo(request, id):
    """Vista para descarga la memoria del trabajo."""
    
    trabajo = get_object_or_404(Trabajo, id=id)
    if not request.user.can_view_trabajo(trabajo):
        return HttpResponseForbidden()

    content = Alfresco().download_content(trabajo.alfresco_uuid)
    file_wrapper = FileWrapper(content)
    response = HttpResponse(file_wrapper, content_type=trabajo.format)
    response['Content-Length'] = content.headers.get('Content-Length')
    response['Content-Disposition'] = ('attachment; filename=' +
        (settings.DESCARGAR_CONTENIDO_FILENAME % trabajo.niu))
    return response


@login_required
def descargar_anexo(request, id, anexo_id):
    """Vista para descarga un anexo de un trabajo."""
    
    trabajo = get_object_or_404(Trabajo, id=id)
    if not request.user.can_view_trabajo(trabajo):
        return HttpResponseForbidden()

    anexo = get_object_or_404(trabajo.anexo_set, id=anexo_id)
    content = Alfresco().download_content(anexo.alfresco_uuid)
    file_wrapper = FileWrapper(content)
    response = HttpResponse(file_wrapper, content_type=trabajo.format)
    response['Content-Length'] = content.headers.get('Content-Length')
    response['Content-Disposition'] = ('attachment; filename=' +
        (settings.DESCARGAR_ANEXO_FILENAME % (anexo.id, trabajo.niu)))
    return response


@login_required
def descargar_autorizacion(request, id):
    """Vista para descarga el documento de autorización de la defensa del trabajo."""
    
    trabajo = get_object_or_404(Trabajo, id=id)
    if not (request.user.can_view_trabajo(trabajo) or
            trabajo.estado == 'autorizado'):
        return HttpResponseForbidden()

    anexos = trabajo.anexo_set.all()
    content = pdf.render_to_pdf('autorizacion_defensa.rml', {
            'trabajo': trabajo,
            'anexos': anexos,
        },
        context_instance=RequestContext(request))
    response = HttpResponse(content,  content_type='application/pdf')
    response['Content-Disposition'] = ('attachment; filename=' +
        (settings.DESCARGAR_AUTORIZACION_FILENAME % trabajo.niu))
    return response

    
#
# Vistas para las acciones sobre cada trabajo
#

@login_required  
def solicitud_mostrar(request, id):
    """Mostrar toda la información acerca del trabajo cuya defensa se ha solicitado."""
    
    trabajo = get_object_or_404(Trabajo, id=id)
    if not request.user.can_view_trabajo(trabajo):
        return HttpResponseForbidden()
    
    anexos = trabajo.anexo_set.all()
    vocales = trabajo.tribunalvocal_set.all()
    return render(request, 'solicitud_mostrar.html', {
                                'trabajo': trabajo,
                                'anexos': anexos,
                                'vocales': vocales,
                            })


@login_required
def autorizar_defensa(request, id):
    """Vista para autorizar la defensa de un trabajo solicitado."""
    
    trabajo = get_object_or_404(Trabajo, id=id)
    if not (request.user.can_autorizar_trabajo(trabajo) and
            trabajo.estado == 'solicitado'):
        return HttpResponseForbidden()

    anexos = trabajo.anexo_set.all()

    if request.method == 'POST':
        trabajo_form = FormularioAutorizar(request.POST, instance=trabajo)

        if trabajo_form.is_valid():
            if "Autorizar" in request.POST:
                trabajo.estado = 'autorizado'
                trabajo.save_to_alfresco()

                # enviar correo al alumno
                plaintext = get_template('autorizar_defensa_email_alumno.txt')
                subject = settings.ASUNTO_TRABAJO_AUTORIZADO_ALUMNO
                from_email = settings.FROM_EMAIL
                to_email = [trabajo.creator_email]
		c = Context({
                    'trabajo': trabajo.title,
		    'comentario' : trabajo_form.cleaned_data['comentario'],
		    'url' : trabajo.get_absolute_url()
                })
		message_content = plaintext.render(c)
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()

                # enviar correo al tutor
                plaintext = get_template('autorizar_defensa_email_tutor.txt')
                subject = settings.ASUNTO_TRABAJO_AUTORIZADO_TUTOR
                from_email = settings.FROM_EMAIL
		to_email, [trabajo.tutor_email]
		c = Context({
                    'trabajo': trabajo.title,
                    'url' : trabajo.get_absolute_url()
                })
		message_content = plaintext.render(c)	    
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()   		
		
                messages.add_message(request, messages.SUCCESS, """
                    <strong>La defensa del trabajo se ha autorizado con éxito.</strong> En
                    breves instantes esta circunstancia le será notificada al alumno. Recuerde
                    que una vez haya tenido lugar la defensa, deberá volver a la aplicación
                    para calificar el trabajo. Se le enviará más información acerca de este
                    procedimiento a través de su cuenta de correo electrónico.
                    """)
            elif "Rechazar" in request.POST:
                trabajo.estado = 'rechazado'
                save_proyect_to_alfresco(trabajo, [], update_db=True)

		# enviar correo al alumno
                plaintext = get_template('rechazar_defensa_email_alumno.txt')
                subject = settings.ASUNTO_TRABAJO_RECHAZADO_ALUMNO
                from_email = settings.FROM_EMAIL
		to_email = [trabajo.creator_email]
		c = Context({
                    'trabajo': trabajo.title,
		    'comentario' : trabajo_form.cleaned_data['comentario']
                })
		message_content = plaintext.render(c)
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()

                messages.add_message(request, messages.SUCCESS, """
                    <strong>La defensa del trabajo se ha rechazado con éxito.</strong> En
                    breves instantes esta circunstancia le será notificada al alumno.
                    """)

            return redirect(lista_autorizar)
    else:
        trabajo_form = FormularioAutorizar(instance=trabajo)

    return render(request, 'autorizar_defensa.html', {
                                'form': trabajo_form,
                                'trabajo': trabajo,
                                'anexos': anexos,
                                'editable': True, # Para que se puedan editar los metados
                            })


@login_required  
def calificar_trabajo(request, id):
    """Vista para calificar un trabajo defendido."""
    
    trabajo = get_object_or_404(Trabajo, id=id)
    if not (request.user.can_calificar_trabajo(trabajo) and
            trabajo.estado == 'autorizado'):
        return HttpResponseForbidden()

    anexos = trabajo.anexo_set.all()

    if request.method == 'POST':
        trabajo_form = FormularioCalificar(request.POST, instance=trabajo)

        if trabajo_form.is_valid(): 
	    vocales_formset = VocalesFormSet (request.POST, instance=trabajo)

	    if vocales_formset.is_valid():
		trabajo.estado = 'calificado'
		# hacemos update
		vocales = vocales_formset.save(commit=False)
		trabajo.save_to_alfresco(anexos=[], vocales=vocales)

                # enviar correo al alumno
                plaintext = get_template('calificar_trabajo_email_alumno.txt')
                subject = settings.ASUNTO_TRABAJO_CALIFICADO
                from_email = settings.FROM_EMAIL
                to_email = [trabajo.creator_email]
                c = Context({
                    'trabajo': trabajo.title,           
                    'url' : trabajo.get_absolute_url()   
                })
                message_content = plaintext.render(c)
                email = EmailMessage(subject, message_content, from_email, to_email)
                email.send()

                # enviar correo a los bibliotecarios
                plaintext = get_template('calificar_trabajo_email_biblioteca.txt') 
		users = AdscripcionUsuarioCentro.objects.filter(centro=trabajo.titulacion.centro,
                    user__groups__name = settings.GRUPO_BIBLIOTECARIOS)
		to_email = [user.user.email for user in users]
		c = Context({
                    'trabajo': trabajo.title,
                    'calificacion': trabajo.pretty_calificacion(),
                    'calificacion_numerica': trabajo.pretty_calificacion_numerica(),
                    'url' : trabajo.get_absolute_url()   
                }) 
		message_content = plaintext.render(c)
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()    

                messages.add_message(request, messages.SUCCESS, """
                    <strong>El trabajo se ha calificado con éxito.</strong> En
                    breves instantes esto le será notificado al alumno.
                    """)
		return redirect(lista_calificar)

        vocales_formset = VocalesFormSet(request.POST)

    else:
        initial = {'fecha_defensa': date.today()}
        trabajo_form = FormularioCalificar(initial=initial)
        vocales_formset = VocalesFormSet()

    return render(request, 'calificar_trabajo.html', {
                                'f': trabajo_form,
                                'v': vocales_formset,
                                'trabajo': trabajo,
                                'anexos': anexos
                            })


@permission_required('defensa.puede_archivar')
def archivar_trabajo(request, id):
    """Vista para archivar un trabajo calificado."""

    trabajo = get_object_or_404(Trabajo, id=id)
    if not (request.user.can_archivar_trabajo(trabajo) and
            trabajo.estado == 'calificado'):
        return HttpResponseForbidden()

    anexos = trabajo.anexo_set.all() 
    vocales = trabajo.tribunalvocal_set.all()

    if request.method == 'POST':
	trabajo_form = FormularioArchivar(request.POST, instance=trabajo)

	if trabajo_form.is_valid():
            trabajo.estado = 'archivado'
            trabajo.save_to_alfresco()
            
            messages.add_message(request, messages.SUCCESS, """
                <strong>El trabajo se ha archivado con éxito.</strong> 
		""")
            return redirect(lista_archivar)
    else:
	trabajo_form = FormularioArchivar(instance=trabajo)

    return render(request, 'archivar_trabajo.html', {
                                'f': trabajo_form,
                                'trabajo': trabajo,
                                'anexos' : anexos,
                                'vocales' : vocales,
                                'editable': True,
                            })


#
# Vistas para listar los trabajos en sus diferentes estados.
#

def buscar_trabajos(request, trabajos):
    if 'q' in request.GET and request.GET['q']:
        words = request.GET['q'].split()
        conditions = []
        for field in BUSQUEDA_CAMPOS:
            kwargs = dict([(field+'__icontains', word) for word in words])
            conditions.append(Q(**kwargs))
        trabajos = trabajos.filter(reduce(operator.or_, conditions))
    trabajos = trabajos.order_by('creator_apellidos', 'creator_nombre')

    # Paginar los resultados de la búsqueda
    if 'per_page' in request.GET and request.GET['per_page']:
        try:
            per_page = int(request.GET['per_page'])
        except ValueError:
            per_page = BUSQUEDA_RESULTADOS_POR_PAGINA
        else:
            per_page = min(per_page, BUSQUEDA_RESULTADOS_POR_PAGINA)
        paginator = Paginator(trabajos, per_page)
    else:
        paginator = Paginator(trabajos, BUSQUEDA_RESULTADOS_POR_PAGINA)

    try:
        if 'page' in request.GET and request.GET['page']:
            page = paginator.page(request.GET['page'])
        else:
            page = paginator.page(1)
    except InvalidPage:
        page = paginator.page(1)

    return page


@login_required  
def lista_autorizar(request):
    if not request.user.is_tutor():
        return HttpResponseForbidden()

    trabajos = Trabajo.objects.filter(estado='solicitado',
        tutor_email=request.user.email)
    page = buscar_trabajos(request, trabajos)
    results = [{
        'title': trabajo.title,
        'niu': trabajo.niu,
        'creator': trabajo.creator_nombre_completo(),
        'creator_email' : trabajo.creator_email,
        'url': trabajo.get_absolute_url(),
    } for trabajo in page.object_list]

    template_dict = {
        'estado': 'solicitado',
        'trabajos': results,
        'total_paginas': page.paginator.num_pages,
        'total_trabajos': page.paginator.count,
    }

    if request.is_ajax():
        if 'json' in request.GET and request.GET['json']:
            return HttpResponse(content=dumps(results), mimetype='application/json')
        return render(request, 'lista_trabajo_partial.html', template_dict)

    if 'q' in request.GET and request.GET['q']:
        template_dict['q'] = request.GET['q']
    return render(request, 'lista.html', template_dict)


@login_required
def lista_calificar(request):
    if not request.user.is_tutor():
        return HttpResponseForbidden()  

    trabajos = Trabajo.objects.filter(estado='autorizado',
        tutor_email=request.user.email)
    page = buscar_trabajos(request, trabajos)
    results = [{
        'title': trabajo.title,
        'niu': trabajo.niu,
        'creator': trabajo.creator_nombre_completo(),
        'creator_email' : trabajo.creator_email,
        'url': trabajo.get_absolute_url(),
    } for trabajo in page.object_list]

    template_dict = {
        'estado': 'autorizado',
        'trabajos': results,
        'total_paginas': page.paginator.num_pages,
        'total_trabajos': page.paginator.count,
    }

    if request.is_ajax():
        if 'json' in request.GET and request.GET['json']:
            return HttpResponse(content=dumps(results), mimetype='application/json')
        return render(request, 'lista_trabajo_partial.html', template_dict)

    if 'q' in request.GET and request.GET['q']:
        template_dict['q'] = request.GET['q']
    return render(request, 'lista.html', template_dict)


@permission_required('defensa.puede_archivar')
def lista_archivar(request):
    trabajos = Trabajo.objects.filter(estado='calificado',
        titulacion__centro__in=request.user.centros())
    page = buscar_trabajos(request, trabajos)
    results = [{
        'title': trabajo.title,
        'niu': trabajo.niu,
        'creator': trabajo.creator_nombre_completo(),
        'creator_email' : trabajo.creator_email,
        'url': trabajo.get_absolute_url(),
    } for trabajo in page.object_list]

    template_dict = {
        'estado': 'calificado',
        'trabajos': results,
        'total_paginas': page.paginator.num_pages,
        'total_trabajos': page.paginator.count,
    }

    if request.is_ajax():
        if 'json' in request.GET and request.GET['json']:
            return HttpResponse(content=dumps(results), mimetype='application/json')
        return render(request, 'lista_trabajo_partial.html', template_dict)

    if 'q' in request.GET and request.GET['q']:
        template_dict['q'] = request.GET['q']
    return render(request, 'lista.html', template_dict)

