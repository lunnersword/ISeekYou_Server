__author__ = 'lunner'

from twisted.enterprise import adbapi
from zope.interface import implements, Interface
from twisted.cred import checkers, credentials, portal
import hashlib

def hash(password):
    return hashlib.sha1(password).hexdigest()


class IProtocolAvatar(Interface):
    def logout(self):
        '''
        Clean up per-login resources allocated to this avator
        :return:
        '''

class ChatAvatar(object):
    implements(IProtocolAvatar)
    def logout(self):
        pass

class Realm(object):
    implements(portal.IRealm)
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IProtocolAvatar in interfaces:
            avatar = ChatAvatar
            return IProtocolAvatar, avatar, avatar.logout
        raise NotImplementedError("This realm only supports the IProtocolAvator interfaces")

realm = Realm()
loginPortal = portal.Portal(realm)
"""
loginChecker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
loginChecker.addUser('super', hash('super'))
loginChecker.addUser('lunner', hash('lunner'))
loginChecker.addUser('user', hash('pass'))
"""


from login_db_checker import DBCredentialsChecker

dbpool = adbapi.ConnectionPool("sqlite3", "ISU_server.db")
loginChecker = DBCredentialsChecker(dbpool.runQuery, query='SELECT ISUname, password FROM users WHERE ISUname = ?')


loginPortal.registerChecker(loginChecker)
