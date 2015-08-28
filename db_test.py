__author__ = 'lunner'
from twisted.enterprise import adbapi
from twisted.internet import reactor

dbpool = adbapi.ConnectionPool("sqlite3", 'ISU_server.db')

def _createUsersTable(transaction, users):
    transaction.execute("CREATE TABLE users (email TEXT, name TEXT)")
    for email, name in users:
        transaction.execute("INSERT INTO users (email, name) VALUES(?, ?)", (email, name))


def createUsersTable(users):
    return dbpool.runInteraction(_createUsersTable, users)

def getByName(name):
    return dbpool.runQuery("SELECT * FROM users WHERE ISUname = ?", (name, ))

def printResults(results):
    for elt in results:
        print elt
def printFailure(failure):
    print failure

def finish():
    dbpool.close()
    reactor.stop()

users = [("jane@foo.com", "jane"), ("joel@foo.com", "joel")]
#d = createUsersTable(users)
#d.addCallback(lambda x: getByName("lunner"))
#d.addCallback(printResults)
d = getByName('lunner')
d.addCallback(printResults)
d.addErrback(printFailure)
#reactor.callLater(1, finish)
reactor.run()