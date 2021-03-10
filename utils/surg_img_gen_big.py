#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'surg_img_gen.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import os
import sys
import time


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(4000, 2156)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.saveImageLabel = QtWidgets.QLabel(self.centralwidget)
        self.saveImageLabel.setGeometry(QtCore.QRect(1, 1, 2000, 2000))
        self.saveImageLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.saveImageLabel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.saveImageLabel.setLineWidth(3)
        self.saveImageLabel.setObjectName("saveImageLabel")
        self.compareImageLabel = QtWidgets.QLabel(self.centralwidget)
        self.compareImageLabel.setGeometry(QtCore.QRect(2000, 0, 2000, 2000))
        self.compareImageLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.compareImageLabel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.compareImageLabel.setLineWidth(3)
        self.compareImageLabel.setObjectName("compareImageLabel")
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(1964, 2030, 101, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(115, 210, 22))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 210, 22))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 210, 22))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.saveButton.setPalette(palette)
        self.saveButton.setObjectName("saveButton")
        self.rewindButton = QtWidgets.QPushButton(self.centralwidget)
        self.rewindButton.setGeometry(QtCore.QRect(1854, 2080, 101, 41))
        self.rewindButton.setObjectName("rewindButton")
        self.rewindButton_1 = QtWidgets.QPushButton(self.centralwidget)
        self.rewindButton_1.setGeometry(QtCore.QRect(1854, 2030, 101, 41))
        self.rewindButton_1.setObjectName("rewindButton_1")
        self.rewindButton_20 = QtWidgets.QPushButton(self.centralwidget)
        self.rewindButton_20.setGeometry(QtCore.QRect(1634, 2030, 101, 41))
        self.rewindButton_20.setObjectName("rewindButton_20")
        self.rewindButton_50 = QtWidgets.QPushButton(self.centralwidget)
        self.rewindButton_50.setGeometry(QtCore.QRect(1524, 2030, 101, 41))
        self.rewindButton_50.setObjectName("rewindButton_50")
        self.rewindButton_100 = QtWidgets.QPushButton(self.centralwidget)
        self.rewindButton_100.setGeometry(QtCore.QRect(1414, 2030, 101, 41))
        self.rewindButton_100.setObjectName("rewindButton_100")
        self.forwardButton = QtWidgets.QPushButton(self.centralwidget)
        self.forwardButton.setGeometry(QtCore.QRect(2074, 2080, 101, 41))
        self.forwardButton.setObjectName("forwardButton")
        self.forwardButton_1 = QtWidgets.QPushButton(self.centralwidget)
        self.forwardButton_1.setGeometry(QtCore.QRect(2074, 2030, 101, 41))
        self.forwardButton_1.setObjectName("forwardButton_1")
        self.forwardButton_20 = QtWidgets.QPushButton(self.centralwidget)
        self.forwardButton_20.setGeometry(QtCore.QRect(2294, 2030, 101, 41))
        self.forwardButton_20.setObjectName("forwardButton_20")
        self.forwardButton_50 = QtWidgets.QPushButton(self.centralwidget)
        self.forwardButton_50.setGeometry(QtCore.QRect(2404, 2030, 101, 41))
        self.forwardButton_50.setObjectName("forwardButton_50")
        self.forwardButton_100 = QtWidgets.QPushButton(self.centralwidget)
        self.forwardButton_100.setGeometry(QtCore.QRect(2514, 2030, 101, 41))
        self.forwardButton_100.setObjectName("forwardButton_100")
        self.frameNumberEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.frameNumberEdit.setGeometry(QtCore.QRect(1134, 2030, 113, 25))
        self.frameNumberEdit.setObjectName("frameNumberEdit")
        self.goToFrameButton = QtWidgets.QPushButton(self.centralwidget)
        self.goToFrameButton.setGeometry(QtCore.QRect(1254, 2030, 40, 25))
        self.goToFrameButton.setObjectName("goToFrameButton")
        self.framNumberLabel = QtWidgets.QLabel(self.centralwidget)
        self.framNumberLabel.setGeometry(QtCore.QRect(1134, 2060, 111, 16))
        self.framNumberLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.framNumberLabel.setObjectName("framNumberLabel")
        self.fileNumberEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.fileNumberEdit.setGeometry(QtCore.QRect(2734, 2030, 81, 21))
        self.fileNumberEdit.setObjectName("fileNumberEdit")
        self.fileNumberLabel = QtWidgets.QLabel(self.centralwidget)
        self.fileNumberLabel.setGeometry(QtCore.QRect(2730, 2050, 91, 20))
        self.fileNumberLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fileNumberLabel.setObjectName("fileNumberLabel")
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setGeometry(QtCore.QRect(1964, 2080, 101, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(210, 115, 22))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(210, 115, 22))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(210, 115, 22))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.stopButton.setPalette(palette)
        self.stopButton.setObjectName("stopButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 4000, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.saveButton.clicked.connect(self.save)
        self.stopButton.clicked.connect(self.stop)
        self.rewindButton.clicked.connect(self.rewind)
        self.rewindButton_1.clicked.connect(self.rewind1)
        self.rewindButton_20.clicked.connect(self.rewind20)
        self.rewindButton_50.clicked.connect(self.rewind50)
        self.rewindButton_100.clicked.connect(self.rewind100)
        self.forwardButton.clicked.connect(self.forward)
        self.forwardButton_1.clicked.connect(self.forward1)
        self.forwardButton_20.clicked.connect(self.forward20)
        self.forwardButton_50.clicked.connect(self.forward50)
        self.forwardButton_100.clicked.connect(self.forward100)
        self.goToFrameButton.clicked.connect(self.goToFrame)

        self.p_timer = QtCore.QTimer()
        self.p_timer.setInterval(100)
        self.p_timer.timeout.connect(self.play_timer)
        self.p_timer.start()

        self.cur_cmnd = 'S'

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.saveButton.setText(_translate("MainWindow", "Save"))
        self.rewindButton.setText(_translate("MainWindow", "RWD"))
        self.rewindButton_1.setText(_translate("MainWindow", "RWD1"))
        self.rewindButton_20.setText(_translate("MainWindow", "RWD10"))
        self.rewindButton_50.setText(_translate("MainWindow", "RWD50"))
        self.rewindButton_100.setText(_translate("MainWindow", "RWD100"))
        self.forwardButton.setText(_translate("MainWindow", "FWD"))
        self.forwardButton_1.setText(_translate("MainWindow", "FWD1"))
        self.forwardButton_20.setText(_translate("MainWindow", "FWD10"))
        self.forwardButton_50.setText(_translate("MainWindow", "FWD50"))
        self.forwardButton_100.setText(_translate("MainWindow", "FWD100"))
        self.goToFrameButton.setText(_translate("MainWindow", "GO"))
        self.framNumberLabel.setText(_translate("MainWindow", "Current Frame"))
        self.fileNumberLabel.setText(_translate("MainWindow", "File Number"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))

    def save(self):

        self.saveFrameNumber = self.currentFrameNumber

        try:
            self.vidcap.set(cv2.CAP_PROP_POS_MSEC,(self.currentFrameNumber * 100))    # added this line
            success, self.image = self.vidcap.read()
            if success:
                cv2.imwrite(os.path.join(self.outputFolder, '%d.jpg') % self.fileNumber, self.image)
                pixmap = QtGui.QPixmap(os.path.join(self.outputFolder, '%d.jpg') % self.fileNumber) # Setup pixmap with the provided cartoon camera image
                pixmap = pixmap.scaled(self.saveImageLabel.width(), self.saveImageLabel.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
                self.saveImageLabel.setPixmap(pixmap) # Set the pixmap onto the label
        except Exception as exc:
            print(exc)

        self.fileNumber += 1
        self.fileNumberEdit.setText(str(self.fileNumber))

        self.forward1()

    def play_timer(self):
        if self.cur_cmnd == 'F':
            self.goPosition(1)
        elif self.cur_cmnd == 'R':
            if self.currentFrameNumber > self.saveFrameNumber:
                self.goPosition(-1)
            else:
                self.cur_cmnd = 'S'

    def stop(self):

        self.cur_cmnd = 'S'

    def rewind(self):

        if self.cur_cmnd == 'S':
            self.cur_cmnd = 'R'
        else:
            self.cur_cmnd = 'S'

    def rewind1(self):

        if self.currentFrameNumber > self.saveFrameNumber:
            self.goPosition(-1)

    def rewind20(self):

        if self.currentFrameNumber > self.saveFrameNumber + 10:
            self.goPosition(-10)

    def rewind50(self):

        if self.currentFrameNumber > self.saveFrameNumber + 50:
            self.goPosition(-50)

    def rewind100(self):

        if self.currentFrameNumber > self.saveFrameNumber + 100:
            self.goPosition(-100)

    def forward(self):

        if self.cur_cmnd == 'S':
            self.cur_cmnd = 'F'
        else:
            self.cur_cmnd = 'S'

    def forward1(self):

        self.goPosition(1)

    def forward20(self):

        self.goPosition(10)

    def forward50(self):

        self.goPosition(50)

    def forward100(self):

        self.goPosition(100)

    def goPosition(self, count):

        self.currentFrameNumber += count
        with open('frame.txt', 'w') as f:
            f.write(str(self.currentFrameNumber) + ' ' + str(self.fileNumber))

        self.frameNumberEdit.setText(str(self.currentFrameNumber))
        try:
            self.vidcap.set(cv2.CAP_PROP_POS_MSEC,(self.currentFrameNumber * 100))    # added this line
            success, self.image = self.vidcap.read()
            if success:
                cv2.imwrite(os.path.join(self.outputFolder, 'temp_image.jpg'), self.image)
                pixmap = QtGui.QPixmap(os.path.join(self.outputFolder, 'temp_image.jpg')) # Setup pixmap with the provided cartoon camera image
                pixmap = pixmap.scaled(self.compareImageLabel.width(), self.compareImageLabel.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
                self.compareImageLabel.setPixmap(pixmap) # Set the pixmap onto the label
            else:
                print("Video raead failed at frame count:", self.currentFrameNumber)
        except Exception as exc:
            print(exc)

    def goToFrame(self):

        self.currentFrameNumber  =  int(self.frameNumberEdit.text())
        self.goPosition(0)




def main(args):

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)



    ui.videoName = args[0]
    ui.outputFolder = args[1]
    if not os.path.exists(ui.outputFolder):
        os.mkdir(ui.outputFolder)

    if (os.path.exists('frame.txt')):
        with open('frame.txt') as f:
            ui.currentFrameNumber, ui.fileNumber = map(int, f.read().split())
            ui.saveFrameNumber = ui.currentFrameNumber
    else:
        ui.currentFrameNumber = int(args[2])
        ui.fileNumber = int(args[3])
        ui.saveFrameNumber = int(args[2])   #currentFrameNumber can never be less than this value

    ui.frameNumberEdit.setText(str(ui.currentFrameNumber))
    ui.fileNumberEdit.setText(str(ui.fileNumber))

    ui.vidcap = cv2.VideoCapture(ui.videoName)
    print("Video frame count:", ui.vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    try:
        ui.vidcap.set(cv2.CAP_PROP_POS_MSEC,(int(ui.currentFrameNumber) * 100))    # added this line
        success, ui.image = ui.vidcap.read()
        if success:
            cv2.imwrite(os.path.join(ui.outputFolder, 'temp_image.jpg'), ui.image)
            pixmap = QtGui.QPixmap(os.path.join(ui.outputFolder, 'temp_image.jpg')) # Setup pixmap with the provided cartoon camera image
            pixmap = pixmap.scaled(ui.compareImageLabel.width(), ui.compareImageLabel.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
            ui.compareImageLabel.setPixmap(pixmap) # Set the pixmap onto the label
            if ui.fileNumber > 1:
                pixmap = QtGui.QPixmap(os.path.join(ui.outputFolder, '%d.jpg') % (ui.fileNumber - 1)) # Setup pixmap with the provided cartoon camera image
                pixmap = pixmap.scaled(ui.saveImageLabel.width(), ui.saveImageLabel.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
                ui.saveImageLabel.setPixmap(pixmap) # Set the pixmap onto the label
        else:
            print("Video Capture read failed(1)")
    except Exception as exc:
        print(exc)


    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    args = ['/home/kamiar/Videos/opervu_videos/Children_Hosp_11-6_12-2/camera_2/11_06_07_53_29/recording-5.mp4', '/home/kamiar/projects/opervu/images/11_06_07_53_29/', '1', '1']
    main(args)
