#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtGui import *

import subprocess
import threading
import time
import socket

USER = subprocess.check_output("logname", shell=True).rstrip()
USER_HOME_DIR = os.path.join("/home", str(USER))



class Builder(threading.Thread):
    """ in order to provide a NONBLocking loop that 
    periodically checks the internet connection 
    this is done it a separate thread
    """
    def __init__(self, mainui):
        threading.Thread.__init__(self)
        self.mainui= mainui
        self.stop = False

    def run(self):
        self.onBuild()
           
            
            
    def onBuild(self):
        #update life EXAM
        line = "Starting buildprocess...\n"
 
        self.mainui.line = line
        self.mainui.updatesignal.emit()
    
        cmd = "cd ~/.life/applications/life-builder && ./lifebuilder" 
        proc = subprocess.Popen(cmd,  shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, bufsize=1)
        for line in iter(proc.stderr.readline, b''):
            if line:
                self.mainui.line = line.decode()
                self.mainui.updatesignal.emit()
        
        for line in iter(proc.stdout.readline, b''):
            if line:
                self.mainui.line = line.decode()
                self.mainui.updatesignal.emit()
        proc.communicate()     
        

        self.mainui.finishedsignal.emit()
        self.stop = True
  















class MeinDialog(QtWidgets.QDialog):
    updatesignal = QtCore.pyqtSignal()
    finishedsignal = QtCore.pyqtSignal()
    
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        scriptdir=os.path.dirname(os.path.abspath(__file__))
        uifile=os.path.join(scriptdir,'main.ui')
        winicon=os.path.join(scriptdir,'appicon.png')
        
        self.ui = uic.loadUi(uifile)        # load UI
        self.ui.setWindowIcon(QIcon(winicon))
        self.ui.mkiso.clicked.connect(self.onISO)        # setup Slots
        self.ui.exit.clicked.connect(self.onAbbrechen)     
       
        self.updatesignal.connect(lambda: self.uiupdate())
        self.finishedsignal.connect(lambda: self.uifinished())
       
        self.line = ""

        
    def uiupdate(self):
        print (self.line)
        self.ui.info.insertPlainText(self.line)  
    
    def onISO(self): 
        self.ui.mkiso.setEnabled(False)
        builder = Builder(self)
        builder.start()
    
    def uifinished(self):
        line = "ISO Erstellung Abgeschlossen!"
        self.ui.inet.setText(line)  
       
    def onAbbrechen(self):    # Exit button
        self.ui.close()
        os._exit(0)










app = QtWidgets.QApplication(sys.argv)
dialog = MeinDialog()
dialog.ui.show()   #show user interface
sys.exit(app.exec_())
