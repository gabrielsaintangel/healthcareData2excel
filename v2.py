# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'v2.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(705, 404)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 461, 301))
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 20, 61, 16))
        self.label.setObjectName("label")
        self.starting_zip_input = QtWidgets.QLineEdit(self.groupBox)
        self.starting_zip_input.setGeometry(QtCore.QRect(100, 20, 113, 20))
        self.starting_zip_input.setObjectName("starting_zip_input")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 71, 16))
        self.label_2.setObjectName("label_2")
        self.radius_slider = QtWidgets.QSlider(self.groupBox)
        self.radius_slider.setGeometry(QtCore.QRect(100, 60, 160, 22))
        self.radius_slider.setMinimum(1)
        self.radius_slider.setMaximum(200)
        self.radius_slider.setOrientation(QtCore.Qt.Horizontal)
        self.radius_slider.setObjectName("radius_slider")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(20, 120, 121, 16))
        self.label_3.setObjectName("label_3")
        self.slider_radius_output = QtWidgets.QLabel(self.groupBox)
        self.slider_radius_output.setGeometry(QtCore.QRect(140, 80, 47, 13))
        self.slider_radius_output.setObjectName("slider_radius_output")
        self.keyword_list_widget = QtWidgets.QListWidget(self.groupBox)
        self.keyword_list_widget.setGeometry(QtCore.QRect(20, 150, 431, 101))
        self.keyword_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.keyword_list_widget.setObjectName("keyword_list_widget")
        self.remove_item_button = QtWidgets.QPushButton(self.groupBox)
        self.remove_item_button.setGeometry(QtCore.QRect(144, 260, 121, 23))
        self.remove_item_button.setObjectName("remove_item_button")
        self.add_item_button = QtWidgets.QPushButton(self.groupBox)
        self.add_item_button.setGeometry(QtCore.QRect(40, 260, 75, 23))
        self.add_item_button.setObjectName("add_item_button")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(490, 10, 201, 301))
        self.groupBox_2.setObjectName("groupBox_2")
        self.write_excel_check = QtWidgets.QCheckBox(self.groupBox_2)
        self.write_excel_check.setGeometry(QtCore.QRect(10, 30, 151, 17))
        self.write_excel_check.setObjectName("write_excel_check")
        self.show_map_check = QtWidgets.QCheckBox(self.groupBox_2)
        self.show_map_check.setGeometry(QtCore.QRect(10, 90, 141, 17))
        self.show_map_check.setObjectName("show_map_check")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(10, 60, 61, 16))
        self.label_4.setObjectName("label_4")
        self.filename_input = QtWidgets.QLineEdit(self.groupBox_2)
        self.filename_input.setEnabled(True)
        self.filename_input.setGeometry(QtCore.QRect(60, 60, 113, 20))
        self.filename_input.setObjectName("filename_input")
        self.generate_button = QtWidgets.QPushButton(Dialog)
        self.generate_button.setGeometry(QtCore.QRect(30, 330, 101, 23))
        self.generate_button.setObjectName("generate_button")
        self.progress_bar = QtWidgets.QProgressBar(Dialog)
        self.progress_bar.setGeometry(QtCore.QRect(20, 370, 471, 23))
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setFormat("")
        self.progress_bar.setObjectName("progress_bar")
        self.reset_button = QtWidgets.QPushButton(Dialog)
        self.reset_button.setGeometry(QtCore.QRect(190, 330, 75, 23))
        self.reset_button.setObjectName("reset_button")
        self.progress_label = QtWidgets.QLabel(Dialog)
        self.progress_label.setGeometry(QtCore.QRect(470, 370, 111, 16))
        self.progress_label.setText("")
        self.progress_label.setObjectName("progress_label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "Search Paramaters"))
        self.label.setText(_translate("Dialog", "Starting Zip"))
        self.label_2.setText(_translate("Dialog", "Search Radius"))
        self.label_3.setText(_translate("Dialog", "Selected Practice Types:"))
        self.slider_radius_output.setText(_translate("Dialog", "0 Miles"))
        self.keyword_list_widget.setSortingEnabled(True)
        self.remove_item_button.setText(_translate("Dialog", "Remove Selected Items"))
        self.add_item_button.setText(_translate("Dialog", "Add Item"))
        self.groupBox_2.setTitle(_translate("Dialog", "Output Paramaters"))
        self.write_excel_check.setText(_translate("Dialog", "Write Excel"))
        self.show_map_check.setText(_translate("Dialog", "Show results on map"))
        self.label_4.setText(_translate("Dialog", "File name"))
        self.generate_button.setText(_translate("Dialog", "Generate"))
        self.reset_button.setText(_translate("Dialog", "Reset"))
