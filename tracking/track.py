#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'track.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets

import predict

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1913, 1967)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(910, 10, 91, 41))
        self.startButton.setObjectName("startButton")
        self.nextButton = QtWidgets.QPushButton(self.centralwidget)
        self.nextButton.setGeometry(QtCore.QRect(910, 900, 91, 41))
        self.nextButton.setObjectName("nextButton")
        self.image1 = QtWidgets.QLabel(self.centralwidget)
        self.image1.setGeometry(QtCore.QRect(90, 70, 800, 800))
        self.image1.setFrameShape(QtWidgets.QFrame.Box)
        self.image1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.image1.setLineWidth(2)
        self.image1.setText("")
        self.image1.setObjectName("image1")
        self.image2 = QtWidgets.QLabel(self.centralwidget)
        self.image2.setGeometry(QtCore.QRect(1010, 70, 800, 800))
        self.image2.setFrameShape(QtWidgets.QFrame.Box)
        self.image2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.image2.setLineWidth(2)
        self.image2.setText("")
        self.image2.setObjectName("image2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(90, 870, 801, 20))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(1010, 870, 801, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.prevSI = QtWidgets.QTextBrowser(self.centralwidget)
        self.prevSI.setGeometry(QtCore.QRect(90, 970, 131, 621))
        self.prevSI.setDocumentTitle("")
        self.prevSI.setObjectName("prevSI")
        self.quitButton = QtWidgets.QPushButton(self.centralwidget)
        self.quitButton.setGeometry(QtCore.QRect(900, 1610, 91, 41))
        self.quitButton.setObjectName("quitButton")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(90, 950, 131, 20))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.prevTrkID = QtWidgets.QTextBrowser(self.centralwidget)
        self.prevTrkID.setGeometry(QtCore.QRect(230, 970, 41, 621))
        self.prevTrkID.setDocumentTitle("")
        self.prevTrkID.setObjectName("prevTrkID")
        self.prevEstVel = QtWidgets.QTextBrowser(self.centralwidget)
        self.prevEstVel.setGeometry(QtCore.QRect(630, 970, 101, 621))
        self.prevEstVel.setDocumentTitle("")
        self.prevEstVel.setObjectName("prevEstVel")
        self.prevBBox = QtWidgets.QTextBrowser(self.centralwidget)
        self.prevBBox.setGeometry(QtCore.QRect(280, 970, 181, 621))
        self.prevBBox.setDocumentTitle("")
        self.prevBBox.setObjectName("prevBBox")
        self.prevScore = QtWidgets.QTextBrowser(self.centralwidget)
        self.prevScore.setGeometry(QtCore.QRect(470, 970, 41, 621))
        self.prevScore.setDocumentTitle("")
        self.prevScore.setObjectName("prevScore")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(230, 950, 41, 20))
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(630, 950, 101, 20))
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(280, 950, 181, 20))
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(470, 950, 41, 20))
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.nextTrkID = QtWidgets.QTextBrowser(self.centralwidget)
        self.nextTrkID.setGeometry(QtCore.QRect(1150, 970, 41, 621))
        self.nextTrkID.setDocumentTitle("")
        self.nextTrkID.setObjectName("nextTrkID")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(1150, 950, 41, 20))
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.nextBBox = QtWidgets.QTextBrowser(self.centralwidget)
        self.nextBBox.setGeometry(QtCore.QRect(1200, 970, 181, 621))
        self.nextBBox.setDocumentTitle("")
        self.nextBBox.setObjectName("nextBBox")
        self.nextEstVel = QtWidgets.QTextBrowser(self.centralwidget)
        self.nextEstVel.setGeometry(QtCore.QRect(1550, 970, 101, 621))
        self.nextEstVel.setDocumentTitle("")
        self.nextEstVel.setObjectName("nextEstVel")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(1390, 950, 41, 20))
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.nextSI = QtWidgets.QTextBrowser(self.centralwidget)
        self.nextSI.setGeometry(QtCore.QRect(1010, 970, 131, 621))
        self.nextSI.setDocumentTitle("")
        self.nextSI.setObjectName("nextSI")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(1550, 950, 101, 20))
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.nextScore = QtWidgets.QTextBrowser(self.centralwidget)
        self.nextScore.setGeometry(QtCore.QRect(1390, 970, 41, 621))
        self.nextScore.setDocumentTitle("")
        self.nextScore.setObjectName("nextScore")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(1010, 950, 131, 20))
        self.label_13.setAlignment(QtCore.Qt.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(1200, 950, 181, 20))
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.prevCenter = QtWidgets.QTextBrowser(self.centralwidget)
        self.prevCenter.setGeometry(QtCore.QRect(520, 970, 101, 621))
        self.prevCenter.setDocumentTitle("")
        self.prevCenter.setObjectName("prevCenter")
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setGeometry(QtCore.QRect(520, 950, 101, 20))
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.prevActVel = QtWidgets.QTextBrowser(self.centralwidget)
        self.prevActVel.setGeometry(QtCore.QRect(740, 970, 101, 621))
        self.prevActVel.setDocumentTitle("")
        self.prevActVel.setObjectName("prevActVel")
        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setGeometry(QtCore.QRect(740, 950, 101, 20))
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.nextCenter = QtWidgets.QTextBrowser(self.centralwidget)
        self.nextCenter.setGeometry(QtCore.QRect(1440, 970, 101, 621))
        self.nextCenter.setDocumentTitle("")
        self.nextCenter.setObjectName("nextCenter")
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setGeometry(QtCore.QRect(1440, 950, 101, 20))
        self.label_17.setAlignment(QtCore.Qt.AlignCenter)
        self.label_17.setObjectName("label_17")
        self.nextActVel = QtWidgets.QTextBrowser(self.centralwidget)
        self.nextActVel.setGeometry(QtCore.QRect(1660, 970, 101, 621))
        self.nextActVel.setDocumentTitle("")
        self.nextActVel.setObjectName("nextActVel")
        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        self.label_18.setGeometry(QtCore.QRect(1660, 950, 101, 20))
        self.label_18.setAlignment(QtCore.Qt.AlignCenter)
        self.label_18.setObjectName("label_18")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1913, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.startButton.clicked.connect(self.start)
        self.nextButton.clicked.connect(self.next)
        self.quitButton.clicked.connect(self.quit)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Simple SI Tracker"))
        self.startButton.setText(_translate("MainWindow", "START"))
        self.nextButton.setText(_translate("MainWindow", "NEXT"))
        self.label.setText(_translate("MainWindow", "Previous Frame"))
        self.label_2.setText(_translate("MainWindow", "Current Frame"))
        self.prevSI.setPlaceholderText(_translate("MainWindow", "Obstruction"))
        self.quitButton.setText(_translate("MainWindow", "QUIT"))
        self.label_5.setText(_translate("MainWindow", "SI"))
        self.prevTrkID.setPlaceholderText(_translate("MainWindow", "0001"))
        self.prevActVel.setPlaceholderText(_translate("MainWindow", "[2000, 2000]"))
        self.prevBBox.setPlaceholderText(_translate("MainWindow", "[2000, 2000, 2000, 2000]"))
        self.prevScore.setPlaceholderText(_translate("MainWindow", "0.99"))
        self.label_6.setText(_translate("MainWindow", "Trk ID"))
        self.label_7.setText(_translate("MainWindow", "Estim. Velocity"))
        self.label_8.setText(_translate("MainWindow", "BBox [x1, y1, x2, y2]"))
        self.label_9.setText(_translate("MainWindow", "Score"))
        self.nextTrkID.setPlaceholderText(_translate("MainWindow", "0001"))
        self.label_10.setText(_translate("MainWindow", "Trk ID"))
        self.nextBBox.setPlaceholderText(_translate("MainWindow", "[2000, 2000, 2000, 2000]"))
        self.nextActVel.setPlaceholderText(_translate("MainWindow", "[2000, 2000]"))
        self.label_11.setText(_translate("MainWindow", "Score"))
        self.nextSI.setPlaceholderText(_translate("MainWindow", "Obstruction"))
        self.label_12.setText(_translate("MainWindow", "Estim. Velocity"))
        self.nextScore.setPlaceholderText(_translate("MainWindow", "0.99"))
        self.label_13.setText(_translate("MainWindow", "SI"))
        self.label_14.setText(_translate("MainWindow", "BBox [x1, y1, x2, y2]"))
        self.prevCenter.setPlaceholderText(_translate("MainWindow", "[2000, 2000]"))
        self.label_15.setText(_translate("MainWindow", "Center"))
        self.prevEstVel.setPlaceholderText(_translate("MainWindow", "[2000, 2000]"))
        self.label_16.setText(_translate("MainWindow", "Actual Velocity"))
        self.nextCenter.setPlaceholderText(_translate("MainWindow", "[2000, 2000]"))
        self.label_17.setText(_translate("MainWindow", "Center"))
        self.nextEstVel.setPlaceholderText(_translate("MainWindow", "[2000, 2000]"))
        self.label_18.setText(_translate("MainWindow", "Actual Velocity"))


    def start(self):
        self.startButton.setEnabled(False)
        self.nextButton.setEnabled(True)
        image, pred_info = predict.predict_first()
        qimg = QtGui.QImage(image,image.shape[0],image.shape[1], QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap(qimg)
        pixmap = pixmap.scaled(self.image2.width(), self.image2.height(), QtCore.Qt.KeepAspectRatio) # Scale pixmap
        self.image2.setPixmap(pixmap) # Set the pixmap onto the label
        self.nextSI.setText(pred_info['si'])
        self.nextTrkID.setText(pred_info['id'])
        self.nextBBox.setText(pred_info['box'])
        self.nextScore.setText(pred_info['scr'])
        self.nextCenter.setText(pred_info['cen'])
        self.nextEstVel.setText(pred_info['vel-est'])
        self.nextActVel.setText(pred_info['vel-act'])

    def next(self):
        qimg = self.image2.pixmap()
        self.image1.setPixmap(qimg)
        self.prevSI.setText(self.nextSI.toPlainText())
        self.prevTrkID.setText(self.nextTrkID.toPlainText())
        self.prevBBox.setText(self.nextBBox.toPlainText())
        self.prevScore.setText(self.nextScore.toPlainText())
        self.prevCenter.setText(self.nextCenter.toPlainText())
        self.prevEstVel.setText(self.nextEstVel.toPlainText())
        self.prevActVel.setText(self.nextActVel.toPlainText())
        self.start()

    def quit(self):
        predict.quit()
        app.quit()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
