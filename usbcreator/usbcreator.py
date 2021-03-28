#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.
#


import sys
import os
from PyQt5 import QtCore, uic, QtWidgets
# from PyQt5.QtGui import *
from subprocess import Popen, PIPE, STDOUT
import subprocess
import sip
from PyQt5.QtGui import QPixmap, QIcon
from configobj import ConfigObj


USER = subprocess.check_output("logname", shell=True).rstrip()
USER_HOME_DIR = os.path.join("/home", str(USER))
WORK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class MeinDialog(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.ui = uic.loadUi(os.path.join(WORK_DIRECTORY, "usbcreator.ui"))        # load UI
        self.ui.setWindowIcon(QIcon(os.path.join(WORK_DIRECTORY, "pixmaps/drive.png")))
        self.ui.search.clicked.connect(self.searchUSB)
        self.ui.exit.clicked.connect(self.onAbbrechen)        # setup Slots
        self.ui.selectiso.clicked.connect(self.selectFile)
        self.ui.usbusb.clicked.connect(self.searchUSB)
        self.ui.copy.clicked.connect(self.startCopy)

        self.ui.copydata.clicked.connect(self.saveConfig)
        self.ui.update.clicked.connect(self.saveConfig)
        self.ui.liveonly.clicked.connect(self.disableCopydata)
        self.ui.bootmessages.clicked.connect(self.saveConfig)

        self.proposed = ["sda", "sdb", "sdc", "sdd", "sde", "sdf", "sdg", "sdh", "sdi", "sdj", "sdk", "sdl", "sdm", "sdn", "sdo", "sdp", "sdq", "sdr", "sds", "sdt", "sdu", "sdv", "sdw", "sdx", "sdy", "sdz"]

        QtWidgets.QApplication.instance().aboutToQuit.connect(self.quit)

        self.extraThread = QtCore.QThread()
        self.worker = Worker(self)
        self.worker.moveToThread(self.extraThread)
        self.extraThread.started.connect(self.worker.doCopy)
        self.extraThread.finished.connect(self.finished)

        self.worker.processed.connect(self.updateProgress)
        self.worker.finished.connect(self.finished)
        self.searchinfo = ""
        self.isolocation = ""

        if len(sys.argv) > 1:
            print(sys.argv[1])
            self.isolocation = sys.argv[1]

        if self.isolocation != "":
            if os.path.isfile(self.isolocation):   # check if the filepath given via commandline is a valid file
                self.ui.copydata.setEnabled(False)
                # self.ui.update.setEnabled(False)
                self.ui.isousb.setChecked(True)
                filename = self.isolocation.rsplit('/', 1)
                self.ui.isofilename.setText("<b>%s</b>" % filename[1])
            else:
                print("isolocation was given but file not found")

        # check for root permissions
        if os.geteuid() != 0:
            print("You need root access in order to create a live USB device")
            command = "pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY KDE_FULL_SESSION=true  %s" % (os.path.abspath(__file__))
            self.ui.close()
            os.system(command)
            os._exit(0)

        self.readConfig()

    def disableCopydata(self):
        if self.ui.liveonly.checkState():
            self.ui.copydata.setEnabled(False)
        else:
            if self.ui.usbusb.isChecked():
                self.ui.copydata.setEnabled(True)
        self.saveConfig()

    def selectFile(self):
        self.lines = []

        filedialog = QtWidgets.QFileDialog()
        filedialog.setDirectory(USER_HOME_DIR)  # set default directory
        # filedialog.selectNameFilter("Text Files (*.txt)")

        file_path = filedialog.getOpenFileName(self, "Bitte wählen sie eine Datei", "", "ISO Images (*.iso)")  # parent, caption, directory, filter
        file_path = file_path[0]

        if os.path.isfile(file_path):
            filename = file_path.rsplit('/', 1)
            self.ui.isofilename.setText("<b>%s</b>" % filename[1])
            self.isolocation = file_path

    def updateProgress(self, value, item, line):
        if "abgeschlossen" in line:
            item.comboBox.setEnabled(True)
        elif "fehlgeschlagen" in line:
            pixmap = QPixmap(os.path.join(WORK_DIRECTORY, "pixmaps/driveno.png"))
            pixmap = pixmap.scaled(QtCore.QSize(64, 64))
            item.picture.setPixmap(pixmap)
            # make sure this process quits immediately
            print('killing running subprocesses')
            command = "sudo pkill -f rsync && sudo killall rsync"
            os.system(command)

        if "LOCK" in line:
            self.ui.listWidget.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
        else:
            item.progressbar.setValue(int(value))
            item.warn.setText(line)

    def quit(self):
        # Quit the thread's event loop. Note that this *doesn't* stop tasks
        # running in the thread, it just stops the thread from dispatching
        # events.
        self.extraThread.quit()
        # Wait for the thread to complete. If the thread's task is not done,
        # this will block.
        self.extraThread.wait()

    def finished(self):
        print('finished')
        # self.ui.copy.setEnabled(True)
        self.ui.exit.setEnabled(True)
        self.ui.search.setEnabled(True)
        self.ui.copydata.setEnabled(True)
        self.ui.update.setEnabled(True)
        self.ui.liveonly.setEnabled(True)
        self.ui.bootmessages.setEnabled(True)
        self.ui.usbusb.setEnabled(True)
        self.ui.isousb.setEnabled(True)
        if self.ui.isousb.isChecked():
            self.ui.copydata.setEnabled(False)
        # restore Config
        self.readConfig()

    def searchUSB(self):
        if self.ui.liveonly.checkState():
            self.ui.copydata.setEnabled(False)

        self.devices = []
        # make sure nothing is running anymore
        self.extraThread.quit()
        self.extraThread.wait()
        self.ui.deviceinfo.setText("USB Speichersticks gefunden")  # reset deviceinfolabel

        # build devices list
        for dev in self.proposed:
            self.checkDevice(dev)

        if len(self.devices) > 0:
            self.ui.copy.setEnabled(True)
            self.ui.deviceinfo.setText("<b>USB Speichersticks gefunden</b>")
        else:
            self.ui.copy.setEnabled(False)
            if self.searchinfo == "SYSUSB":
                self.ui.deviceinfo.setText("<b>Es wurde nur der Systemdatenträger gefunden!</b>")
            elif self.searchinfo == "NOLIVE":
                self.ui.deviceinfo.setText("<b>Kopie von installierten Systemen nicht unterstützt!</b>")
            elif self.searchinfo == "LOCKED":
                self.ui.deviceinfo.setText("<b>Der gefundene USB Datenträger ist gesperrt!</b>")
            else:
                self.ui.deviceinfo.setText("<b>Es wurde kein USB Datenträger gefunden!</b>")

        # delete all widgets
        items = self.get_list_widget_items()
        for item in items:
            sip.delete(item)  # noqa

        # build size information for every device
        for deviceentry in self.devices:
            usbdev = deviceentry[0]
            device_info = deviceentry[1]
            devicemodel = deviceentry[2]
            devicesize = deviceentry[3]  # noqa
            usbbytesize = deviceentry[4]
            self.createWidget(usbdev, device_info, devicemodel, usbbytesize)

        # do not allow copy if any of the flashdrives is too small
        items = self.get_list_widget_items()
        for item in items:
            if item.sharesize == 0:
                self.ui.copy.setEnabled(False)

    def createWidget(self, usbdev, device_info, devicemodel, usbbytesize):
        # add device widgets to UI
        items = self.get_list_widget_items()
        if items:
            existing = False
            for item in items:
                if usbdev == item.id:
                    existing = True
                    print("found existing widget for usb device")

            if existing is False:
                self.addNewListItem(usbdev, device_info, devicemodel, usbbytesize)
                return
        else:
            self.addNewListItem(usbdev, device_info, devicemodel, usbbytesize)
            return

    def addNewListItem(self, usbdev, device_info, devicemodel, usbbytesize):
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(400, 154))
        # store important information on the widget
        item.id = usbdev
        item.size = usbbytesize
        item.sharesize = 2000

        pixmap = QPixmap(os.path.join(WORK_DIRECTORY, "pixmaps/drive.png"))
        pixmap = pixmap.scaled(QtCore.QSize(64, 64))
        item.picture = QtWidgets.QLabel()
        item.picture.setPixmap(pixmap)
        item.picture.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)

        usbbytesize = float(usbbytesize) / 1000 / 1000 / 1000

        item.info = QtWidgets.QLabel('      %s %s ( %s ) %.2fGB' % (device_info, devicemodel, item.id, usbbytesize))
        item.info.setAlignment(QtCore.Qt.AlignRight)
        item.info.setFixedWidth(240)

        item.warn = QtWidgets.QLabel('')
        item.warn.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        item.placeholder = QtWidgets.QLabel('      ')
        item.share = QtWidgets.QLabel("Größe der 'share' Partition:")
        item.share.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        item.comboBox = QtWidgets.QComboBox()
        item.comboBox.addItem("0.5 GB")
        item.comboBox.addItem("1 GB")
        item.comboBox.addItem("2 GB")
        item.comboBox.addItem("4 GB")
        item.comboBox.addItem("8 GB")
        item.comboBox.addItem("16 GB")
        item.comboBox.addItem("32 GB")
        item.comboBox.addItem("48 GB")
        item.comboBox.setFixedWidth(200)
        item.comboBox.setCurrentIndex(2)
        item.comboBox.currentIndexChanged.connect(lambda: self.checkSize(item))

        item.progressbar = QtWidgets.QProgressBar(self)
        item.progressbar.setInvertedAppearance(True)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(0)
        # grid.setRowStretch (1, 4)

        grid.addWidget(item.info, 0, 1)
        grid.addWidget(item.warn, 4, 1)
        grid.addWidget(item.picture, 3, 0)
        grid.addWidget(item.comboBox, 3, 1)
        grid.addWidget(item.share, 2, 1)
        grid.addWidget(item.progressbar, 4, 0)
        grid.addWidget(item.placeholder, 1, 1)
        grid.addWidget(item.placeholder, 5, 1)

        widget = QtWidgets.QWidget()
        widget.setLayout(grid)

        # widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # widget.customContextMenuRequested.connect(lambda: self._on_context_menu(item.pID, item.disabled))

        self.ui.listWidget.addItem(item)  # add the listitem to the listwidget
        self.ui.listWidget.setItemWidget(item, widget)  # set the widget as the listitem's widget

        self.checkSize(item)

    def get_list_widget_items(self):
        items = []
        for index in range(self.ui.listWidget.count()):
            items.append(self.ui.listWidget.item(index))
        return items

    def checkDevice(self, dev):
        """this function builds a list
        of all found and confirmed usb devices
        """
        if self.ui.isousb.isChecked():
            copylife = "False"
        else:
            copylife = "True"

        getcommand = os.path.join(WORK_DIRECTORY, "getflashdrive.sh")

        answer = Popen([getcommand, "check", dev, copylife], stdout=PIPE)
        answer = str(answer.communicate()[0], 'utf-8')  # das shellscript antwortet immer mit dem namen der datei die die informationen beinhaltet
        answerlist = answer.split(';')    # "0 $USB; 1 $DEVICEVENDOR; 2 $DEVICEMODEL; 3 $DEVICESIZE; 4 $USBBYTESIZE"
        print(answerlist)

        usbdev = answerlist[0]    # erster teil ist usb gerät
        device_info = answerlist[1]
        try:
            devicemodel = answerlist[2]
            devicesize = answerlist[3]
            usbbytesize = answerlist[4]
        except Exception:
            IndexError

        if device_info in ("NOUSB", "SYSUSB", "NOLIVE", "LOCKED"):
            # be more verbose if there is no usb found at all or if the only drive found is the sysusb  - we could iterate over a separate list of all devices later
            if device_info == "NOLIVE":
                self.searchinfo = "NOLIVE"
            elif device_info == "SYSUSB":
                self.searchinfo = "SYSUSB"
            elif device_info == "LOCKED":
                self.searchinfo = "LOCKED"

            return  # we do not use those devices
        else:
            devlist = []   # rebuild list of found devices and check if a device is already in it
            for devname in self.devices:
                devlist.append(devname[0])

            if usbdev in devlist:
                print("already in list")
            else:
                # erstelle eine umfassende liste mit geräteinformationen
                self.devices.append([usbdev, device_info, devicemodel, devicesize, usbbytesize])

        return

    def checkSize(self, item):
        devicesize = int(item.size) / 1024 / 1024
        sharesize = self.getShareSize(item)

        if devicesize - 6000 - sharesize > 0:   # 4GB for the system 2GB  casper-rw + SHARE
            print("device size ok")
            pixmap = QPixmap(os.path.join(WORK_DIRECTORY, "pixmaps/driveyes.png"))
            pixmap = pixmap.scaled(QtCore.QSize(64, 64))
            item.picture.setPixmap(pixmap)
            item.sharesize = sharesize
            item.warn.setText("<b>Alles Ok</b>")
            self.ui.copy.setEnabled(True)
            return True
        else:
            print("device to small %s" % item.id)

            item.warn.setText("<b>Zu wenig Speicherplatz</b>")
            pixmap = QPixmap(os.path.join(WORK_DIRECTORY, "pixmaps/driveno.png"))
            pixmap = pixmap.scaled(QtCore.QSize(64, 64))
            item.picture.setPixmap(pixmap)
            item.sharesize = 0
            self.ui.copy.setEnabled(False)

            return False

    def getShareSize(self, item):
        sharesize = str(item.comboBox.currentText())
        if sharesize == "0.5 GB":
            sharesize = 500
        elif sharesize == "1 GB":
            sharesize = 1000
        elif sharesize == "2 GB":
            sharesize = 2000
        elif sharesize == "4 GB":
            sharesize = 4000
        elif sharesize == "8 GB":
            sharesize = 8000
        elif sharesize == "16 GB":
            sharesize = 16000
        elif sharesize == "32 GB":
            sharesize = 32000
        elif sharesize == "48 GB":
            sharesize = 48000
        return sharesize

    def startCopy(self):
        items = self.get_list_widget_items()

        if self.ui.isousb.isChecked():
            if self.isolocation != "":
                if os.path.isfile(self.isolocation):
                    print("iso check ok")
                else:
                    self.ui.isofilename.setText("<b>Bitte wählen sie eine ISO Datei!</b>")
                    return
            else:
                self.ui.isofilename.setText("<b>Bitte wählen sie eine ISO Datei!</b>")
                return

        if items:
            for item in items:
                item.comboBox.setEnabled(False)

            self.ui.copy.setEnabled(False)
            self.ui.copydata.setEnabled(False)
            self.ui.update.setEnabled(False)
            self.ui.search.setEnabled(False)
            self.ui.liveonly.setEnabled(False)
            self.ui.usbusb.setEnabled(False)
            self.ui.isousb.setEnabled(False)
            self.ui.bootmessages.setEnabled(False)

            self.extraThread.start()

        else:
            return

    def onAbbrechen(self):    # Exit button - remove ALL lockfiles
        print("Beende alle Prozesse")
        for i in self.proposed:
            try:
                os.remove("%s.lock" % i)
            except Exception:
                pass

        command = "sudo pkill -f getflashdrive &"
        os.system(command)
        command = "sudo pkill -f rsync && sudo killall rsync"
        os.system(command)
        self.ui.close()
        sys.exit(0)

    def writeDefaultConfig(self):
        """ default Config File """
        config = ConfigObj('config.ini', encoding='UTF8')
        config['copydata'] = 0
        config['update'] = 0
        config['liveonly'] = 0
        config['bootmessages'] = 2
        config.write()

    def saveConfig(self):
        config = ConfigObj('config.ini', encoding='UTF8')
        config['copydata'] = self.ui.copydata.checkState()
        config['update'] = self.ui.update.checkState()
        config['liveonly'] = self.ui.liveonly.checkState()
        config['bootmessages'] = self.ui.bootmessages.checkState()
        config.write()

    def setCheckBox(self, what, status):
        """ set the checkbox from Config File """
        if status == 2:  # 2 is checked
            what.setChecked(True)
        else:
            what.setChecked(False)

    def readConfig(self):
        """ read the last used Configuration """
        try:
            config = ConfigObj('config.ini', encoding='UTF8')
            self.setCheckBox(self.ui.copydata, int(config['copydata']))
            self.setCheckBox(self.ui.update, int(config['update']))
            self.setCheckBox(self.ui.liveonly, int(config['liveonly']))
            self.setCheckBox(self.ui.bootmessages, int(config['bootmessages']))
        except Exception:
            # config does not exists > default Values
            self.setCheckBox(self.ui.copydata, 0)
            self.setCheckBox(self.ui.update, 0)
            self.setCheckBox(self.ui.liveonly, 0)
            self.setCheckBox(self.ui.bootmessages, 2)
            self.writeDefaultConfig()


