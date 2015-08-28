__author__ = 'lunner'

from twisted.internet import reactor, threads, protocol

from zope.interface import implements, Interface
from twisted.cred import checkers, credentials, portal
from twisted.cred import error
from twisted.protocols import basic
from db_manager import DataManager
import time


import globalName


from login_cred import *

dataManager = DataManager()

def pushToSendPool(data):
    pass



class ChatFactory(protocol.Factory):

    commands = {'msg': 'M',
                'login': 'L',
                'channel-msg': 'G',
                'logout': 'O',
                'register': 'R'}
    def __init__(self, loginPortal):
        self.userProtocols = {}
        self.loginPortal = loginPortal


    def buildProtocol(self, addr):
        protocol = ChatProtocal(self)
        protocol.loginPortal = self.loginPortal
        return protocol

class ChatProtocal(basic.LineReceiver):
    loginPortal = None # type property
    avatar = None
    logout = None

    def __init__(self, factory):
        #self.data = ''
        self.factory = factory
        self.name = None
        self.avatar = None
        self.logout = None
        self.clientType = globalName.phone # TODO: add multiple clients
        self.clientDescriptor = ''

        #commands as instance property or as as class property ?
        self.commands = {}
        self.commands[self.factory.commands['msg']] = self.sendMessageToPerson
        self.commands[self.factory.commands['login']] = self.tryLogin
        self.commands[self.factory.commands['register']] = self.tryRegister

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        if self.logout:
            if self.avatar:
                self.logout(self.avater)
            self.avatar = None
            self.logout = None
    def lineReceived(self, line):
        print line
        self.parseData(line)

    def getProtocol(self, receiver):
        assert isinstance(receiver, str)
        return self.factory.userProtocols.get(receiver)

    @classmethod
    def sendMessage(cls, protocol, msg):
        assert isinstance(protocol, ChatProtocal)
        #protocol.transport.write(msg)
        protocol.sendLine(msg)
    def sendMessageToPerson(self, data):
        sender, receiver, rawMsg = data.split(' ', 2)
        # here sender can get from self.name, but we get it from the msg data
        '''
        msg, rawTime = rawMsg.split(':')
        (_, time) = rawTime.split(' ')
        '''
        #assert isinstance(receiver, object)
        protocol = self.getProtocol(receiver)
        if protocol:
            newMsg = self.factory.commands['msg'] + ' ' + sender + ' ' + rawMsg
            if globalName.debug:
                print newMsg
            #protocol.transport.write(newMsg)
            ChatProtocal.sendMessage(protocol, newMsg)
        else:
            #receiver is not online
            assert isinstance(data, str)
            pushToSendPool(data)

    def tryRegister(self, data):
        params = data.split(' ')
        username = params[0]
        password = params[1] # username and password is not null, client's response to check it.
        # TODO:
        # check whether username exists, if exists
        if globalName.debug:
            print username, password
        #ISUname, nickname, password, email, signature, sex, phone, city
        user = (username, None, hash(password), None,
                None, None, None, None)
        deferred = dataManager.addUser(user)
        deferred.addCallbacks(self._cbRegister, self._ebRegister)

    def _cbRegister(self, data):
        #register success, tell client
        (username, password) = data
        msg = self.factory.commands["register"] + globalName.space + globalName.success + globalName.space + globalName.eol + globalName.space
        # do something to user, such as create user's friends table.
        dataManager.createUserFriendsTable(username) # TODO: handle errors
        self.name = username
        self.sendLine(msg)
        self.loginPortal.login(credentials.UsernameHashedPassword(username, password), None, IProtocolAvatar).addCallbacks(self._cbLogin, self._ebLogin)

    def _ebRegister(self, failure):
        errorMessage = failure.getErrorMessage()
        #msg = ''
        if errorMessage == globalName.failure:
            msg = self.factory.commands["register"] + globalName.space + globalName.failure + globalName.wrapEOL
        elif errorMessage == globalName.exists:
            msg = self.factory.commands["register"] + globalName.space + globalName.exists + globalName.wrapEOL
        if globalName.debug:
            print msg
        self.sendLine(msg)
        self.transport.loseConnection()


    def tryLogin(self, data):
        params = data.split(' ')
        username = params[0]
        password = params[1]
        #loginPortal.login(credentials.UsernameHashedPassword(username, hash(password)), None, IProtocalAvatar).addCallback(self._cbLogin, self._ebLogin)
        if globalName.debug:
            print username, password
        # TODO: to support multiple clients, check whether a username's client is logined.
        self.name = username
        self.loginPortal.login(credentials.UsernameHashedPassword(username, hash(password)), None, IProtocolAvatar).addCallbacks(self._cbLogin, self._ebLogin)
        #self._cbLogin((None, None, None))
        #self.loginPortal.login(credentials.UsernameHashedPassword(username, hash(password)), None, IProtocolAvatar).addCallback(self._cbLogin, self._ebLogin)
    def _cbLogin(self, (interface, avatar, logout), other = None):
        self.avatar = avatar
        self.logout = logout
        self.factory.userProtocols[self.name] = self
        msg = self.factory.commands["login"] + " " + "success" + " " + ":EOL" + " "
        self.sendLine(msg)
        #self.transport.write(msg)
    def _ebLogin(self, failure):
        if type(failure.type) == type(error.UnauthorizedLogin):
            errorMessage = failure.getErrorMessage()
            if errorMessage == 'User not in database':
                msg = self.factory.commands['login'] + " " + 'inexistence' + ' ' + ':EOL' + ' '
            elif errorMessage == 'Password mismatch':
                msg = self.factory.commands['login'] + ' ' + 'mismatch' + ' ' + ':EOL' + ' '

        else:
            msg = self.factory.commands["login"] + " " + 'failure' + ' ' + ':EOL' + ' '
        self.sendLine(msg)
        #self.transport.write(msg)
        if globalName.debug:
            print(msg)
            print failure

        #time.sleep(2)
        self.transport.loseConnection()
        #reactor.stop()

    def parseData(self, data):

        #params = data.split(' ')


        if data[0][0] != ":":
            command, reminder = data.split(' ', 1)
            if not self.avatar:
                if command != 'L' and command != 'R':
                    msg = self.factory.commands["login"] + globalName.space + "please" + globalName.space + globalName.eol + globalName.space
                    self.sendLine(msg)
                else:
                    self.commands[command](reminder)
            else:
                self.commands[command](reminder)



reactor.listenTCP(7777, ChatFactory(loginPortal))
reactor.run()