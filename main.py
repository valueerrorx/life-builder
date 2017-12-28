#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtGui import *
from subprocess import Popen, PIPE, STDOUT
import shlex
import time


class  BuildWorker(QtCore.QObject):
    processed = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self, meindialog):
        super(BuildWorker, self).__init__()
        self.meindialog = meindialog

    def doCopy(self):
        command = "./lifebuilder"
        self.meindialog.buildprocess = Popen(shlex.split(command), stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=1, shell=True,universal_newlines=True)
        while True:
            output = self.meindialog.buildprocess.stdout.readline()    # wartet bei mksquashfs auf die line und blockiert weil keine line mehr kommt..  
            
            if output == '' and self.meindialog.buildprocess.poll() is not None:    
                break
            
            if output:
                print (output)
                
                if "SQUASHSTART" in output:   # triggers a different logging structure
                    number=output.split(",")
                    number=int(number[1])  # lines produced by mksquashfs - the number of inodes (every inode produces a line in mksquashfs)
                    print (number)
                    step = 100/number  #calculate 1%
                    self.meindialog.lineprocessing = False
                    self.meindialog.extraThread1.start()
                elif "SQUASHEND" in output:   # returns to normal logging
                    output = "\nSquashfs creation finished \n"
                    self.meindialog.lineprocessing = True
                    self.meindialog.percent = 100
  

                if self.meindialog.lineprocessing == True:
                    line = output
                    self.processed.emit(line)
                else:
                    self.meindialog.percent += step
                    print (self.meindialog.percent)
        self.finished.emit()  
      



class  CheckWorker(QtCore.QObject):
    processed1 = QtCore.pyqtSignal(str)
    finished1 = QtCore.pyqtSignal()

    def __init__(self, meindialog):
        super(CheckWorker, self).__init__()
        self.meindialog = meindialog
  
    def doCheck(self): 
        while self.meindialog.percent < 100:
            line = "Percent done: %s \n" %(self.meindialog.percent)
            self.processed1.emit(line)
            time.sleep(0.5)
        
        line = "Percent done: %s \n" %(self.meindialog.percent)
        self.processed1.emit(line)
        self.finished1.emit() 
  



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
    
        #one worker to start the life iso creator 
        self.extraThread = QtCore.QThread()
        self.worker = BuildWorker(self)
        self.worker.moveToThread(self.extraThread)
        self.extraThread.started.connect(self.worker.doCopy)
        self.worker.processed.connect(self.updateProgress)
        self.worker.finished.connect(self.buildfinished)
        
        #one worker1 to check other things while worker1 is occupied
        self.extraThread1 = QtCore.QThread()
        self.worker1 = CheckWorker(self)
        self.worker1.moveToThread(self.extraThread1)
        self.extraThread1.started.connect(self.worker1.doCheck)
        self.worker1.processed1.connect(self.updateProgress)
        self.worker1.finished1.connect(self.worker1finished)
       
        self.buildprocess = ""
        self.lineprocessing = True
        self.percent = 0
        
    def updateProgress(self,line):  
        self.ui.info.insertPlainText(line)  
        self.ui.info.setFocus(True)
        self.ui.info.moveCursor(QTextCursor.End)

    
    def onISO(self): 
        self.ui.mkiso.setEnabled(False)
        self.extraThread.start()
    
    def worker1finished(self):
        self.extraThread1.quit()
        self.percent = 0
    
    def buildfinished(self):
        line = "<b>ISO Erstellung Abgeschlossen!</b>"
        self.extraThread.quit()
        self.ui.inet.setText(line) 
      
       
    def onAbbrechen(self):    # Exit button
        command = "sudo pkill -f mksquashfs &"
        os.system(command)  
        command = "sudo pkill -f unsquashfs &"
        os.system(command)  
        command = "sudo pkill -f genisoimage &"
        os.system(command)  
        command = "sudo pkill -f mkisofs &"
        os.system(command)  
        command = "sudo pkill -f lifebuilder &"
        self.extraThread.quit()
        self.extraThread1.quit()
        
        os.system(command)  
        self.ui.close()
        os._exit(0)





app = QtWidgets.QApplication(sys.argv)
dialog = MeinDialog()
dialog.ui.show()   #show user interface
sys.exit(app.exec_())
