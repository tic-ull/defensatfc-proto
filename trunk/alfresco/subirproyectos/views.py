from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory, formset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.contrib.auth.decorators import login_required

import mimetypes

from subirproyectos.forms import *
from subirproyectos.models import Proyecto, Anexo
from subirproyectos.models import save_proyect_to_alfresco
from subirproyectos.alfresco import Alfresco
from subirproyectos.url_download_file import url_download_file 


def index(request):
    return render_to_response('subirproyectos/index.html',
                               context_instance=RequestContext(request))
                               
                               
# def login(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         if user.is_active:
#             auth_login(request, user)
#             print "You provided a correct username and password!"
#             if is_student(request.user.username):
# 	       return HttpResponseRedirect('/subirproyectos/subir/')
#             if is_library_staff (request.user.username):
# 	       return HttpResponseRedirect('/subirproyectos/mostrarlistabiblioteca/')
#             #if is_faculty_staff (request.user.username):
# 	       #return HttpResponseRedirect('/subirproyectos/mostrarlista/')
# 	    if is_professor (request.user.username):
# 	       return HttpResponseRedirect('/subirproyectos/mostrarlistatutor/')
#             #si eres alumno goto formulario
#             
# 
#             #si eres otra cosa goto mostrarlista
#         else:
# 	    print "Your account has been disabled!"
#             # Return a 'disabled account' error message
#     else:
#         print "Your username and password were incorrect."
#         # Return an 'invalid login' error message.
#         
# def logout_view(request):
#     logout(request)

#TODO la plantilla de los anexos se ve mal, no caben tantos fields en una row
@login_required        
def solicitar_defensa(request):
    if request.method == 'POST':
        proyecto_form = FormularioProyecto(request.POST, request.FILES)
        if proyecto_form.is_valid(): 
	        proyecto = proyecto_form.save(commit=False)
	        anexo_formset = AnexoFormSet (request.POST, request.FILES, instance = proyecto)
	        if anexo_formset.is_valid():
	            proyecto.estado = 'SOL'
	            proyecto.format = mimetypes.guess_type(request.FILES['file'].name)
	            proyecto.type = 'MEMORIA'
		    anexos = anexo_formset.save(commit=False)
		    lista_anexos = []
		    for anexo, form in zip(anexos, anexo_formset.forms):
		      anexo.format = mimetypes.guess_type(form.cleaned_data['file'].name)
		      lista_anexos.append (form.cleaned_data['file'])
		    save_proyect_to_alfresco(proyecto, anexos, update_db=True, proyecto_contenido = request.FILES['file'], anexos_contenidos = lista_anexos )
		    return HttpResponseRedirect('/subirproyectos/results/')	            
	        else:
	            print anexo_formset.errors 
	            anexo_formset = AnexoFormSet (request.POST, request.FILES)
        else:
	    anexo_formset = AnexoFormSet (request.POST, request.FILES)
    else:
        proyecto_form = FormularioProyecto()
        anexo_formset = AnexoFormSet(instance = Proyecto())
    return render_to_response('subirproyectos/solicitar_defensa.html', {'f': proyecto_form, 'a' : anexo_formset }, context_instance=RequestContext(request))


def formulario(request):
    ##necesita estar logueado
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/subirproyectos/')
    f = FormularioProyecto()
    return render_to_response('subirproyectos/subir.html', {'f': f},
                               context_instance=RequestContext(request))
    

def result(request):
    return HttpResponse("Ha sido exitoso.")
 
#mostrar un proyecto, diferente comportamiento segun el rol del que lo ve.
def mostrar(request, id):
    p = Proyecto.objects.get(id = id)
    if p.estado == 'SOL':  
        url_proyecto = Alfresco().get_download_url(p.alfresco_uuid)
        anexos = Anexo.objects.filter(proyecto = p.pk) 
        urls_anexos = []
        for anexo in anexos:
	  #TODO mostrar el nombre del anexo en la plantilla
	  urls_anexos.append(Alfresco().get_download_url(anexo.alfresco_uuid))
	return render_to_response('subirproyectos/revisar_tutor.html', {'p': p, 'url_proyecto' : url_proyecto, 'urls_anexos' : urls_anexos, 'anexos' : anexos})
    if p.estado == 'REV':
        #return render_to_response('subirproyectos/calificar_proyecto_tutor.html', {'p': p})
        return HttpResponseRedirect('/subirproyectos/'+id+'/calificar_proyecto_tutor/') 
    if p.estado == 'CAL':    
        return HttpResponseRedirect('/subirproyectos/'+id+'/archivar_proyecto_biblioteca/')


