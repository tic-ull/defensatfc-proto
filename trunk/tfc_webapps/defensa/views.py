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

from django.core.mail import EmailMessage
from django.core.paginator import Paginator, InvalidPage
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission, User, Group
from django.db.models import Q, F
from django.forms.models import inlineformset_factory, formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.template.loader import get_template
from django.utils.simplejson import dumps

from defensa import settings
from defensa.alfresco import Alfresco
from defensa.forms import *
from defensa.models import Proyecto, Anexo
from defensa.models import AdscripcionUsuarioCentro
from defensa.models import save_proyect_to_alfresco

import mimetypes
import operator
import os.path


BUSQUEDA_CAMPOS = ('title', 'creator_nombre', 'creator_apellidos', 'niu',)
BUSQUEDA_RESULTADOS_POR_PAGINA = 30


def filter(request, model_class, field_name):
    query_test = 'q' in request.GET and request.GET['q']
    if not request.user.is_authenticated() or not query_test:
        return HttpResponseNotFound()

    kwargs = {field_name: request.GET['q']}
    search = list(model_class.objects.filter(**kwargs).values('id', 'nombre'))
    if not search:
        return HttpResponseNotFound()

    return HttpResponse(content=dumps(search), mimetype='application/json')


@login_required
def index(request):
    return render_to_response('index.html',
                              context_instance=RequestContext(request))


@login_required
def solicitar_defensa(request):
    if request.method == 'POST':
        request.POST['niu'] = request.user.niu()
        proyecto_form = FormularioProyecto(request.POST, request.FILES)
	anexo_formset = AnexoFormSet (request.POST, request.FILES)

	if proyecto_form.is_valid():
	    proyecto = proyecto_form.save(commit=True)
	    anexo_formset = AnexoFormSet (request.POST, request.FILES, instance = proyecto)

	    if anexo_formset.is_valid():
		anexos = anexo_formset.save(commit=False)

	if proyecto_form.is_valid() and anexo_formset.is_valid():
	    proyecto.estado = 'solicitado'
	    proyecto.type = 'memoria'
            proyecto.creator_email = request.user.email
	    proyecto.format = mimetypes.guess_type(request.FILES['file'].name)[0]

	    anexos_files = []
            for anexo, form in zip(anexos, anexo_formset.forms):
	        anexo.format = mimetypes.guess_type(form.cleaned_data['file'].name)
		anexos_files.append (form.cleaned_data['file'])
	    save_proyect_to_alfresco(proyecto, anexos,
				     update_db=True,
                                     proyecto_contenido = request.FILES['file'],
				     anexos_contenidos = anexos_files)

            # enviar correo al alumno
            plaintext = get_template('solicitar_defensa_email.txt')
            subject = settings.ASUNTO_PROYECTO_SOLICITADO
            from_email = settings.FROM_EMAIL
            to_email = [proyecto.tutor_email]
            c = Context({
                'proyecto': proyecto.title,
                'id': proyecto.id,
                'creator_nombre': proyecto.creator_nombre_completo(),
                'creator_email' : proyecto.creator_email,
                'niu': proyecto.niu,
            })
	    message_content = plaintext.render(c)
	    email = EmailMessage(subject, message_content, from_email, to_email)
	    email.send()

            messages.add_message(request, messages.SUCCESS, """
                <strong>Su solicitud se ha registrado con éxito.</strong> En
                breves instantes se le notificará al tutor que puede revisar
                la solicitud. Recibirá un correo electrónico con más detalles
                en cuanto el tutor autorice la defensa del proyecto.
            """)
	    return redirect(solicitud_mostrar, id=proyecto.id)

    else:
        initial = { 'niu': request.user.niu() }
        proyecto_form = FormularioProyecto(initial=initial)
        anexo_formset = AnexoFormSet()
	if request.user.niu() is not None:
	    proyecto_form.fields['niu'].widget.attrs['disabled'] = True
    return render_to_response('solicitar_defensa.html', {
                        'f': proyecto_form,
                        'a': anexo_formset,
                        'dominio_correo_tutor': settings.DOMINIO_CORREO_TUTOR,
                        },
                        context_instance=RequestContext(request))


#
# Vistas para la descarga de contenidos.
#

