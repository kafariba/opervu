#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'video_capture_gui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from queue import Queue
from threading import Thread
import camera_control
import shutil

STOP_CMND = "StopCmnd"
RECORD_CMND = "RecordCmnd"
PREVIEW_CMND = "PreviewCmnd"
QUIT_CMND = "QuitCmnd"
NAME_CMND = 'NameCmnd'

cmnd_q = Queue()
status_q = Queue()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(743, 628)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.recordBtn = QtWidgets.QPushButton(self.centralwidget)
        self.recordBtn.setGeometry(QtCore.QRect(470, 50, 141, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.recordBtn.setPalette(palette)
        self.recordBtn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.recordBtn.setAutoRepeatDelay(298)
        self.recordBtn.setObjectName("recordBtn")
        self.stopBtn = QtWidgets.QPushButton(self.centralwidget)
        self.stopBtn.setGeometry(QtCore.QRect(290, 50, 141, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.stopBtn.setPalette(palette)
        self.stopBtn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.stopBtn.setAutoRepeatDelay(298)
        self.stopBtn.setObjectName("stopBtn")
        self.stopBtn.setEnabled(False)
        self.statusEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.statusEdit.setGeometry(QtCore.QRect(290, 110, 141, 25))
        self.statusEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.statusEdit.setReadOnly(True)
        self.statusEdit.setObjectName("statusEdit")
        self.recordingStatusLbl = QtWidgets.QLabel(self.centralwidget)
        self.recordingStatusLbl.setGeometry(QtCore.QRect(300, 130, 121, 21))
        self.recordingStatusLbl.setObjectName("recordingStatusLbl")
        self.camera1ImageLbl = QtWidgets.QLabel(self.centralwidget)
        self.camera1ImageLbl.setGeometry(QtCore.QRect(30, 170, 331, 321))
        self.camera1ImageLbl.setFrameShape(QtWidgets.QFrame.Box)
        self.camera1ImageLbl.setFrameShadow(QtWidgets.QFrame.Raised)
        self.camera1ImageLbl.setLineWidth(2)
        self.camera1ImageLbl.setText("")
        self.camera1ImageLbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.camera1ImageLbl.setObjectName("camera1ImageLbl")
        pixmap = QtGui.QPixmap("camera.jpg") # Setup pixmap with the provided cartoon camera image
        pixmap = pixmap.scaled(self.camera1ImageLbl.width(), self.camera1ImageLbl.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
        self.camera1ImageLbl.setPixmap(pixmap) # Set the pixmap onto the label
        self.camera2ImageLbl = QtWidgets.QLabel(self.centralwidget)
        self.camera2ImageLbl.setGeometry(QtCore.QRect(370, 170, 331, 321))
        self.camera2ImageLbl.setFrameShape(QtWidgets.QFrame.Box)
        self.camera2ImageLbl.setFrameShadow(QtWidgets.QFrame.Raised)
        self.camera2ImageLbl.setLineWidth(2)
        self.camera2ImageLbl.setText("")
        self.camera2ImageLbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.camera2ImageLbl.setObjectName("camera2ImageLbl")
        pixmap = pixmap.scaled(self.camera2ImageLbl.width(), self.camera2ImageLbl.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
        self.camera2ImageLbl.setPixmap(pixmap) # Set the pixmap onto the label
        self.camera2Lbl = QtWidgets.QLabel(self.centralwidget)
        self.camera2Lbl.setGeometry(QtCore.QRect(380, 490, 311, 21))
        self.camera2Lbl.setFocusPolicy(QtCore.Qt.NoFocus)
        self.camera2Lbl.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.camera2Lbl.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.camera2Lbl.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.camera2Lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.camera2Lbl.setObjectName("camera2Lbl")
        self.camera1Lbl = QtWidgets.QLabel(self.centralwidget)
        self.camera1Lbl.setGeometry(QtCore.QRect(30, 490, 331, 21))
        self.camera1Lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.camera1Lbl.setObjectName("camera1Lbl")
        self.quitBtn = QtWidgets.QPushButton(self.centralwidget)
        self.quitBtn.setGeometry(QtCore.QRect(300, 540, 141, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.quitBtn.setPalette(palette)
        self.quitBtn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.quitBtn.setAutoRepeatDelay(298)
        self.quitBtn.setObjectName("quitBtn")
        self.previewBtn = QtWidgets.QPushButton(self.centralwidget)
        self.previewBtn.setGeometry(QtCore.QRect(110, 50, 141, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(233, 185, 110))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(233, 185, 110))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(233, 185, 110))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.previewBtn.setPalette(palette)
        self.previewBtn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.previewBtn.setAutoRepeatDelay(298)
        self.previewBtn.setObjectName("previewBtn")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 743, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.p_timer = QtCore.QTimer()
        self.p_timer.setInterval(200)
        self.p_timer.timeout.connect(self.preview_timer)
        self.r_timer = QtCore.QTimer()
        self.r_timer.setInterval(200)
        self.r_timer.timeout.connect(self.record_timer)

        self.cur_cmnd = STOP_CMND

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.recordBtn.clicked.connect(self.record)
        self.previewBtn.clicked.connect(self.preview)
        self.stopBtn.clicked.connect(self.stop)
        self.quitBtn.clicked.connect(self.quit)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "OperVu Video Capture"))
        self.recordBtn.setText(_translate("MainWindow", "Record"))
        self.stopBtn.setText(_translate("MainWindow", "Stop"))
        self.recordingStatusLbl.setText(_translate("MainWindow", "Recording Status"))
        self.camera2Lbl.setText(_translate("MainWindow", "Camera 2"))
        self.camera1Lbl.setText(_translate("MainWindow", "Camera 1"))
        self.quitBtn.setText(_translate("MainWindow", "Quit"))
        self.previewBtn.setText(_translate("MainWindow", "Preview"))

    def record(self):
        self.recordBtn.setEnabled(False)
        self.previewBtn.setEnabled(False)
        self.quitBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.statusEdit.setText("Recording...")
        self.cur_cmnd = RECORD_CMND
        cmnd_q.put(RECORD_CMND)
        self.r_timer.start()

    def record_timer(self):
        if self.cur_cmnd != RECORD_CMND:
            self.r_timer.stop()
        while status_q.empty():
            return
        num_cameras = status_q.get()
        pixmap = QtGui.QPixmap("camera_1/image.jpg") # Setup pixmap with the provided cartoon camera image
        pixmap = pixmap.scaled(self.camera1ImageLbl.width(), self.camera1ImageLbl.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
        self.camera1ImageLbl.setPixmap(pixmap) # Set the pixmap onto the label
        if num_cameras > 1:
            pixmap = QtGui.QPixmap("camera_2/image.jpg") # Setup pixmap with the provided cartoon camera image
            pixmap = pixmap.scaled(self.camera2ImageLbl.width(), self.camera2ImageLbl.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
            self.camera2ImageLbl.setPixmap(pixmap) # Set the pixmap onto the label

    def preview(self):
        self.previewBtn.setEnabled(False)
        self.recordBtn.setEnabled(False)
        self.quitBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.statusEdit.setText("Previewing...")
        self.cur_cmnd = PREVIEW_CMND
        cmnd_q.put(PREVIEW_CMND)
        self.p_timer.start()

    def preview_timer(self):
        if self.cur_cmnd != PREVIEW_CMND:
            self.p_timer.stop()
        while status_q.empty():
            return
        num_cameras = status_q.get()
        pixmap = QtGui.QPixmap("camera_1/image.jpg") # Setup pixmap with the provided cartoon camera image
        pixmap = pixmap.scaled(self.camera1ImageLbl.width(), self.camera1ImageLbl.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
        self.camera1ImageLbl.setPixmap(pixmap) # Set the pixmap onto the label
        if num_cameras > 1:
            pixmap = QtGui.QPixmap("camera_2/image.jpg") # Setup pixmap with the provided cartoon camera image
            pixmap = pixmap.scaled(self.camera2ImageLbl.width(), self.camera2ImageLbl.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
            self.camera2ImageLbl.setPixmap(pixmap) # Set the pixmap onto the label
        cmnd_q.put(PREVIEW_CMND)


    def stop(self):
        if self.cur_cmnd == PREVIEW_CMND:
            self.p_timer.stop()
        elif self.cur_cmnd == RECORD_CMND:
            self.r_timer.stop()
        self.stopBtn.setEnabled(False)
        self.previewBtn.setEnabled(True)
        self.recordBtn.setEnabled(True)
        self.quitBtn.setEnabled(True)
        self.statusEdit.setText("Stopped")
        pixmap = QtGui.QPixmap("camera.jpg") # Setup pixmap with the provided cartoon camera image
        pixmap = pixmap.scaled(self.camera1ImageLbl.width(), self.camera1ImageLbl.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
        self.camera1ImageLbl.setPixmap(pixmap) # Set the pixmap onto the label
        pixmap = pixmap.scaled(self.camera2ImageLbl.width(), self.camera2ImageLbl.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
        self.camera2ImageLbl.setPixmap(pixmap) # Set the pixmap onto the label
        cmnd_q.put(STOP_CMND)
        self.cur_cmnd = STOP_CMND

    def quit(self):
        cmnd_q.put(QUIT_CMND)
        app.quit()



if __name__ == "__main__":
    import sys

    cam_ctl = camera_control.CameraControl(cmnd_q, status_q)
    cam_ctl.start()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