def mostrarlistatutor(request):
    if not request.user.is_authenticated():
       return HttpResponseRedirect('/subirproyectos/')
    #proyectos por revisar la memoria y anexos   
    proyectos = Proyecto.objects.filter(tutor_email=request.user.username, estado='SOL')
    #proyectos por poner nota.
    proyectos_por_calificar = Proyecto.objects.filter(tutor_email=request.user.username, estado='REV')    
    print proyectos_por_calificar
    t = loader.get_template('subirproyectos/mostrarlistatutor.html')
    c = Context({
        'proyectos': proyectos,
        'proyectos_por_calificar': proyectos_por_calificar,
    })
    return HttpResponse(t.render(c))
    
def mostrarlistabiblioteca(request):
    if not request.user.is_authenticated():
       return HttpResponseRedirect('/subirproyectos/')
    proyectos = Proyecto.objects.filter(estado='CAL')#comprobar que es de la facultad
    #if is_faculty_staff (request.user.username):
       #proyectos = Proyecto.objects.filter(centro=get_faculty(request.user.username),estado=3)
       
    t = loader.get_template('subirproyectos/mostrarlistabiblioteca.html')
    c = Context({
        'proyectos': proyectos,
    })
    return HttpResponse(t.render(c))


def revisar(request):
   print request.POST['id']
   proyecto = Proyecto.objects.get(id = request.POST['id'])
   proyecto.estado = 'REV'
   proyecto.tutor_nombre = request.POST['tutor_nombre']
   proyecto.tutor_apellidos = request.POST['tutor_apellidos']
   proyecto.director_nombre = request.POST['director_nombre']
   proyecto.director_apellidos = request.POST['director_apellidos']   
   proyecto.save()
   #dir = proyecto.alumno + '@ull.es'
   send_mail('ULL: PFC validado', 'El tutor ha validado tu proyecto.', 'from@example.com',
    ['nombre@alfrescoull.org'], fail_silently=False)

   #correo a biblioteca avisando
   return HttpResponseRedirect('/subirproyectos/results/')
   
def rechazar(request):
   print request.POST['id']
   proyecto = Proyecto.objects.get(id = request.POST['id'])
   proyecto.estado = 'error'
   proyecto.save()
   send_mail('ULL: PFC no validado', 'El tutor no ha validado tu proyecto. Ponte en contacto con el', 'from@example.com',
    ['nombre@alfrescoull.org'], fail_silently=False)
   return HttpResponseRedirect('/subirproyectos/results/')
   
def calificar_proyecto_tutor(request, id):#TODO El codigo en caso de hacerse un post nunca se ejecuta
    p = Proyecto.objects.get(id = id)
    #pc = p.proyectocalificado
    if request.method == 'POST': 
        form_proyecto_calificado = FormularioProyectoCalificado(request.POST) 
        if form_proyecto_calificado.is_valid(): 
	    p.proyectocalificado = form_proyecto_calificado.save(commit=False)
	    vocales_formset = VocalesFormSet (request.POST, instance = pc)
	    if vocales_formset.is_valid():
		p.estado = 'CAL'
		#TODO save project. update
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
    
   
def archivar_proyecto_biblioteca(request, id):#TODO mostrar los values de los campos que hay que revisar en el template
    pc = ProyectoCalificado.objects.get(id = id)
    if request.method == 'POST': # If the form has been submitted...
	form = FormularioProyectoArchivado(request.POST) # A form bound to the POST data
	if form.is_valid(): # All validation rules pass
	    pc.proyectoarchivado = form.save(commit=False)
            # Process the data in form.cleaned_data
            # ...
            pc.estado = 'ARC'
            pc.save()
	    return HttpResponseRedirect('/subirproyectos/results/') # Redirect after POST
    else:
	form = FormularioProyectoArchivado() # An unbound form

    return render_to_response('subirproyectos/archivar_proyecto_biblioteca.html', {
        'f': form,
    })
   
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
