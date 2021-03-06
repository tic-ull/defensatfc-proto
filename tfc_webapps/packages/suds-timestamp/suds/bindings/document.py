# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jeff Ortel ( jortel@redhat.com )

"""
Provides classes for the (WS) SOAP I{document/literal}.
"""

from logging import getLogger
from suds import *
from suds.bindings.binding import Binding
from suds.sax.element import Element

log = getLogger(__name__)


class Document(Binding):
    """
    The document/literal style.  Literal is the only (@use) supported
    since document/encoded is pretty much dead.
    Although the soap specification supports multiple documents within the soap
    <body/>, it is very uncommon.  As such, suds presents an I{RPC} view of
    service methods defined with a single document parameter.  This is done so 
    that the user can pass individual parameters instead of one, single document.
    To support the complete specification, service methods defined with multiple documents
    (multiple message parts), must present a I{document} view for that method.
    """
        
    def bodycontent(self, method, args, kwargs):
        """
        Get the content for the soap I{body} node.
        The I{wrapped} vs I{bare} style is detected in 2 ways.
        If there is 2+ parts in the message then it is I{bare}.
        If there is only (1) part and that part resolves to a builtin then
        it is I{bare}.  Otherwise, it is I{wrapped}.
        @param method: A service method.
        @type method: I{service.Method}
        @param args: method parameter values
        @type args: list
        @param kwargs: Named (keyword) args for the method invoked.
        @type kwargs: dict
        @return: The xml content for the <body/>
        @rtype: [L{Element},..]
        """
        if not len(method.message.input.parts):
            return ()
        wrapped = method.message.input.wrapped
        if wrapped:
            pts = self.bodypart_types(method)
            root = self.document(pts[0])
        else:
            root = []
        n = 0
        for pd in self.param_defs(method):
            if n < len(args):
                value = args[n]
            else:
                value = kwargs.get(pd[0])
            n += 1
            p = self.mkparam(method, pd, value)
            if p is None:
                continue
            if not wrapped:
                ns = pd[1].namespace('ns0')
                p.setPrefix(ns[0], ns[1])
            root.append(p)
        return root

    def replycontent(self, method, body):
        """
        Get the reply body content.
        @param method: A service method.
        @type method: I{service.Method}
        @param body: The soap body
        @type body: L{Element}
        @return: the body content
        @rtype: [L{Element},...]
        """
        wrapped = method.message.output.wrapped
        if wrapped:
            return body[0].children
        else:
            return body.children
        
    def document(self, wrapper):
        """
        Get the document root.  For I{document/literal}, this is the
        name of the wrapper element qualifed by the schema tns.
        @param wrapper: The method name.
        @type wrapper: L{xsd.sxbase.SchemaObject}
        @return: A root element.
        @rtype: L{Element}
        """
        tag = wrapper[1].name
        ns = wrapper[1].namespace('ns0')
        d = Element(tag, ns=ns)
        return d
        
    def param_defs(self, method):
        """
        Get parameter definitions for document literal.
        The I{wrapped} vs I{bare} style is detected in 2 ways.
        If there is 2+ parts in the message then it is I{bare}.
        If there is only (1) part and that part resolves to a builtin then
        it is I{bare}.  Otherwise, it is I{wrapped}.
        @param method: A method name.
        @type method: basestring
        @return: A collection of parameter definitions
        @rtype: [(str, L{xsd.sxbase.SchemaObject}),..]
        """
        pts = self.bodypart_types(method)
        wrapped = method.message.input.wrapped
        if not wrapped:
            return pts
        result = []
        for p in pts:
            resolved = p[1].resolve()
            for child, ancestry in resolved:
                result.append((child.name, child))
        return result
    
    def returned_types(self, method):
        """
        Get the referenced type returned by the I{method}.
        @param method: The name of a method.
        @type method: str
        @return: The name of the type return by the method.
        @rtype: [L{xsd.sxbase.SchemaObject}]
        """
        result = []
        wrapped = method.message.output.wrapped
        rts = self.bodypart_types(method, input=False)
        if wrapped:
            for pt in rts:
                resolved = pt.resolve(nobuiltin=True)
                for child, ancestry in resolved:
                    result.append(child)
                break
        else:
            result += rts
        return result