class Worker(QtCore.QObject):
    def __init__(self, meindialog):
        super(Worker, self).__init__()
        self.meindialog = meindialog

    processed = QtCore.pyqtSignal(int, QtWidgets.QListWidgetItem, str)
    finished = QtCore.pyqtSignal()

    def doCopy(self):
        copydata = self.meindialog.ui.copydata.checkState()

        update = self.meindialog.ui.update.checkState()

        if self.meindialog.ui.isousb.isChecked():
            update = False
            copydata = False
            method = "iso"
            self.isolocation = self.meindialog.isolocation
        else:
            method = "copy"
            self.isolocation = "none"

        liveonly = self.meindialog.ui.liveonly.checkState()

        items = self.meindialog.get_list_widget_items()
        for item in items:

            self.processed.emit(0, item, 'LOCK')  # lock UI on process start

            # get rid of spaces an special chars in order to pass it as parameter - i know there is a better way ;-)
            iteminfo = item.info.text().replace("(", "").replace(")", "").replace("  ", " ").replace("   ", "").replace(" ", "-")

            completed = float(0)
            if update is True:   # less steps
                increment = float(2.5)
            else:
                increment = float(1.3)

            liveonly = self.meindialog.ui.liveonly.checkState()
            if liveonly == 0:
                liveonly = False
            else:
                liveonly = True

            bootmessages = self.meindialog.ui.bootmessages.checkState()
            if bootmessages == 0:
                bootmessages = False
            else:
                bootmessages = True

            getcommand = os.path.join(WORK_DIRECTORY, "getflashdrive.sh")
            p = Popen([getcommand, str(method), str(item.sharesize), str(copydata), str(item.id), str(iteminfo), str(update), str(self.isolocation), str(liveonly), str(bootmessages)], stdout=PIPE, stderr=STDOUT, bufsize=1, shell=False)

            with p.stdout:
                for line in iter(p.stdout.readline, b''):
                    line = line.decode()
                    line = line.strip('\n')
                    print(line)

                    if "0%" not in line:    # rsync delivers 200 entries with 0% sometimes - do not increment
                        completed += increment

                    if "FILENUMBER" in line:   # keyword FILENUMBER liefert anzahl an files für rsync
                        number = line.split(",")
                        number = float(number[1])
                        increment = float(84 / number)
                        completed += 1  # ganzer schritt notwendig um textupdate zu erzwingen
                    elif "CASPER" in line:   # keyword CASPER liefert anzahl an files für rsync
                        number = line.split(",")
                        number = float(number[1])
                        item.progressbar.setValue(18)
                        increment = float(80 / number)
                        completed += 1

                    if "size" in line:  # rsync is finished - advance 1 step
                        increment = float(1)   # progressbar geht nur weiter beim überschreiten ganzer zahlen - setze wieder auf 1 sonst werden letze einträge nicht visualisiert
                        completed += 1

                    if "F90" in line:  # advance to 90% (after sync)
                        completed = 90

                    if "FAILED" in line or "error" in line or "failed" in line:
                        completed = 100
                        line = "Kopiervorgang fehlgeschlagen"
                        print(line)
                        self.processed.emit(completed, item, line)
                        p.kill()
                        break

                    if "END" in line:
                        completed = 100
                        line = "Kopiervorgang abgeschlossen"

                    self.processed.emit(completed, item, line)  # update progressbar over signal DO NOT directly acces UI elements from separate thread

            p.wait()
        self.finished.emit()


app = QtWidgets.QApplication(sys.argv)
dialog = MeinDialog()
dialog.ui.show()
sys.exit(app.exec_())
