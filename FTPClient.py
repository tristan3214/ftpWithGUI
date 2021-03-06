#!/usr/bin/env python2
from __future__ import  print_function, division, absolute_import


import wx
import sys
import threading
import time

from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor

from twisted.protocols.ftp import FTPFactory
from twisted.protocols.ftp import FTPFileListProtocol
from twisted.protocols.ftp import FTPClient
from twisted.protocols.ftp import DTPFactory
from twisted.protocols.ftp import ProtocolWrapper
from twisted.protocols.policies import TimeoutMixin, ThrottlingProtocol, ThrottlingFactory

from twisted.internet import protocol
from twisted.internet import threads
from twisted.python import log

import numpy as np

transferTimes = []

class TextSend(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Request Files", size=(200, 110))

        self.protocol = None # client protocol
        self.factory = None
        
        panel = wx.Panel(self)

        vertSizer = wx.BoxSizer(wx.VERTICAL)
        horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.fileName = None
        self.textbox = wx.TextCtrl(parent=panel, id=100, size=(100,-1))
        self.btn = wx.Button(panel, label="Retr.")

        # timer and checkbox for timer
        self.timer = wx.Timer(self, id=wx.ID_ANY)
        self.check = wx.CheckBox(parent=panel, label="Start blocking")
        self.gauge = wx.Gauge(panel, range=1000)

        #Bind
        self.textbox.Bind(wx.EVT_TEXT, self.getText)
        self.btn.Bind(wx.EVT_BUTTON, self.press)
        self.check.Bind(wx.EVT_CHECKBOX, self.onCheck)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

        horzSizer.Add(self.textbox, flag=wx.ALIGN_CENTER)
        horzSizer.Add(self.btn, flag=wx.ALIGN_CENTER)

        vertSizer.Add(horzSizer, flag=wx.ALIGN_CENTER)
        vertSizer.Add(self.check, flag=wx.ALIGN_CENTER)
        vertSizer.Add(self.gauge, flag=wx.ALIGN_CENTER)

        panel.SetSizer(vertSizer)
        panel.Layout()

    def getText(self, evt):
        self.fileName = str(self.textbox.GetValue())

    def onCheck(self, evt):
        print("CHECKED")
        yes = self.check.GetValue()
        print(yes)
        if yes:
            print("Starting timer")
            #self.timer.Start(500)
            didStart = self.timer.Start(1)
            print("Started timer:", didStart)
            print("Running:", self.timer.IsRunning())
            #self.startTimer(True)
        else: # no
            self.timer.Stop()
            #self.startTimer(False)

    def onTimer(self, evt):
        #print("Triggered timer")
        max = self.gauge.GetRange()
        current = self.gauge.GetValue()
        #print(current)
        if current < max:
            self.gauge.SetValue(current+1)
        else:
            self.gauge.SetValue(0)
        pass
            
    def startTimer(self, boolean):
        if boolean:
            self.timer.Start(50)
        else:
            self.timer.Stop()
        
    def press(self, evt):
        print("Send:", self.fileName)
        self.protocol.pwd().addCallback(self.getCWD)
        self.protocol.getDirectory().addCallback(self.getCWD)
        print("Average:", np.mean(transferTimes), "and median:", np.median(transferTimes))
        #self.protocol.cwd("").addCallback(self.getCWD)
        #fileList = FTPFileListProtocol()
        #self.protocol.list(".", fileList).addCallbacks(self.printFiles, self.fail, callbackArgs=(fileList,))
        #self.protocol.retrieveFile(self.fileName, FileWriter(self.fileName), offset=0).addCallbacks(self.done, self.fail)
        #threads.deferToThread(self.protocol.retrieveFile, self.fileName, FileWriter(self.fileName), offset=0)).addCallbacks(self.done, self.fail)
        #d = threads.deferToThread(self.protocol.retrieveFile, self.fileName, FileWriter(self.fileName), offset=0)
        #d.addCallbacks(self.done, self.fail)
        d = threads.deferToThread(self.retrieve)
        d.addCallback(self.done)

    def retrieve(self):
        print(threading.current_thread())
        self.protocol.retrieveFile(self.fileName, FileWriter(self.fileName), offset=0).addCallbacks(self.done, self.fail)
        return "Done with deferToThread"
        
    def getCWD(self, msg):
        print("GOT STUFF:", msg)

    def printFiles(self, results, fileList):
        #print("MESSAGE:", results)
        for file in fileList.files:
            print('    %s: %d bytes, %s' \
              % (file['filename'], file['size'], file['date']))
        print('Total: %d files' % (len(fileList.files)))

    def done(self, msg):
        print(threading.current_thread())
        print("DONE Retrieving:", msg)
        return "STUFF"
            
    def fail(self, error):
        print('Failed. Error was:')
        print(error)


"""
class TextSend(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Request Files", size=(200, 75))

        self.protocol = None # client protocol
        self.factory = None
        
        panel = wx.Panel(self)

        vertSizer = wx.BoxSizer(wx.VERTICAL)
        horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.fileName = None
        self.textbox = wx.TextCtrl(parent=panel, id=100, size=(100,-1))
        self.btn = wx.Button(panel, label="Retr.")

        self.textbox.Bind(wx.EVT_TEXT, self.getText)
        self.btn.Bind(wx.EVT_BUTTON, self.press)

        horzSizer.Add(self.textbox, flag=wx.ALIGN_CENTER)
        horzSizer.Add(self.btn, flag=wx.ALIGN_CENTER)

        vertSizer.Add(horzSizer, flag=wx.ALIGN_CENTER)

        panel.SetSizer(vertSizer)
        panel.Layout()

    def getText(self, evt):
        self.fileName = str(self.textbox.GetValue())

    def press(self, evt):
        print("Send:", self.fileName)
        self.protocol.pwd().addCallback(self.getCWD)
        self.protocol.getDirectory().addCallback(self.getCWD)
        #self.protocol.cwd("").addCallback(self.getCWD)
        fileList = FTPFileListProtocol()
        self.protocol.list(".", fileList).addCallbacks(self.printFiles, self.fail, callbackArgs=(fileList,))
        self.protocol.retrieveFile(self.fileName, FileWriter(self.fileName), offset=0).addCallbacks(self.done, self.fail)

    def getCWD(self, msg):
        print("GOT STUFF:", msg)

    def printFiles(self, results, fileList):
        #print("MESSAGE:", results)
        for file in fileList.files:
            print('    %s: %d bytes, %s' \
              % (file['filename'], file['size'], file['date']))
        print('Total: %d files' % (len(fileList.files)))

    def done(self, msg):
        print("DONE Retrieving:", msg)
            
    def fail(self, error):
        print('Failed. Error was:')
        print(error)
"""
"""
class FileReceiver(FTPClient):

    
    def getFile(self, fileName):
        d = self.retrieveFile(fileName, FTPFile(fileName))
        d.addCallback(self.completedDownload)
    

    def completedDownload(self):
        print("COMPLETED FILE DOWNLOAD")


    def connectionMade(self, msg):
        print("CONNECTION was made:", msg)

    def startFactory(self):
        print("STARTING FACTORY")


class FileClientFactory(DTPFactory):
    def __init__(self, gui):
        self.gui = gui
        self.protocol = FileReceiver
"""     
    
"""
class FileClientFactory(FTPFactory):

    protocol = FileReceiver

    def startedConnecting(self, msg):
        print("CONNECTING:", msg)
"""

class FileReceiver(protocol.Protocol):
    def __init__(self):
        self.ftpClient = None

    
    def connectionMade(self):
        print("Connection made within protocol")
        self.ftpClient = FTPClient(username="anonymous", password="twisted@matrix.com", passive=1)
        print("Created FTP Client")
        self.ftpClient.pwd().addCallback(self.printCWD)

    def printCWD(self, msg):
        print("current working directory:", msg)


"""        
class TestFactory(FTPFactory):

    def __init__(self, gui, portal=None, userAnonymous='anonymous'):
        self.gui = gui
        self.protcol = FTPClient
        super(TestFactory, self).__init__(portal, userAnonymouos)
"""

class FileWriter(protocol.Protocol):

    def __init__(self, fileName):
        self.time = 0 - time.clock()
        self.f = open(fileName, 'wb')
        print("FROM FileWriter __init__:", threading.current_thread())

    def dataReceived(self, data):
        #print("Byte size", len(data))
        #print("FROM FileWriter dataReceived:", threading.current_thread())
        self.f.write(data)

    def connectionLost(self, reason):
        print("Writing closed and done")
        print("FROM FileWriter connectionLost:", threading.current_thread())
        self.f.close()
        self.time += time.clock()
        print("Took %.3f s to download" % self.time)
        transferTimes.append(self.time)
        

class TestClient(FTPClient, TimeoutMixin, object):

    def __init__(self, factory, username, password, passive):
        super(TestClient, self).__init__(username=username, password=password, passive=passive)
        self.factory = factory
    
    def connectionMade(self):
        print("hello")
        gui = self.factory.gui
        gui.protocol = self
        self.setTimeout(None)
    
class FileClientFactory(protocol.ClientFactory, TimeoutMixin):

    def __init__(self, gui):
        self.gui = gui
        #self.gui.protocol = None
        #self.protocol = FileReceiver
        self.protocol = None
        self.setTimeout(None)

    def buildProtocol(self, addr):
        user = 'anonymous'
        passwd = 'twisted@matrix.com'
        self.protocol = TestClient(self, username=user, password=passwd, passive=1)
        #self.gui.protocol = self.protocol
        return self.protocol

    def clientConnectionLost(self, transport, reason):
        print("Connectiong lost normally:", reason)

    def clientConnectionFailed(self, transport, reason):
        print("Connection failed:", reason)


class FileClientFactoryThrottle(ThrottlingFactory, object):

    def __init__(self, gui):
        self.gui = gui
        #self.gui.protocol = None
        #self.protocol = FileReceiver
        self.protocol = None
        super(FileClientFactoryThrottle, self).__init__(protocol.ClientFactory, readLimit=100, writeLimit=100)

    def buildProtocol(self, addr):
        user = 'anonymous'
        passwd = 'twisted@matrix.com'
        self.protocol = TestClient(self, username=user, password=passwd, passive=1)
        #self.gui.protocol = self.protocol
        return self.protocol

    def clientConnectionLost(self, transport, reason):
        print("Connectiong lost normally:", reason)

    def clientConnectionFailed(self, transport, reason):
        print("Connection failed:", reason)

        
def getCWD(dir):
    print("This is the server's CWD:", dir)

if __name__ == "__main__":
    logger = log.startLogging(sys.stdout)
    app = wx.App(False)
    app.frame = TextSend()
    app.frame.Show()
    
    #app.MainLoop()

    #f = TestFactory(None)
    #reactor.connectTCP("connect", 5502, f)
    reactor.registerWxApp(app)
    f = FileClientFactory(app.frame)
    #f = FileClientFactoryThrottle(app.frame)
    reactor.connectTCP("localhost", 5504, f)
    #reactor.connectTCP("10.155.88.135", 5504, f)
    #reactor.connectTCP("192.168.254.18", 5504, f)
    reactor.run()
    print("some stuff")
    
    #f.protocol.getpwd().addCallback(getCWD)
    #f.protocol.getFile("test1.txt")
    #
    app.MainLoop()

