from defensa.alfresco import Alfresco




def url_download_file(uuid):
    alfresco = Alfresco ()
    ruta = alfresco.url_bajar_pfc (uuid)
    #alfresco.terminar_sesion()
    return ruta
