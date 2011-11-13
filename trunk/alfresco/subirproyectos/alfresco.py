  # -*- encoding: utf-8 -*-
import logging
import put
import urllib2

from datetime import datetime, timedelta

from suds import wsse
from suds.client import Client

from subirproyectos import settings


logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO)


class Alfresco(object):
    NAME_PROPERTY = 'cm:name'
    NAMESPACES = {
        'cm': '{http://www.alfresco.org/model/content/1.0}%s',
        'content': '{http://www.alfresco.org/ws/model/content/1.0}%s',
        'cml': '{http://www.alfresco.org/ws/cml/1.0}%s',
        'rep': '{http://www.alfresco.org/ws/service/repository/1.0}%s',
    }

    _instance = None

    def __new__(cls, *args, **kargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kargs)
        return cls._instance

    def __init__(self, username=settings.ALFRESCO_USERNAME,
                 password=settings.ALFRESCO_PASSWORD,
                 proxy=settings.ALFRESCO_PROXY_SERVER):
        # Autenticación
        self._client = Client(settings.ALFRESCO_URL_AUTH_SERVICE, proxy=proxy)
        login_result = self._client.service.startSession(username, password)
        self._ticket = login_result['ticket']

        # Preparar WS-Security
        token = wsse.UsernameToken(username, self._ticket)
        timestamp = wsse.Timestamp()
        self._security = wsse.Security()
        self._security.tokens.append(timestamp)
        self._security.tokens.append(token)
 
        # WS del repositorio
        self._repository = Client(settings.ALFRESCO_URL_RESPOSITORY_SERVICE, proxy=proxy)
        self._repository.set_options(wsse=self._security)

    def __del__(self):
        self._client.service.endSession(self.ticket)

    def upload_content(self, uuid, file_object, file_name=None):
        if file_name is None:
            if hasattr(file_object, 'name'):
                name = file_object.name
            else:
                name = 'file'
        else:
            name = file_name

        url = settings.ALFRESCO_URL_PUT % {
            'uuid': uuid, 
            'filename': name,
            'ticket': self._ticket
        }
        return put.putfile(file_object, url)

    def get_download_url(self, uuid):
        return settings.ALFRESCO_URL_DOWN % {
            'uuid': uuid,
            'filename': 'file',
            'ticket': self._ticket
        }

    def download_content(self, uuid):
        proxy_type = settings.ALFRESCO_PROXY_SERVER.iterkeys().next()
        proxy_host = settings.ALFRESCO_PROXY_SERVER[proxy_type]
        request = urllib2.Request(self.get_download_url(uuid))
        request.set_proxy(proxy_host, proxy_type)
        return urlopen(request)

    def cml(self):
        return CML(self)


class CML(object):
    NAME_PROPERTY = Alfresco.NAME_PROPERTY
    NAMESPACES = Alfresco.NAMESPACES

    def __init__(self, alfresco):
        self._repository = alfresco._repository
        self._callbacks = []
        self.cml = self._repository.factory.create(self.NAMESPACES['cml'] % 'cml')

    def create(self, parent_uuid, content_type, properties={}, callback=None):
        # Obtener la referencia al nodo padre
        store = self._repository.factory.create(self.NAMESPACES['content'] % 'Store')
        store.scheme = 'workspace'
        store.address = 'SpacesStore'
        parent_reference = self._repository.factory.create(self.NAMESPACES['content'] % 'ParentReference')
        parent_reference.associationType = self.NAMESPACES['cm'] % 'contains'
        parent_reference.childName = self.NAMESPACES['cm'] % properties['{http://www.alfresco.org/model/content/1.0}name']
        parent_reference.uuid = parent_uuid
        parent_reference.store = store

        # create
        create = self._repository.factory.create(self.NAMESPACES['cml'] % 'create')
        create.id = '1'
        create.type = content_type
        create.parent = parent_reference

        # Cargar las propiedades del nuevo elemento
        for name, value in properties.iteritems():
            named_value = self._repository.factory.create(self.NAMESPACES['content'] % 'NamedValue')
            named_value.name = name
            if type(value) in (list, tuple):
                named_value.values = value
                named_value.isMultiValue = True
            else:
                named_value.value = value
                named_value.isMultiValue = False
            create.property.append(named_value)

        # Añadir la operación
        self.cml.create.append(create)
        self._callbacks.append(callback)
        return self

    def add_aspect(self, uuid, aspect, properties={}, callback=None):
        predicate = self._repository.factory.create(self.NAMESPACES['content'] % 'Predicate')
        predicate.nodes = self._get_reference(uuid)

        add_aspect = self._repository.factory.create(self.NAMESPACES['cml'] % 'addAspect')
        add_aspect.aspect = aspect
        add_aspect.where = predicate

        # Cargar las propiedades en el aspect
        for name, value in properties.iteritems():
            named_value = self._repository.factory.create(self.NAMESPACES['content'] % 'NamedValue')
            named_value.name = name
            if type(value) in (list, tuple):
                named_value.values = value
                named_value.isMultiValue = True
            else:
                named_value.value = value
                named_value.isMultiValue = False
            add_aspect.property.append(named_value)

        self.cml.addAspect.append(add_aspect)
        self._callbacks.append(callback)
        return self

    def update(self, uuid, properties, callback=None):
        predicate = self._repository.factory.create(self.NAMESPACES['content'] % 'Predicate')
        predicate.nodes = self._get_reference(uuid)

        update = self._repository.factory.create(self.NAMESPACES['cml'] % 'update')
        update.where = predicate

        # Cargar las propiedades en el aspect
        for name, value in properties.iteritems():
            named_value = self._repository.factory.create(self.NAMESPACES['content'] % 'NamedValue')
            named_value.name = name
            if type(value) in (list, tuple):
                named_value.values = value
                named_value.isMultiValue = True
            else:
                named_value.value = value
                named_value.isMultiValue = False
            update.property.append(named_value)

        self.cml.update.append(update)
        self._callbacks.append(callback)
        return self

    def delete(self, uuid, callback=None):
        predicate = self._repository.factory.create(self.NAMESPACES['content'] % 'Predicate')
        predicate.nodes = self._get_reference(uuid)

        delete = self._repository.factory.create(self.NAMESPACES['cml'] % 'delete')
        delete.where = predicate

        self.cml.update.append(delete)
        self.callbacks.append(callback)
        return self

    def do(self):
        results = self._repository.service.update(self.cml)
        for result, callback in zip(results, self._callbacks):
            if callback is not None:
                callback(result)
        return results

    def _get_reference(self, uuid):
        store = self._repository.factory.create(self.NAMESPACES['content'] % 'Store')
        store.scheme = 'workspace'
        store.address = 'SpacesStore'

        reference = self._repository.factory.create(self.NAMESPACES['content'] % 'Reference')
        reference.uuid = uuid
        reference.store = store

        return reference

