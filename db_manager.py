__author__ = 'lunner'

from twisted.enterprise import adbapi
from twisted.internet.defer import Deferred
import globalName
import error

class DataManager:
    dbpool = adbapi.ConnectionPool("sqlite3", "ISU_server.db")


    def _createUserFriendsTable(self, transaction, username):
        transaction.execute("CREATE TABLE " + username + "Friends (ISUname char(12) references users(ISUname) on delete cascade, myGroup nchar(12), maked char(1))")

    def createUserFriendsTable(self, username):
        return self.dbpool.runInteraction(self._createUserFriendsTable, username)



    def addUser(self, user):
        '''
        insert a record into users table.
        :param user: parameter user should have 8 columns, None column for NULL
        :return: a deferred
        '''
        ISUname, nickname, password, email, signature, sex, phone, city = user
        dbDeferred = self.dbpool.runOperation("INSERT INTO users (ISUname, nickname, password, email, signature, sex, phone, city) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                            (ISUname, nickname, password, email, signature, sex, phone, city))
        deferred = Deferred()
        dbDeferred.addCallbacks(self._cbAddUser, self._ebAddUser, callbackArgs=(ISUname, password, deferred), errbackArgs=(deferred,))

        return deferred

    def _cbAddUser(self, result, username, password, deferred):

        deferred.callback((username, password))

    def _ebAddUser(self, failure, deferred):
        if globalName.debug:
            print 'Insert into users Failure: %s' % (failure,)
        failure = failure.getErrorMessage()
        try:
            failure.index("UNIQUE constraint failed")
        except ValueError, e:
            deferred.errback(error.DatabaseOperationFailed(globalName.failure)) #
        else:
            if globalName.debug:
                print "UNIQUE constraint"
            deferred.errback(error.DatabaseOperationFailed(globalName.exists))


    def removeUser(self, ISUname):

        return self.dbpool.runOperation("DELETE FROM users WHERE  ISUname = ?", (ISUname,))

    def queryAll(self, ISUname):
        return self.dbpool.runQuery("SELECT * FROM users WHERE ISUname = ?", (ISUname,))

    def queryPassword(self, ISUname):
        return self.dbpool.runQuery("SELECT password FROM users WHERE ISUname = ?", (ISUname, ))


