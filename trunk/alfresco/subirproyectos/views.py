# -*- coding: utf-8 -*-

from django.core.mail import EmailMessage
from django.core.paginator import Paginator, InvalidPage
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.forms.models import inlineformset_factory, formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.template.loader import get_template
from django.utils.simplejson import dumps

from subirproyectos.alfresco import Alfresco
from subirproyectos.forms import *
from subirproyectos.models import Proyecto, Anexo, ProyectoCalificado
from subirproyectos.models import AdscripcionUsuarioCentro
from subirproyectos.models import save_proyect_to_alfresco
from subirproyectos import settings

import mimetypes
import operator


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
	    proyecto = proyecto_form.save(commit=False)
	    anexo_formset = AnexoFormSet (request.POST, request.FILES, instance = proyecto)

	if anexo_formset.is_valid():
	    anexos = anexo_formset.save(commit=False)

	if proyecto_form.is_valid() and anexo_formset.is_valid():
	    proyecto.estado = Proyecto.ESTADOS['solicitado']
	    proyecto.type = 'MEMORIA'
            proyecto.creator_email = request.user.email
	    proyecto.format = mimetypes.guess_type(request.FILES['file'].name)

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
            from_email = settings.FROM_MAIL
            to_email = [proyecto.tutor_email]
            c = Context({
                'proyecto': proyecto.title,
                'id': proyecto.id,
                'creator_nombre': proyecto.creator_nombre_compleo(),
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
    # TODO: Probar que funciona
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_view_proyecto(proyecto):
        return HttpResponseForbidden()

    content = Alfresco().download_content(proyecto.alfresco_uuid)
    file_wrapper = FileWrapper(content)
    response = HttpResponse(file_wrapper, content_type=proyecto.format)
    response['Content-Length'] = content.headers.get('Content-Length')
    return response


@login_required
def descargar_anexo(request, id, anexo_id):
    # TODO: Probar que funciona
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_view_proyecto(proyecto):
        return HttpResponseForbidden()

    anexo = get_object_or_404(proyecto.anexo_set, id=anexo_id)
    content = Alfresco().download_content(anexo.alfresco_uuid)
    file_wrapper = FileWrapper(content)
    response = HttpResponse(file_wrapper, content_type=proyecto.format)
    response['Content-Length'] = content.headers.get('Content-Length')
    return response


@login_required  
def solicitud_mostrar(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_view_proyecto(proyecto):
        return HttpResponseForbidden()
    
    anexos = proyecto.anexo_set.all()
    return render_to_response('solicitud_mostrar.html', {
                                'proyecto': proyecto,
                                'anexos': anexos,
                                },
                                context_instance=RequestContext(request))


@login_required
def autorizar_defensa(request, id):
    proyecto = get_object_or_404(Proyecto, id=id) # TODO: Recuperar proyecto calificar
    if not request.user.can_autorizar_proyecto(proyecto):
        return HttpResponseForbidden()

    anexos = proyecto.anexo_set.all()

    if request.method == 'POST':
        proyecto_form = FormularioAutorizar(request.POST, instance=proyecto)

        if proyecto_form.is_valid():
            if "Autorizar" in request.POST:
                proyecto.estado = Proyecto.ESTADOS['autorizado']
                save_proyect_to_alfresco(proyecto, [], update_db=True)

                # enviar correo al alumno
                plaintext = get_template('autorizar_defensa_email_alumno.txt')
                subject = settings.ASUNTO_PROYECTO_AUTORIZADO_ALUMNO
                from_email = settings.FROM_MAIL
                to_email = [proyecto.creator_email]
		c = Context({
                    'proyecto': proyecto.title,
		    'comentario' : proyecto_form.comentario
                })
		message_content = plaintext.render(c)
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()

                # enviar correo al tutor
                plaintext = get_template('autorizar_defensa_email_tutor.txt')
                subject = settings.ASUNTO_PROYECTO_AUTORIZADO_TUTOR
                from_email = settings.FROM_MAIL
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
                proyecto.estado = Proyecto.ESTADOS['rechazado']
                save_proyect_to_alfresco(proyecto, [], update_db=True)

		# enviar correo al alumno
                plaintext = get_template('rechazar_defensa_email_alumno.txt')
                subject = settings.ASUNTO_PROYECTO_RECHAZADO_ALUMNO
                from_email = settings.FROM_MAIL
		to_email = [proyecto.creator_email]
		c = Context({
                    'proyecto': proyecto.title,
		    'comentario' : proyecto_form.comentario
                })
		message_content = plaintext.render(c)
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()

                messages.add_message(request, messages.SUCCESS, """
                    <strong>La defensa del proyecto se ha rechazado con éxito.</strong> En
                    breves instantes esta circunstancia le será notificada al alumno.
                    """)

            return redirect(mostrarlistatutor)
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
    if not request.user.can_calificar_proyecto(p): # TODO: Esta no puede ser la comprobación del permiso. Mejor usar el decorado @permission_required
        return HttpResponseForbidden()

    anexos = p.anexo_set.all()

    if request.method == 'POST':
        # TODO: Por coherencia usar proyecto_form simplemente
        # TODO: ¿Seguro que no hace falta el instance=p?
        # Si no se  pone ¿Como si vincula el formulario a esta instancia de proyecto?
        form_proyecto_calificado = FormularioProyectoCalificado(request.POST)

        if form_proyecto_calificado.is_valid(): 
	    p.proyectocalificado = form_proyecto_calificado.save(commit=False) # TODO: Si se usa instance=p, no ace falta
	    vocales_formset = VocalesFormSet (request.POST, instance = p)

	    # TODO: Asegurarnos de que la validación de los dos tipos de
	    # calificación funciona (númerica y no numérica).
	    if vocales_formset.is_valid():
		p.estado = Proyecto.ESTADOS['calificado']
		#hacemos update
		p.save() # TODO: No hace falta, lo hace save_proyecto_to....
		#p.save_to_alfresco(p.titulacion.alfresco_uuid, False, True)
		save_proyect_to_alfresco(pc, [], update_db=True)

                # enviar correo al alumno
                plaintext = get_template('calificar_proyecto_email_alumno.txt')
                subject = settings.ASUNTO_PROYECTO_CALIFICADO
                from_email = settings.FROM_MAIL
                to_email = [proyecto.creator_email]
                c = Context({
                    'proyecto': proyecto.title,           # TODO: Estás usando p ¿no será p?
                    'url' : proyecto.get_absolute_url()   # TODO: Estás usando p ¿no será p?
                })
                message_content = plaintext.render(d)
                email = EmailMessage(subject, message_content, from_email, to_email)
                email.send()

                # enviar correo a los bibliotecarios
                plaintext = get_template('calificar_proyecto_email_biblioteca.txt')
                perm = Permission.objects.get(codename='puede_archivar')
                users = User.objects.filter(Q(groups__permissions=perm) | Q(user_permissions=perm) ).distinct()
                to_email = [user.email for user in users]

		c = Context({
                    'proyecto': proyecto.title,           # TODO: Estás usando p ¿no será p?
                    'url' : proyecto.get_absolute_url()   # TODO: Estás usando p ¿no será p?
                }) 
		message_content = plaintext.render(c)
		email = EmailMessage(subject, message_content, from_email, to_email)
		email.send()    

                messages.add_message(request, messages.SUCCESS, """
                    <strong>El proyecto se ha calificado con éxito.</strong> En
                    breves instantes esta circunstancia le será notificada al alumno.
                    """)
                # TODO: Como autorizar, debe ir a lista_calificar si todo va bien
		return redirect(calificar_proyecto)

        vocales_formset = VocalesFormSet (request.POST)

    else:
        # TODO: ¿Seguro que no hace falta el instance=p?
        form_proyecto_calificado = FormularioProyectoCalificado() 
        vocales_formset = VocalesFormSet(instance = p)

    return render_to_response('calificar_proyecto.html', {
                                'f': form_proyecto_calificado,
                                'v': vocales_formset,
                                'proyecto': p, # TODO: ¿Para qué lo pasas?
                                'anexos': anexos # TODO: Esto no está definido
                                }, 
                                context_instance=RequestContext(request))


@login_required 
def archivar_proyecto(request, id):
    pc = get_object_or_404(ProyectoCalificado, id=id)
    #pc = ProyectoCalificado.objects.get(id = id)

    if request.method == 'POST':
        # TODO: Por coherencia usar proyecto_form simplemente y vincular con
        # pc (mejor p o proyecto como antes con el instance=p
	form = FormularioProyectoArchivado(request.POST)
	if form.is_valid():
	    pc.proyectoarchivado = form.save(commit=False) # TODO: NO hace falta
            pc.estado = Proyecto.ESTADOS['archivado']
            pc.save() # TODO: Tampoco hace falta
            #pc.save_to_alfresco(p.titulacion.alfresco_uuid, False, True)
            save_proyect_to_alfresco(pc, [], update_db=True)
            messages.add_message(request, messages.SUCCESS, """
		<strong>El proyecto se ha archivado con éxito.</strong> 
                """)
            # TODO: Volver al listado de proyectos a archiva.
	    return redirect(archivar_proyecto)
    else:
	form = FormularioProyectoArchivado(instance = pc)

    return render_to_response('archivar_proyecto.html', {
                                'f': form
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

    proyectos = Proyecto.objects.filter(estado=Proyecto.ESTADOS['solicitado'],
        tutor_email=request.user.email)
    page = buscar_proyectos(request, proyectos)
    results = [{
        'title': proyecto.title,
        'niu': proyecto.niu,
        'creator': proyecto.creator_nombre_completo(),
        'url': proyecto.get_absolute_url(),
    } for proyecto in page.object_list]

    template_dict = {
        'estado': 'solicitado',
        'proyectos': results,
        'total_paginas': page.paginator.num_pages,
        'total_proyectos': page.paginator.count,
    }

    if request.is_ajax():
        return render_to_response('lista_proyecto_partial.html', template_dict,
            context_instance= RequestContext(request))

    if 'q' in request.GET and request.GET['q']:
        template_dict['q'] = request.GET['q']
    return render_to_response('lista.html', template_dict,
        context_instance= RequestContext(request))


@login_required
def lista_calificar(request):
    # TODO: Preparar como lista autorizar
    if not request.user.is_authenticated():
       return HttpResponseRedirect('/subirproyectos/')

    proyectos = Proyecto.objects.filter(estado=Proyecto.ESTADOS['autorizado'],
        tutor_email=request.user.email)

    #proyectos por revisar la memoria y anexos
    proyectos = Proyecto.objects.filter(tutor_email=request.user.username,
        estado=Proyecto.ESTADOS['solicitado'])
    #proyectos por poner nota.
    t = loader.get_template('subirproyectos/mostrarlistatutor.html')
    c = RequestContext(request, {'proyectos':proyectos, 'proyectos_por_calificar': proyectos_por_calificar })

    #c = Context({
        #'proyectos': proyectos,
        #'proyectos_por_calificar': proyectos_por_calificar,
    #})
    return HttpResponse(t.render(c))


@permission_required('Proyecto.puede_archivar')
def lista_archivar(request):
    # TODO: Preparar como lista autorizar
    if not request.user.is_authenticated():
       return HttpResponseRedirect('/subirproyectos/')

    centros = AdscripcionUsuarioCentro.objects.filter(user=request.user)
    proyectos = Proyecto.objects.filter(estado=Proyecto.ESTADOS['calificado'],
        centro__in=centros)

    #if is_faculty_staff (request.user.username):
       #proyectos = Proyecto.objects.filter(centro=get_faculty(request.user.username),estado=3)
       
    t = loader.get_template('subirproyectos/mostrarlistabiblioteca.html')
    c = RequestContext(request, {'proyectos': proyectos})
    #c = Context({
        #'proyectos': proyectos,
    #})
    return HttpResponse(t.render(c))
