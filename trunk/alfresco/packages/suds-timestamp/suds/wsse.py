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
The I{wsse} module provides WS-Security.

See: http://www.oasis-open.org/committees/tc_home.php?wg_abbrev=wss
"""

from logging import getLogger
from suds import *
from suds.sudsobject import Object
from suds.sax.element import Element
from datetime import datetime, timedelta
try:
    from hashlib import md5
except ImportError:
    # Python 2.4 compatibility
    from md5 import md5


dsns = \
    ('ds',
     'http://www.w3.org/2000/09/xmldsig#')
wssens = \
    ('wsse', 
     'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd')
wsuns = \
    ('wsu',
     'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd')
wsencns = \
    ('wsenc',
     'http://www.w3.org/2001/04/xmlenc#')

PASSWORD_TYPES = {
    'plain': "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText",
}

class Security(Object):
    """
    WS-Security object.
    @ivar tokens: A list of security tokens
    @type tokens: [L{Token},...]
    @ivar timestamp: Whether or not to attach a Security Timestamp
    @type timestamp: bool
    @ivar signatures: A list of signatures.
    @type signatures: TBD
    @ivar references: A list of references.
    @type references: TBD
    @ivar keys: A list of encryption keys.
    @type keys: TBD
    """
    
    def __init__(self, timestamp=False):
        """
        Create a new WS-Security object.
        @param timestamp: Whether or not to create a Security Timestamp
        @type timestamp: bool
        """
        Object.__init__(self)
        self.mustUnderstand = True
        self.timestamp = timestamp
        self.tokens = []
        self.signatures = []
        self.references = []
        self.keys = []
        
    def xml(self):
        """
        Get xml representation of the object.
        @return: The root node.
        @rtype: L{Element}
        """
        root = Element('Security', ns=wssens)
        root.set('mustUnderstand', 1 if self.mustUnderstand else 0)
        if self.timestamp:
            root.append(Timestamp().xml())
        for t in self.tokens:
            root.append(t.xml())
        return root


class Token(Object):
    """ I{Abstract} security token. """
    
    def __init__(self):
            Object.__init__(self)


class UsernameToken(Token):
    """
    Represents a basic I{UsernameToken} WS-Secuirty token.
    @ivar username: A username.
    @type username: str
    @ivar password: A password.
    @type password: str
    @ivar nonce: A set of bytes to prevent reply attacks.
    @type nonce: str
    @ivar created: The token created.
    @type created: L{datetime}
    """
    
    @classmethod
    def now(cls):
        return datetime.now()
    
    @classmethod
    def sysdate(cls):
        return cls.now().isoformat()

    def __init__(self, username=None, password=None):
        """
        @param username: A username.
        @type username: str
        @param password: A password.
        @type password: str
        """
        Token.__init__(self)
        self.username = username
        self.password = password
        self.nonce = None
        self.created = None
        
    def setnonce(self, text=None):
        """
        Set I{nonce} which is arbitraty set of bytes to prevent
        reply attacks.
        @param text: The nonce text value.
            Generated when I{None}.
        @type text: str
        """
        if text is None:
            s = []
            s.append(self.username)
            s.append(self.password)
            s.append(self.sysdate())
            m = md5()
            m.update(':'.join(s))
            self.nonce = m.hexdigest()
        else:
            self.nonce = text
        
    def setcreated(self, dt=None):
        """
        Set I{created}.
        @param dt: The created date & time.
            Set as datetime.now() when I{None}.
        @type dt: L{datetime}
        """
        if dt is None:
            self.created = self.now()
        else:
            self.created = dt
        
        
    def xml(self):
        """
        Get xml representation of the object.
        @return: The root node.
        @rtype: L{Element}
        """
        root = Element('UsernameToken', ns=wssens)
        root.set('wsu:Id', 'UsernameToken-%i' % hash(self))
        u = Element('Username', ns=wssens)
        u.setText(self.username)
        root.append(u)
        p = Element('Password', ns=wssens)
        p.setText(self.password)
        # The Type attribute defaults to PasswordText, but some endpoints
        # seem to want it specified anyway.
        p.set('Type', PASSWORD_TYPES['plain'])
        root.append(p)
        if self.nonce is not None:
            n = Element('Nonce', ns=wssens)
            n.setText(self.nonce)
            root.append(n)
        if self.created is not None:
            n = Element('Created', ns=wsuns)
            n.setText(self.created.isoformat())
            root.append(n)
        return root

class Timestamp(Object):
    """
    Represents a Timestamp WS-Secuirty object.
    @ivar created: When the security semantics were creaetd.
    @type created: L{datetime}
    @ivar expires: When the security semantics should expire.
    @type expires: L{datetime}
    """

    def __init__(self, expires=True):
        """
        @param expires: Add optional expiration date
        @type expires: bool
        """
        super(Timestamp, self).__init__()
        self.created = datetime.utcnow()

        if expires:
            # The example in the spec uses 1 month, so why not?
            self.expires = self.created + timedelta(days=30)
        else:
            self.expires = None

    def xml(self):
        """
        Get xml representation of the object.
        @return: The root node.
        @rtype: L{Element}
        """
        root = Element('Timestamp', ns=wsuns)
        root.set('wsu:Id', 'Timestamp-%i' % hash(self))
        c = Element('Created', ns=wsuns)
        c.setText(self.created.isoformat())
        root.append(c)
        if self.expires:
            e = Element('Expires', ns=wsuns)
            e.setText(self.expires.isoformat())
            root.append(e)
        return root
