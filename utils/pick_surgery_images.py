#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pick_surgery_images.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import os
import sys
import time
import shutil

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.imageLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageLabel.setGeometry(QtCore.QRect(1, 1, 900, 900))
        self.imageLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imageLabel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.imageLabel.setLineWidth(4)
        self.imageLabel.setText("")
        self.imageLabel.setObjectName("imageLabel")
        self.imageNameEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.imageNameEdit.setGeometry(QtCore.QRect(20, 910, 113, 25))
        self.imageNameEdit.setObjectName("imageNameEdit")
        self.imageNameLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageNameLabel.setGeometry(QtCore.QRect(40, 940, 91, 17))
        self.imageNameLabel.setObjectName("imageNameLabel")
        self.nextButton = QtWidgets.QPushButton(self.centralwidget)
        self.nextButton.setGeometry(QtCore.QRect(310, 910, 89, 31))
        self.nextButton.setObjectName("nextButton")
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(450, 910, 91, 31))
        self.saveButton.setObjectName("saveButton")
        self.countLabel = QtWidgets.QLabel(self.centralwidget)
        self.countLabel.setGeometry(QtCore.QRect(770, 940, 67, 17))
        self.countLabel.setObjectName("countLabel")
        self.countEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.countEdit.setGeometry(QtCore.QRect(730, 910, 113, 25))
        self.countEdit.setObjectName("countEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.saveButton.clicked.connect(self.save)
        self.nextButton.clicked.connect(self.next)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.imageNameLabel.setText(_translate("MainWindow", "Image Name"))
        self.nextButton.setText(_translate("MainWindow", "NEXT"))
        self.saveButton.setText(_translate("MainWindow", "SAVE"))
        self.countLabel.setText(_translate("MainWindow", "Count"))

    def save(self):

        if self.count >= 1000:
            self.count = 1
            self.dirNum = str(int(self.dirNum) + 1)
            if not os.path.exists(self.outputDir + self.dirNum):
                os.makedirs(self.outputDir + self.dirNum)
        else:
            self.count += 1
        shutil.move(os.path.join(self.imageDir, self.imageName), self.outputDir + self.dirNum)
        self.next()


    def next(self):

        self.imageListIndex += 1
        if self.imageListIndex >= len(self.imageList):
            sys.exit()

        self.imageName = self.imageList[self.imageListIndex]
        self.imageNameEdit.setText(str(self.imageName))
        self.countEdit.setText(str(self.count))
        pixmap = QtGui.QPixmap(os.path.join(self.imageDir, self.imageName))
        pixmap = pixmap.scaled(self.imageLabel.width(), self.imageLabel.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
        self.imageLabel.setPixmap(pixmap) # Set the pixmap onto the label
        with open("image.txt", 'w') as f:
            f.write(self.imageName + ' ' + str(self.count) + ' ' + self.dirNum)


def main(args):

    global app
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)



    ui.imageDir = args[0]
    ui.outputDir = args[1]

    if os.path.exists('image.txt'):
        with open('image.txt') as f:
            ui.imageName, ui.count, ui.dirNum = f.read().split()
            ui.count = int(ui.count)

    ui.imageList = sorted(os.listdir(ui.imageDir))
    ui.imageListIndex = 0;
    for i, imgName in enumerate(ui.imageList):
        if imgName == ui.imageName:
            ui.imageListIndex = i
            break

    if not os.path.exists(ui.outputDir + ui.dirNum):
        os.makedirs(ui.outputDir + ui.dirNum)


    ui.imageNameEdit.setText(str(ui.imageName))
    ui.countEdit.setText(str(ui.count))

    try:
        pixmap = QtGui.QPixmap(os.path.join(ui.imageDir, ui.imageName))
        pixmap = pixmap.scaled(ui.imageLabel.width(), ui.imageLabel.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
        ui.imageLabel.setPixmap(pixmap) # Set the pixmap onto the label
    except Exception as exc:
        print(exc)


    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    args = ['/home/kamiar/projects/opervu/images/surgery_images_9_18-1', '/home/kamiar/projects/opervu/images/training/train_']
    main(args)
