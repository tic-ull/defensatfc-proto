# -*- encoding: utf-8 -*-

from subirproyectos.alfresco import Alfresco


#http://127.0.0.1:8080/alfresco/upload/workspace/SpacesStore/0000-0000-0000-0000/myfile.pdf






def handle_uploaded_file(f,p):
    alfresco = Alfresco ()
    uuid = alfresco.subir_pfc (f,p)
    ##print alfresco.url_bajar_pfc ('92c53631-5e74-47f0-8f8b-cec5ddcb1e42')
    alfresco.terminar_sesion()
    return uuid