@login_required
def descargar_contenido(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_view_proyecto(proyecto):
        return HttpResponseForbidden()

    content = Alfresco().download_content(proyecto.alfresco_uuid)
    file_wrapper = FileWrapper(content)
    response = HttpResponse(file_wrapper, content_type=proyecto.format)
    response['Content-Length'] = content.headers.get('Content-Length')
    response['Content-Disposition'] = ('attachment; filename=' +
        (settings.DESCARGAR_CONTENIDO_FILENAME % proyecto.niu))
    return response


@login_required
def descargar_anexo(request, id, anexo_id):
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_view_proyecto(proyecto):
        return HttpResponseForbidden()

    anexo = get_object_or_404(proyecto.anexo_set, id=anexo_id)
    content = Alfresco().download_content(anexo.alfresco_uuid)
    file_wrapper = FileWrapper(content)
    response = HttpResponse(file_wrapper, content_type=proyecto.format)
    response['Content-Length'] = content.headers.get('Content-Length')
    response['Content-Disposition'] = ('attachment; filename=' +
        (settings.DESCARGAR_ANEXO_FILENAME % (anexo.id, proyecto.niu)))
    return response


@login_required
def descargar_autorizacion(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)


@login_required  
def solicitud_mostrar(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_view_proyecto(proyecto):
        return HttpResponseForbidden()
    
    anexos = proyecto.anexo_set.all()
    vocales = proyecto.tribunalvocal_set.all()
    return render_to_response('solicitud_mostrar.html', {
                                'proyecto': proyecto,
                                'anexos': anexos,
                                'vocales': vocales,
                                },
                                context_instance=RequestContext(request))


@login_required
def autorizar_defensa(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_autorizar_proyecto(proyecto) or not proyecto.estado == 'solicitado':
        return HttpResponseForbidden()

    anexos = proyecto.anexo_set.all()

    if request.method == 'POST':
        proyecto_form = FormularioAutorizar(request.POST, instance=proyecto)

        if proyecto_form.is_valid():
            if "Autorizar" in request.POST:
                proyecto.estado = 'autorizado'
                save_proyect_to_alfresco(proyecto, [], update_db=True)

                # enviar correo al alumno
                plaintext = get_template('autorizar_defensa_email_alumno.txt')
                subject = settings.ASUNTO_PROYECTO_AUTORIZADO_ALUMNO
                from_email = settings.FROM_EMAIL
                to_email = [proyecto.creator_email]
		c = Context({
                    'proyecto': proyecto.title,
		    'comentario' : proyecto_form.cleaned_data['comentario'],
		    'url' : proyecto.get_absolute_url()
                })
		message_content = plaintext.render(c)
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()

                # enviar correo al tutor
                plaintext = get_template('autorizar_defensa_email_tutor.txt')
                subject = settings.ASUNTO_PROYECTO_AUTORIZADO_TUTOR
                from_email = settings.FROM_EMAIL
		to_email, [proyecto.tutor_email]
		c = Context({
                    'proyecto': proyecto.title,
                    'url' : proyecto.get_absolute_url()
                })
		message_content = plaintext.render(c)	    
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()   		
		
                messages.add_message(request, messages.SUCCESS, """
                    <strong>La defensa del proyecto se ha autorizado con éxito.</strong> En
                    breves instantes esta circunstancia le será notificada al alumno. Recuerde
                    que una vez haya tenido lugar la defensa, deberá volver a la aplicación
                    para calificar el proyecto. Se le enviará más información acerca de este
                    procedimiento a través de su cuenta de correo electrónico.
                    """)
            elif "Rechazar" in request.POST:
                proyecto.estado = 'rechazado'
                save_proyect_to_alfresco(proyecto, [], update_db=True)

		# enviar correo al alumno
                plaintext = get_template('rechazar_defensa_email_alumno.txt')
                subject = settings.ASUNTO_PROYECTO_RECHAZADO_ALUMNO
                from_email = settings.FROM_EMAIL
		to_email = [proyecto.creator_email]
		c = Context({
                    'proyecto': proyecto.title,
		    'comentario' : proyecto_form.cleaned_data['comentario']
                })
		message_content = plaintext.render(c)
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()

                messages.add_message(request, messages.SUCCESS, """
                    <strong>La defensa del proyecto se ha rechazado con éxito.</strong> En
                    breves instantes esta circunstancia le será notificada al alumno.
                    """)

            return redirect(lista_autorizar)
    else:
        proyecto_form = FormularioAutorizar(instance=proyecto)

    return render_to_response('autorizar_defensa.html', {
                                'form': proyecto_form,
                                'proyecto': proyecto,
                                'anexos': anexos,
                                },
                                context_instance=RequestContext(request))


@login_required  
def calificar_proyecto(request, id):
    p = get_object_or_404(Proyecto, id=id)
    if not request.user.can_calificar_proyecto(p) or not p.estado == 'autorizado':
        return HttpResponseForbidden()

    anexos = p.anexo_set.all()
    if request.method == 'POST':
        proyecto_form = FormularioProyectoCalificado(request.POST, instance=p)

        if proyecto_form.is_valid(): 
	    vocales_formset = VocalesFormSet (request.POST, instance = p)

	    if vocales_formset.is_valid():
		p.estado = 'calificado'
		# hacemos update
		vocales = vocales_formset.save(commit=False) 
		save_proyect_to_alfresco(p, [], vocales=vocales, update_db=True)		
                # enviar correo al alumno
                plaintext = get_template('calificar_proyecto_email_alumno.txt')
                subject = settings.ASUNTO_PROYECTO_CALIFICADO
                from_email = settings.FROM_EMAIL
                to_email = [p.creator_email]
                c = Context({
                    'proyecto': p.title,           
                    'url' : p.get_absolute_url()   
                })
                message_content = plaintext.render(c)
                email = EmailMessage(subject, message_content, from_email, to_email)
                email.send()

                # enviar correo a los bibliotecarios
                plaintext = get_template('calificar_proyecto_email_biblioteca.txt') 
		users = AdscripcionUsuarioCentro.objects.filter(centro=p.titulacion.centro, user__groups__name = settings.PUEDEN_ARCHIVAR)
		to_email = [user.user.email for user in users]                
		c = Context({
                    'proyecto': p.title,         
                    'url' : p.get_absolute_url()   
                }) 
		message_content = plaintext.render(c)
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()    

                messages.add_message(request, messages.SUCCESS, """
                    <strong>El proyecto se ha calificado con éxito.</strong> En
                    breves instantes esta circunstancia le será notificada al alumno.
                    """)
		return redirect(lista_calificar)

        vocales_formset = VocalesFormSet (request.POST)

    else:
        proyecto_form = FormularioProyectoCalificado(instance = p) 
        vocales_formset = VocalesFormSet()

    return render_to_response('calificar_proyecto.html', {
                                'f': proyecto_form,
                                'v': vocales_formset,
                                'proyecto': p,
                                'anexos': anexos
                                }, 
                                context_instance=RequestContext(request))



@permission_required('defensa.puede_archivar')
def archivar_proyecto(request, id):
    p = get_object_or_404(Proyecto, id=id) 
    if not p.estado == 'calificado':
        return HttpResponseForbidden()    
    anexos = p.anexo_set.all() 
    vocales = p.tribunalvocal_set.all()
    if request.method == 'POST':
	proyecto_form = FormularioProyectoArchivado(request.POST, instance = p)
	anexo_formset = AnexoModelFormset(request.POST, queryset = anexos)
	if proyecto_form.is_valid():
	    if anexo_formset.is_valid():
	        anexos = anexo_formset.save(commit=False)
		p.estado = 'archivado'
		save_proyect_to_alfresco(p, anexos, update_db=True)
		messages.add_message(request, messages.SUCCESS, """
		    <strong>El proyecto se ha archivado con éxito.</strong> 
		    """)
		return redirect(lista_archivar)
    else:
	proyecto_form = FormularioProyectoArchivado(instance=p)
	anexo_formset = AnexoModelFormset (queryset = anexos)
    return render_to_response('archivar_proyecto.html', {
                                'f': proyecto_form,
                                'a' : anexo_formset,
                                'proyecto': p,
                                'anexos' : anexos,
                                'vocales' : vocales,
                                },
                                context_instance=RequestContext(request))




def buscar_proyectos(request, proyectos):
    if 'q' in request.GET and request.GET['q']:
        words = request.GET['q'].split()
        conditions = []
        for field in BUSQUEDA_CAMPOS:
            kwargs = dict([(field+'__icontains', word) for word in words])
            conditions.append(Q(**kwargs))
        proyectos = proyectos.filter(reduce(operator.or_, conditions))
    proyectos = proyectos.order_by('creator_apellidos', 'creator_nombre')

    # Paginar los resultados de la búsqueda
    if 'per_page' in request.GET and request.GET['per_page']:
        try:
            per_page = int(request.GET['per_page'])
        except ValueError:
            per_page = BUSQUEDA_RESULTADOS_POR_PAGINA
        else:
            per_page = min(per_page, BUSQUEDA_RESULTADOS_POR_PAGINA)
        paginator = Paginator(proyectos, per_page)
    else:
        paginator = Paginator(proyectos, BUSQUEDA_RESULTADOS_POR_PAGINA)

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

    proyectos = Proyecto.objects.filter(estado='solicitado',
        tutor_email=request.user.email)
    page = buscar_proyectos(request, proyectos)
    results = [{
        'title': proyecto.title,
        'niu': proyecto.niu,
        'creator': proyecto.creator_nombre_completo(),
        'creator_email' : proyecto.creator_email,
        'url': proyecto.get_absolute_url(),
    } for proyecto in page.object_list]

    template_dict = {
        'estado': 'solicitado',
        'proyectos': results,
        'total_paginas': page.paginator.num_pages,
        'total_proyectos': page.paginator.count,
    }

    if request.is_ajax():
        if 'json' in request.GET and request.GET['json']:
            return HttpResponse(content=dumps(results), mimetype='application/json')
        return render_to_response('lista_proyecto_partial.html', template_dict,
            context_instance= RequestContext(request))

    if 'q' in request.GET and request.GET['q']:
        template_dict['q'] = request.GET['q']
    return render_to_response('lista.html', template_dict,
        context_instance= RequestContext(request))


@login_required
def lista_calificar(request):
    if not request.user.is_tutor():
        return HttpResponseForbidden()  

    proyectos = Proyecto.objects.filter(estado='autorizado',
        tutor_email=request.user.email)
    page = buscar_proyectos(request, proyectos)
    results = [{
        'title': proyecto.title,
        'niu': proyecto.niu,
        'creator': proyecto.creator_nombre_completo(),
        'creator_email' : proyecto.creator_email,
        'url': proyecto.get_absolute_url(),
    } for proyecto in page.object_list]

    template_dict = {
        'estado': 'autorizado',
        'proyectos': results,
        'total_paginas': page.paginator.num_pages,
        'total_proyectos': page.paginator.count,
    }

    if request.is_ajax():
        if 'json' in request.GET and request.GET['json']:
            return HttpResponse(content=dumps(results), mimetype='application/json')
        return render_to_response('lista_proyecto_partial.html', template_dict,
            context_instance= RequestContext(request))

    if 'q' in request.GET and request.GET['q']:
        template_dict['q'] = request.GET['q']
    return render_to_response('lista.html', template_dict,
        context_instance= RequestContext(request))


@permission_required('defensa.puede_archivar')
def lista_archivar(request):
    centros = AdscripcionUsuarioCentro.objects.filter(user=request.user).values('centro')
    proyectos = Proyecto.objects.filter(estado='calificado',
        titulacion__centro__in=centros)
    page = buscar_proyectos(request, proyectos)
    results = [{
        'title': proyecto.title,
        'niu': proyecto.niu,
        'creator': proyecto.creator_nombre_completo(),
        'creator_email' : proyecto.creator_email,
        'url': proyecto.get_absolute_url(),
    } for proyecto in page.object_list]

    template_dict = {
        'estado': 'calificado',
        'proyectos': results,
        'total_paginas': page.paginator.num_pages,
        'total_proyectos': page.paginator.count,
    }

    if request.is_ajax():
        if 'json' in request.GET and request.GET['json']:
            return HttpResponse(content=dumps(results), mimetype='application/json')
        return render_to_response('lista_proyecto_partial.html', template_dict,
            context_instance= RequestContext(request))

    if 'q' in request.GET and request.GET['q']:
        template_dict['q'] = request.GET['q']
    return render_to_response('lista.html', template_dict,
        context_instance= RequestContext(request))

