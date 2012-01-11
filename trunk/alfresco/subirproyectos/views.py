# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory, formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.utils.simplejson import dumps


import mimetypes

from subirproyectos.forms import *
from subirproyectos.models import Proyecto, Anexo
from subirproyectos.models import save_proyect_to_alfresco
from subirproyectos.alfresco import Alfresco


@login_required
def index(request):
    return render_to_response('subirproyectos/index.html',
                              context_instance=RequestContext(request))


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
def solicitar_defensa(request):
    if request.method == 'POST':
	proyecto = None
	anexos = None

        request.POST['niu'] = request.user.niu()
	proyecto_form = FormularioProyecto(request.POST, request.FILES)
	anexo_formset = AnexoFormSet (request.POST, request.FILES)

	if proyecto_form.is_valid():
	    proyecto = proyecto_form.save(commit=False)
	    anexo_formset = AnexoFormSet (request.POST, request.FILES, instance = proyecto)
	else:
	    print proyecto_form.errors

	if anexo_formset.is_valid():
	    anexos = anexo_formset.save(commit=False)
	else:
	    print anexo_formset.errors

	if proyecto_form.is_valid() and anexo_formset.is_valid():
	    proyecto.estado = 'SOL'
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

            # TODO: Mandar correo al tutor para informar de la solicitud
            # El Correo debe contener el nombre del proyecto, el del alumno
            # y su dirección de correo. Para generarlo se deben usar plantillas
            # http://stackoverflow.com/questions/2809547/creating-email-templates-with-django
            # De manera que sea más fácil cambiar el correo (ojo, sólo hay que
            # mandar un correo en texto plano, no es necesario el envio de
            # alternativas en HTML.
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
    return render_to_response('subirproyectos/solicitar_defensa.html', {
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
    response = HTTPResponse(file_wrapper, content_type=proyect.format)
    response['Content-Length'] = content.headers.get('Content-Length')
    return response


@login_required
def descargar_anexo(request, id, anexo_id):
    # TODO: Probar que funciona
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_view_proyecto(proyecto):
        return HttpResponseForbidden()

    anexo = get_object_or_404(proyecto.anexos, id=anexo_id)
    content = Alfresco().download_content(anexo.alfresco_uuid)
    file_wrapper = FileWrapper(content)
    response = HTTPResponse(file_wrapper, content_type=proyect.format)
    response['Content-Length'] = content.headers.get('Content-Length')
    return response


# Sostrar una solicitud, diferente comportamiento segun el rol del que lo ve.
@login_required  
def solicitud_mostrar(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_view_proyecto(proyecto):
        return HttpResponseForbidden()
    
    anexos = proyecto.anexo_set.all()
    return render_to_response('subirproyectos/solicitud_mostrar.html', {
                                'proyecto': proyecto,
                                'anexos': anexos,
                                },
                                context_instance=RequestContext(request))
    #if p.estado == 'SOL':
        #url_proyecto = Alfresco().get_download_url(p.alfresco_uuid)
        #anexos = Anexo.objects.filter(proyecto = p.pk) 
        #urls_anexos = []
        #for anexo in anexos:
	  ##TODO mostrar el nombre del anexo en la plantilla
	  #urls_anexos.append(Alfresco().get_download_url(anexo.alfresco_uuid))
	#return render_to_response('subirproyectos/revisar_tutor.html', {'p': p, 'url_proyecto' : url_proyecto, 'urls_anexos' : urls_anexos, 'anexos' : anexos}
	#,  context_instance= RequestContext(request))
    #if p.estado == 'REV':
        ##return render_to_response('subirproyectos/calificar_proyecto_tutor.html', {'p': p})
        #return HttpResponseRedirect('/subirproyectos/'+id+'/calificar_proyecto_tutor/') 
    #if p.estado == 'CAL':    
        #return HttpResponseRedirect('/subirproyectos/'+id+'/archivar_proyecto_biblioteca/')

@login_required
def autorizar_defensa(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)
    if not request.user.can_autorizar_proyecto(proyecto):
        return HttpResponseForbidden()

    anexos = proyecto.anexo_set.all()

    if request.method == 'POST':
        proyecto_form = FormularioAutorizar(request.POST, instance=proyecto)

        if proyecto_form.is_valid():
            if "Autorizar" in request.POST:
                proyecto.estado = 'AUT'
                save_proyect_to_alfresco(proyecto, [], update_db=True)
                # TODO: Mandar correo al tutor y al alumno.
                # Al alumno para notificarle la decisión del tutor incluyendo el
                # comentario así como elnombre del proyecto.
                # Al profesor para recorarle que a autorizado la defensa del proyecto
                # X (incluir url a mostrar el proyecto) y recordándole una vez defendido
                # debe calificarlo (incluir url).
                # Para generarlo se deben usar plantillas
                # http://stackoverflow.com/questions/2809547/creating-email-templates-with-django
                # De manera que sea más fácil cambiar el correo (ojo, sólo hay que
                # mandar un correo en texto plano, no es necesario el envio de
                # alternativas en HTML.
                messages.add_message(request, messages.SUCCESS, """
                    <strong>La defensa del proyecto se ha autorizado con éxito.</strong> En
                    breves instantes esta circunstancia le será notificada al alumno. Recuerde
                    que una vez haya tenido lugar la defensa, deberá volver a la aplicación
                    para calificar el proyecto. Se le enviará más información acerca de este
                    procedimiento a través de su cuenta de correo electrónico.
                    """)
            elif "Rechazar" in request.POST:
                proyecto.estado = 'REC'
                save_proyect_to_alfresco(proyecto, [], update_db=True)
                # TODO: Mandar correo al tutor y al alumno.
                # Al alumno para notificarle la decisión del tutor incluyendo el
                # comentario así como elnombre del proyecto.
                # Al profesor para recorarle que a autorizado la defensa del proyecto
                # X (incluir url a mostrar el proyecto) y recordándole una vez defendido
                # debe calificarlo (incluir url).
                # Para generarlo se deben usar plantillas
                # http://stackoverflow.com/questions/2809547/creating-email-templates-with-django
                # De manera que sea más fácil cambiar el correo (ojo, sólo hay que
                # mandar un correo en texto plano, no es necesario el envio de
                # alternativas en HTML.
                messages.add_message(request, messages.SUCCESS, """
                    <strong>La defensa del proyecto se ha rechazado con éxito.</strong> En
                    breves instantes esta circunstancia le será notificada al alumno.
                    """)

            return redirect(mostrarlistatutor)
    else:
        proyecto_form = FormularioAutorizar(instance=proyecto)

    return render_to_response('subirproyectos/autorizar_defensa.html', {
                                'form': proyecto_form,
                                'proyecto': proyecto,
                                'anexos': anexos,
                                },
                                context_instance=RequestContext(request))

   #proyecto.estado = 'REV'
   #proyecto.tutor_nombre = request.POST['tutor_nombre']
   #proyecto.tutor_apellidos = request.POST['tutor_apellidos']
   #proyecto.director_nombre = request.POST['director_nombre']
   #proyecto.director_apellidos = request.POST['director_apellidos']
   #proyecto.save()
   ##dir = proyecto.alumno + '@ull.es'
   #send_mail('ULL: PFC validado', 'El tutor ha validado tu proyecto.', 'from@example.com',
    #['nombre@alfrescoull.org'], fail_silently=False)

   #correo a biblioteca avisando
   #return HttpResponseRedirect('/subirproyectos/results/')

@login_required
def rechazar(request):
   print request.POST['id']
   proyecto = Proyecto.objects.get(id = request.POST['id'])
   proyecto.estado = 'error'
   proyecto.save()
   send_mail('ULL: PFC no validado', 'El tutor no ha validado tu proyecto. Ponte en contacto con el', 'from@example.com',
    ['nombre@alfrescoull.org'], fail_silently=False)
   return HttpResponseRedirect('/subirproyectos/results/')

@login_required
def mostrarlistatutor(request):
    if not request.user.is_authenticated():
       return HttpResponseRedirect('/subirproyectos/')
    #proyectos por revisar la memoria y anexos   
    proyectos = Proyecto.objects.filter(tutor_email=request.user.username, estado='SOL')
    #proyectos por poner nota.
    proyectos_por_calificar = Proyecto.objects.filter(tutor_email=request.user.username, estado='REV')    
    print proyectos_por_calificar
    t = loader.get_template('subirproyectos/mostrarlistatutor.html')
    c = RequestContext(request, {'proyectos':proyectos, 'proyectos_por_calificar': proyectos_por_calificar })

    #c = Context({
        #'proyectos': proyectos,
        #'proyectos_por_calificar': proyectos_por_calificar,
    #})
    return HttpResponse(t.render(c))

@login_required  
def mostrarlistabiblioteca(request):
    if not request.user.is_authenticated():
       return HttpResponseRedirect('/subirproyectos/')
    proyectos = Proyecto.objects.filter(estado='CAL')#comprobar que es de la facultad
    #if is_faculty_staff (request.user.username):
       #proyectos = Proyecto.objects.filter(centro=get_faculty(request.user.username),estado=3)
       
    t = loader.get_template('subirproyectos/mostrarlistabiblioteca.html')
    c = RequestContext(request, {'proyectos': proyectos})
    #c = Context({
        #'proyectos': proyectos,
    #})
    return HttpResponse(t.render(c))

@login_required  
def calificar_proyecto_tutor(request, id):#TODO El codigo en caso de hacerse un post nunca se ejecuta
    p = Proyecto.objects.get(id = id)
    if request.method == 'POST': 
        form_proyecto_calificado = FormularioProyectoCalificado(request.POST) 
        if form_proyecto_calificado.is_valid(): 
	    p.proyectocalificado = form_proyecto_calificado.save(commit=False)
	    vocales_formset = VocalesFormSet (request.POST, instance = pc)
	    if vocales_formset.is_valid():
		p.estado = 'CAL'
		#hacemos update
		p.save()
		p.save_to_alfresco(p.titulacion.alfresco_uuid, False, True)
		return HttpResponseRedirect('/subirproyectos/results/') 
	    else:
		print vocales_formset.errors
		
		vocales_formset = VocalesFormSet (request.POST)
	else:
	    print form_proyecto_calificado.errors
	    vocales_formset = VocalesFormSet (request.POST)
    else:
        form_proyecto_calificado = FormularioProyectoCalificado() 
        vocales_formset = VocalesFormSet(instance = pc)
    return render_to_response('subirproyectos/calificar_proyecto_tutor.html', {
        'f': form_proyecto_calificado,
        'v': vocales_formset}, 
        context_instance= RequestContext(request))
    
@login_required 
def archivar_proyecto_biblioteca(request, id):
    pc = ProyectoCalificado.objects.get(id = id)
    if request.method == 'POST': 
	form = FormularioProyectoArchivado(request.POST) 
	if form.is_valid(): # All validation rules pass
	    pc.proyectoarchivado = form.save(commit=False)
            pc.estado = 'ARC'
            pc.save()
            p.save_to_alfresco(p.titulacion.alfresco_uuid, False, True)
	    return HttpResponseRedirect('/subirproyectos/results/') # Redirect after POST
    else:
	form = FormularioProyectoArchivado(instance = pc) # An unbound form

    return render_to_response('subirproyectos/archivar_proyecto_biblioteca.html', {
        'f': form},
    context_instance= RequestContext(request))
   
   #proyecto.estado = '4'
   #proyecto.title = request.POST['title']
   #proyecto.creator = request.POST['creator']
   #proyecto.description = request.POST['description']
   #proyecto.language = request.POST['language']
   ##proyecto.rights = request.POST['rights']
   #proyecto.coverage = request.POST['coverage']
   #proyecto.subject = request.POST['subject']
   #proyecto.save()
   #alfresco = Alfresco ()
   #alfresco.addMetadata (proyecto)
   #return HttpResponseRedirect('/subirproyectos/results/')
