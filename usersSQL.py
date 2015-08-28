__author__ = 'lunner'

from twisted.enterprise import adbapi
from twisted.internet import reactor
from globalName import *

dbpool = adbapi.ConnectionPool("sqlite3", "ISU_server.db")


def queryPassword(ISUname):
    return dbpool.runQuery("SELECT password FROM users WHERE ISUname = ?", (ISUname, ))

def printPassword(results): #list
    print type(results)
    for elt in results:
        print type(elt) # tuple
        print elt[0]

def addUser(user):
    ISUname, nickname, password, email, signature, sex, phone, city = user
    return dbpool.runOperation("INSERT INTO users (ISUname, nickname, password, email, signature, sex, phone, city) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                        (ISUname, nickname, password, email, signature, sex, phone, city))
'''
def addUser(user):
    return dbpool.runInteraction(_addUser, user)
'''
def removeUserByISUname(ISUname):
    return dbpool.runOperation("DELETE FROM users where ISUname = ?", (ISUname,))
def handleRemoveUserSuccess():
    print 'Success'

def handleRemoveUserFailure(failure):
    print 'remove failure:', failure


def handleAddUserSuccess(result):
    print 'Success'

def handleAddUserFailure(failure):
    print 'Failure: %s' % (failure)
    #if isinstance(failure, str): #it is twisted.python.failure.Failure
    failure = failure.getErrorMessage()
    try:
        failure.index("UNIQUE constraint failed")
    except ValueError, e:
        print 'other'

    else:
        print 'exists'




'''
user = {ISUname = 'super',
        nickname = None,
        password = '8451ba8a14d79753d34cb33b51ba46b4b025eb81',
        email = None,
        signature,
        sex,
        phone,
        city,
        photo}
        '''
user = ['super',None, '8451ba8a14d79753d34cb33b51ba46b4b025eb81',
        None, None, None,
        None, None]
#d = addUser(user)
#d.addCallbacks(handleAddUserSuccess, handleAddUserFailure) #if success return None -> d == None
p = removeUserByISUname('super')
p.addCallbacks(handleRemoveUserSuccess, handleRemoveUserFailure)

d = queryPassword('lunner')
d.addCallback(printPassword)

#dbpool.close()
reactor.run()