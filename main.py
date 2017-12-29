#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtGui import *
from subprocess import Popen, PIPE, STDOUT
import shlex
import time
import re

class  BuildWorker(QtCore.QObject):
    processed = QtCore.pyqtSignal(str,int)
    aborted = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self, meindialog):
        super(BuildWorker, self).__init__()
        self.meindialog = meindialog

    def doCopy(self):
        command = "./lifebuilder"
        lasttotalpercent = 0 
        self.meindialog.buildprocess = Popen(shlex.split(command), stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=1, shell=True,universal_newlines=True)
        while True:
            output = self.meindialog.buildprocess.stdout.readline()    # wartet bei mksquashfs auf die line und blockiert weil keine line mehr kommt..  
            
            if output == '' and self.meindialog.buildprocess.poll() is not None:    
                break
            
            if output:
                print (output)    #always print everything 
               
                if "OUTPUT:" in output:    #differentiate between our output and other output
                    
                    
                    output = output.strip("OUTPUT: ")

                    content = output.split("§")
                    text = str(content[0])
                    try:                # just in case the lifebuilder script does not provide a percentage with an output line
                        totalpercentfinished = int(content[1])
                        lasttotalpercent = totalpercentfinished
                    except:
                        totalpercentfinished = lasttotalpercent
                       
                    if "ERROR" in text: 
                        self.aborted.emit(text) 
                        return
                
                    # this is a very tricky workaround in order to get mksquashfs percentage into the UI
                    if "SQUASHSTART" in text:   # triggers a different logging structure
                        number=text.split(",")
                        number=int(number[1])  # lines produced by mksquashfs - the number of inodes (every inode produces a line in mksquashfs) calculated in the lifebuilder sh script
                        print (number)
                        step = 100/number  #calculate 1%
                        self.meindialog.lineprocessing = False
                        self.meindialog.extraThread1.start()    # we need to unchain this cause if we would send every change to the ui it would overload and block 
                    elif "SQUASHEND" in text:   # returns to normal logging
                        text = "\nSquashfs creation finished \n"
                        self.meindialog.lineprocessing = True
                        self.meindialog.percent = 100
    

                if self.meindialog.lineprocessing == True:
                    line = text
                    self.processed.emit(line, totalpercentfinished)
                else:   #stop emmiting every output line - to much overhead - just set percent variable on mydialog and CheckWorker will poll the current value every .5 seconds - thats accurate enough
                    self.meindialog.percent += step
                    print (self.meindialog.percent)
        self.finished.emit()  
      



class  CheckWorker(QtCore.QObject):
    processed1 = QtCore.pyqtSignal(str, int)
    finished1 = QtCore.pyqtSignal()

    def __init__(self, meindialog):
        super(CheckWorker, self).__init__()
        self.meindialog = meindialog
  
    def doCheck(self): 
        while self.meindialog.percent < 100:
            line = "Percent done: %s \n" %(self.meindialog.percent)
            self.processed1.emit(line, self.meindialog.percent)
            time.sleep(0.5)
        
        line = "Percent done: %s \n" %(self.meindialog.percent)
        self.processed1.emit(line, self.meindialog.percent)
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
        self.worker.aborted.connect(self.builderror)
        
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
        
    def updateProgress(self,line, totalpercentfinished):  
        self.ui.progressBar.setValue(int(totalpercentfinished))
        self.ui.info.setText(line)  
    
    def onISO(self): 
        self.ui.mkiso.setEnabled(False)
        self.extraThread.start()
    
    def worker1finished(self):
        self.extraThread1.quit()
        self.percent = 0
    
    def buildfinished(self):
        line = "<b>ISO Erstellung Abgeschlossen!</b>"
        self.ui.inet.setText(line) 
        self.stopall()
        
    def builderror(self,line):
        self.ui.info.setText(line) 
        infoline = "<b>ISO Erstellung Abgebrochen!</b>"
        self.ui.inet.setText(infoline) 
        self.stopall()

    def stopall(self):
        command = "sudo pkill -f mksquashfs &"
        os.system(command)  
        command = "sudo pkill -f unsquashfs &"
        os.system(command)  
        command = "sudo pkill -f genisoimage &"
        os.system(command)  
        command = "sudo pkill -f mkisofs &"
        os.system(command)  
        command = "sudo pkill -f lifebuilder &"
        os.system(command) 
        self.extraThread.quit()
        self.extraThread1.quit()
       
    def onAbbrechen(self):    # Exit button
        self.stopall()
        self.ui.close()
        os._exit(0)

    



app = QtWidgets.QApplication(sys.argv)
dialog = MeinDialog()
dialog.ui.show()   #show user interface
sys.exit(app.exec_())
