# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/setting.ui'
#
# Created by: PyQt5 UI code generator 5.15.5
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
#Test


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setToolTip("")
        self.formLayoutWidget = QtWidgets.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(70, 100, 261, 80))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.TidakDiulang = QtWidgets.QRadioButton(self.formLayoutWidget)
        self.TidakDiulang.setObjectName("TidakDiulang")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.TidakDiulang)
        self.SelaluDiulang = QtWidgets.QRadioButton(self.formLayoutWidget)
        self.SelaluDiulang.setObjectName("SelaluDiulang")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.SelaluDiulang)
        self.formLayoutWidget_2 = QtWidgets.QWidget(Dialog)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(70, 20, 261, 80))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.MenggabaikanShortcut = QtWidgets.QCheckBox(self.formLayoutWidget_2)
        self.MenggabaikanShortcut.setObjectName("MenggabaikanShortcut")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.MenggabaikanShortcut)
        self.TopSaatRecord = QtWidgets.QCheckBox(self.formLayoutWidget_2)
        self.TopSaatRecord.setObjectName("TopSaatRecord")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.TopSaatRecord)
        self.TopMauUnpause = QtWidgets.QCheckBox(self.formLayoutWidget_2)
        self.TopMauUnpause.setObjectName("TopMauUnpause")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.TopMauUnpause)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(60, 181, 121, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(220, 180, 113, 51))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.lineEdit.setFont(font)
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Settingan loop"))
        self.TidakDiulang.setText(_translate("Dialog", "Tidak diulang"))
        self.SelaluDiulang.setText(_translate("Dialog", "Selalu diulang"))
        self.label_2.setText(_translate("Dialog", "Settingan       "))
        self.MenggabaikanShortcut.setText(_translate("Dialog", "Mengabaikan keyboard shortcuts"))
        self.TopSaatRecord.setText(_translate("Dialog", "Always top saat mulai recorder"))
        self.TopMauUnpause.setText(_translate("Dialog", "Always top saat mau unpause"))
        self.pushButton.setText(_translate("Dialog", "Ganti Keybind"))
        self.lineEdit.setText(_translate("Dialog", "F6"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())