#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtGui import *
from subprocess import Popen, PIPE, STDOUT
import socket


class MeinDialog(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        scriptdir=os.path.dirname(os.path.abspath(__file__))
        uifile=os.path.join(scriptdir,'main.ui')
        winicon=os.path.join(scriptdir,'appicon.png')
        self.ui = uic.loadUi(uifile)        # load UI
        self.ui.setWindowIcon(QIcon(winicon))
        self.ui.mkiso.clicked.connect(self.onISO)        # setup Slots
        self.ui.exit.clicked.connect(self.onAbbrechen)     
    
        self.extraThread = QtCore.QThread()
        self.worker = Worker(self)
        self.worker.moveToThread(self.extraThread)
        self.extraThread.started.connect(self.worker.doCopy)
        self.worker.processed.connect(self.updateProgress)
        self.worker.finished.connect(self.uifinished)
        
        
    def updateProgress(self,line):  
        print (line)
        self.ui.info.insertPlainText(line)  
        self.ui.info.setFocus(True)
        self.ui.info.moveCursor(QTextCursor.End)

    
    def onISO(self): 
        self.ui.mkiso.setEnabled(False)
        self.extraThread.start()
    
    def uifinished(self):
        line = "<b>ISO Erstellung Abgeschlossen!</b>"
        self.ui.inet.setText(line)  
       
    def onAbbrechen(self):    # Exit button
        command = "sudo pkill -f lifebuilder &"
        os.system(command)  
        self.ui.close()
        os._exit(0)





class  Worker(QtCore.QObject):
    def __init__(self, meindialog):
        super(Worker, self).__init__()
        self.meindialog = meindialog
    
    processed = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    
    def doCopy(self):
        p=Popen(["./lifebuilder"],stdout=PIPE, stderr=STDOUT, bufsize=1, shell=False)
        with p.stdout:
            for line in iter(p.stdout.readline, b''):
                self.processed.emit(line)
                
        p.wait()
        self.finished.emit()   




app = QtWidgets.QApplication(sys.argv)
dialog = MeinDialog()
dialog.ui.show()   #show user interface
sys.exit(app.exec_())
