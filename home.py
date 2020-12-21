import ntpath

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, \
    QMainWindow, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QRect, Qt
import os
from sys import platform


class MyCustomItem(QWidget):
    def __init__(self, text, img_path):
        super(MyCustomItem, self).__init__()
        self.img_path = img_path
        self.project_title = QLabel(text)
        self.project_title.setGeometry(QRect(0, 0, 320, 100))
        self.image = QLabel()
        self.image.setGeometry(QRect(0, 0, 320, 100))
        self.image.setPixmap(QPixmap(img_path))
        self.textbox = QLineEdit()
        self.textbox.setStyleSheet("border: 1px solid black;")
        self.set_ui()

    def get_line(self):
        return '{ipath} {itext}\n'.format(ipath=self.img_path, itext=self.textbox.text())

    def set_ui(self):
        grid_box = QHBoxLayout()
        grid_box.addWidget(self.image)
        grid_box.addWidget(self.project_title)
        grid_box.addWidget(self.textbox)

        self.setLayout(grid_box)
        self.show()


class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.initUI()
        self.resize(800, 600)
        self.setWindowTitle("FSNS tool")

        scrollarea = QScrollArea()
        scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollarea.setWidgetResizable(True)
        self.setCentralWidget(scrollarea)

        widget = QWidget()
        scrollarea.setWidget(widget)

        qvboxlayout = QVBoxLayout()
        self.verticalLayout = qvboxlayout
        widget.setLayout(qvboxlayout)

        menubar = QtWidgets.QMenuBar(self)
        menubar.setGeometry(QRect(0, 0, 800, 22))
        menubar.setObjectName("menubar")
        menuFile = QtWidgets.QMenu(menubar)
        menuFile.setObjectName("menuFile")
        self.setMenuBar(menubar)
        menubar.addAction(menuFile.menuAction())
        menuFile.setTitle("File")

        actionOpen_Folder = QtWidgets.QAction(self)
        menuFile.addAction(actionOpen_Folder)
        actionOpen_Folder.setText("Load Image Folder")
        actionOpen_Folder.setShortcut("Ctrl+O")
        actionOpen_Folder.triggered.connect(self.onopenfolder)

        actionOpen_Txt_File = QtWidgets.QAction(self)
        menuFile.addAction(actionOpen_Txt_File)
        actionOpen_Txt_File.setText("Load txt file")
        actionOpen_Txt_File.setShortcut("Ctrl+L")
        actionOpen_Txt_File.triggered.connect(self.onloadtxtfile)

        actionSave_File = QtWidgets.QAction(self)
        menuFile.addAction(actionSave_File)
        actionSave_File.setText("Save txt file")
        actionSave_File.setShortcut("Ctrl+S")
        actionSave_File.triggered.connect(self.onsavefile)

    def onloadtxtfile(self):
        dialog = QFileDialog()
        txtfilepath, _ = dialog.getOpenFileName(None, "Select txt File", os.getcwd(), '*.txt')
        if txtfilepath:
            with open(txtfilepath, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    image_full_path, inputted_txt = line.split(" ")
                    inputted_txt = inputted_txt.strip()
                    image_name = ntpath.basename(image_full_path)
                    for i in reversed(range(self.verticalLayout.count())):
                        widget_to_fill = self.verticalLayout.itemAt(i).widget()
                        if isinstance(widget_to_fill, MyCustomItem):
                            if widget_to_fill.objectName() == image_name:
                                widget_to_fill.textbox.setText(inputted_txt)
                f.close()

    def onsavefile(self):
        problemDetected = False
        filedata = ''
        for i in range(self.verticalLayout.count()):
            mycustomitem = self.verticalLayout.itemAt(i).widget()
            if isinstance(mycustomitem, MyCustomItem):
                if isinstance(mycustomitem.textbox, QLineEdit):
                    if mycustomitem.textbox.text() == "":
                        problemDetected = True
                        mycustomitem.textbox.setStyleSheet("border: 1px solid red;")
                    else:
                        filedata += mycustomitem.get_line()
                        mycustomitem.textbox.setStyleSheet("border: 1px solid black;")

        if not problemDetected:
            name = QtWidgets.QFileDialog.getSaveFileName(self, "Save FSNS File", os.getcwd(), '.txt')[0]
            if not name == "":
                file = open(name, 'w')
                file.write(filedata)
                file.close()

    def onopenfolder(self):
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder", os.getcwd())
        if not folder_path == '':
            allfiles = os.listdir(folder_path)
            for fichier in allfiles[:]:
                if not (fichier.endswith(".png")) and not (fichier.endswith(".jpg")):
                    allfiles.remove(fichier)
            if platform == "win32":
                allfiles.sort(key=lambda x: os.stat(os.path.join(folder_path, x)).st_ctime, reverse=True)
            else:
                allfiles.sort(key=lambda x: os.stat(os.path.join(folder_path, x)).st_mtime, reverse=True)
            for i in reversed(range(self.verticalLayout.count())):
                widgetToRemove = self.verticalLayout.itemAt(i).widget()
                self.verticalLayout.removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
            counter = 1
            for image in allfiles:
                imagefullpath = os.path.join(folder_path, image)
                item = MyCustomItem(image, imagefullpath)
                item.setObjectName(image)
                self.verticalLayout.addWidget(item)
                counter += 1


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main = HomeWindow()
    main.show()
    sys.exit(app.exec_())
