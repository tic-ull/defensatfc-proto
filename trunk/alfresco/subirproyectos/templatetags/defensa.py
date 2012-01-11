from django import template

from subirproyectos import settings


register = template.Library()


class TiposDocumentosNode(template.Node):

    def render(self, context):
        tipos = [tipo[1] for tipo in settings.SELECCION_TIPO_DOCUMENTO]
        return '"' + '", "'.join(tipos[:-1]) + '" o "' + tipos[-1] + '"'

@register.tag
def tipos_documentos(parser, token):
    return TiposDocumentosNode()
