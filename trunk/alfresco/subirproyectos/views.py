from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from subirproyectos.forms import *
from django.template import RequestContext, Context, loader
from subirproyectos.handle_uploaded_file import handle_uploaded_file
from subirproyectos.url_download_file import url_download_file 
from suds.client import Client
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required
from subirproyectos.ull import *
from subirproyectos.models import Proyecto, Anexo
from django.core.mail import send_mail
from subirproyectos.alfresco import Alfresco
from django.forms.models import inlineformset_factory, formset_factory





def index(request):
    f = FormularioLogin()
    return render_to_response('subirproyectos/index.html', {'f': f},
                               context_instance=RequestContext(request))
                               
                               
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            print "You provided a correct username and password!"
            if is_student(request.user.username):
	       return HttpResponseRedirect('/subirproyectos/subir/')
            if is_library_staff (request.user.username):
	       return HttpResponseRedirect('/subirproyectos/mostrarlistabiblioteca/')
            #if is_faculty_staff (request.user.username):
	       #return HttpResponseRedirect('/subirproyectos/mostrarlista/')
	    if is_professor (request.user.username):
	       return HttpResponseRedirect('/subirproyectos/mostrarlistatutor/')
            #si eres alumno goto formulario
            

            #si eres otra cosa goto mostrarlista
        else:
	    print "Your account has been disabled!"
            # Return a 'disabled account' error message
    else:
        print "Your username and password were incorrect."
        # Return an 'invalid login' error message.
        
def logout_view(request):
    logout(request)


   
def formulario(request):
    ##necesita estar logueado
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/subirproyectos/')
    f = FormularioProyecto()
    return render_to_response('subirproyectos/subir.html', {'f': f},
                               context_instance=RequestContext(request))
    
def result(request):
    return HttpResponse("Ha sido exitoso.")
    
        
def subir(request):
    #AnexoFormSet = formset_factory(AnexoForm, formset=FormularioAnexoFormSet)
    #AnexoFormSet = inlineformset_factory(Proyecto, Anexo, formset = FormularioAnexoFormset, fields=('title', 'file', 'proyecto'))  
    if request.method == 'POST':

        #proyecto_form = FormularioProyecto(request.POST, request.FILES)
        proyecto_form = FormularioProyecto(request.POST, request.FILES)
        #anexo_formset = AnexoFormSet(request.POST, request.FILES)

        if proyecto_form.is_valid(): 
	    proyecto = proyecto_form.save(commit=False)
	    anexo_formset = AnexoFormSet (request.POST, request.FILES, instance = proyecto)
	    if anexo_formset.is_valid():
		proyecto.save()
		anexo_formset.save()
		proyecto.uuid = handle_uploaded_file(request.FILES['file'], proyecto) 
		proyecto.save()
            #anexo_formset.save()
	    
	    #p = Proyecto()
	    #p.title = request.POST['title']
	    #p.creator = request.POST['creator']
	    #p.description = request.POST['description']
	    #p.language = request.POST['language']
	    #p.niu = request.POST['niu']
	    #p.tutor = request.POST['tutor']
	    #p.centro = request.POST['centro']
	    #p.titulacion = request.POST['titulacion']
	    ##p.universidad = request.POST['universidad']
	    #p.estado = '1'
	    #p.uuid = handle_uploaded_file(request.FILES['file'], p) 
	    #p.save()
            return HttpResponseRedirect('/subirproyectos/results/')
    else:
        #proyecto_form = FormularioProyecto(request.POST, request.FILES)
        proyecto_form = FormularioProyecto()
        anexo_formset = AnexoFormSet(instance = Proyecto())
    return render_to_response('subirproyectos/subir.html', {'f': proyecto_form, 'a' : anexo_formset }, context_instance=RequestContext(request))


def mostrar(request, id):
    p = Proyecto.objects.get(id = id)
    if p.estado == '1':
        url = url_download_file(p.uuid)
	return render_to_response('subirproyectos/mostrar.html', {'p': p, 'url' : url})
    if p.estado == '2':
        return render_to_response('subirproyectos/mostrar_tutor.html', {'p': p})
    if p.estado == '3':    
        return render_to_response('subirproyectos/mostrar_biblioteca.html', {'p': p})


def mostrarlistatutor(request):
    if not request.user.is_authenticated():
       return HttpResponseRedirect('/subirproyectos/')
    proyectos = Proyecto.objects.filter(tutor=request.user.username, estado=1)
    proyectos_por_leer = Proyecto.objects.filter(tutor=request.user.username, estado=2)
    #if is_faculty_staff (request.user.username):
       #proyectos = Proyecto.objects.filter(centro=get_faculty(request.user.username),estado=3)
       
    t = loader.get_template('subirproyectos/mostrarlistatutor.html')
    c = Context({
        'proyectos': proyectos,
        'proyectos_por_leer': proyectos_por_leer,
    })
    return HttpResponse(t.render(c))
    
def mostrarlistabiblioteca(request):
    if not request.user.is_authenticated():
       return HttpResponseRedirect('/subirproyectos/')
    proyectos = Proyecto.objects.filter(centro=get_faculty(request.user.username),estado=3)
    #if is_faculty_staff (request.user.username):
       #proyectos = Proyecto.objects.filter(centro=get_faculty(request.user.username),estado=3)
       
    t = loader.get_template('subirproyectos/mostrarlistabiblioteca.html')
    c = Context({
        'proyectos': proyectos,
    })
    return HttpResponse(t.render(c))


def validar(request):
   print request.POST['id']
   proyecto = Proyecto.objects.get(id = request.POST['id'])
   proyecto.estado = '2'
   proyecto.tutor = request.POST['tutor']
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
   
def validar_tutor(request):
  #despues de leer el proy
   proyecto = Proyecto.objects.get(id = request.POST['id'])
   proyecto.estado = '3'
   proyecto.calificacion = request.POST['calificacion']
   proyecto.fecha = request.POST['fecha']
   proyecto.tribunal_presidente = request.POST['presidente']
   proyecto.tribunal_secretario = request.POST['secretario']
   proyecto.tribunal_vocal = request.POST['vocal']
   proyecto.save()
   #email alumno
   send_mail('ULL: PFC validado', 'Tutor ha validado tu proyecto. Listo para lectura', 'from@example.com',
    ['nombre@alfrescoull.org'], fail_silently=False)
   #correo al tutor
   #dir = proyecto.tutor + '@ull.es'
   send_mail('ULL: PFC validado', 'Tutor ha validado el proyecto', 'from@example.com',
    ['nombre@alfrescoull.org'], fail_silently=False)
   return HttpResponseRedirect('/subirproyectos/results/')
  
  
def validar_biblioteca(request):
   proyecto = Proyecto.objects.get(id = request.POST['id'])
   proyecto.estado = '4'
   proyecto.title = request.POST['title']
   proyecto.creator = request.POST['creator']
   proyecto.description = request.POST['description']
   proyecto.language = request.POST['language']
   #proyecto.rights = request.POST['rights']
   proyecto.coverage = request.POST['coverage']
   proyecto.subject = request.POST['subject']
   proyecto.save()
   alfresco = Alfresco ()
   alfresco.addMetadata (proyecto)
   return HttpResponseRedirect('/subirproyectos/results/')
   
   