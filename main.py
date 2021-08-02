# IMPORT / GUI AND MODULES AND WIDGETS

import sys
import os
import platform
from modules import *
from widgets import *
import cv2,time
from PySide6.QtGui import QImage, QPixmap
from PySide6 import QtWidgets


os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

widgets = None # SET AS GLOBAL WIDGETS 

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "PyDracula - Modern GUI"
        description = "PyDracula APP - Theme with colors based on Dracula for Python."
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////


        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)
        self.new = QWidget()
        self.check=False
        self.images = []
        self.videos=[]
        self.vidlist=[]
        self.i,self.j=0,0
        self.saveimg=False
        self.savevid=False
        widgets.startcamera.clicked.connect(self.start_camera)
        widgets.imgtable.selectionModel().selectionChanged.connect(self.imgselected)
        widgets.vidtable.selectionModel().selectionChanged.connect(self.vidselected)
        widgets.saveimage.clicked.connect(self.save_image)
        widgets.savevideo.clicked.connect(self.save_video)
    
 
        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme: 
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

        
    def start_camera(self):
        self.check=True
        self.loadImage()
    
    def vidselected(self,selected):
        if selected.indexes():
            id=selected.indexes()[0].row()
            if id<=len(self.videos)-1:
                for img in self.videos[id]:
                    cv2.waitKey(1)
                    widgets.imglabel.setPixmap(QPixmap(QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888).rgbSwapped())) 

    def imgselected(self,selected):
        if selected.indexes():
            id=selected.indexes()[0].row()
            if id<=len(self.images)-1:self.setPhoto(self.images[id],widgets.imglabel)
          
    def save_video(self):
        self.savevid=True
        self.start_time = time.time()

    def getimglabel(self,img):
        imagelabel=QtWidgets.QLabel(self.new)
        imagelabel.setText("")
        imagelabel.setScaledContents(True)  
        pixmap = QPixmap(QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888).rgbSwapped())
        imagelabel.setPixmap(pixmap) 
        return imagelabel
   
    def addimgtable(self,img,table,i):
        item=self.getimglabel(img)
        table.setCellWidget(i,0,item)
        table.setRowHeight(i,60)
        table.setColumnWidth(0,130)
     
    def save_image(self):
        
        self.saveimg=True

    def setPhoto(self,img,label):
        pixmap = QPixmap(QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888).rgbSwapped())
        label.setPixmap(pixmap) 

    def loadImage(self):
        vid = cv2.VideoCapture(0)
        while(True):
            img, image = vid.read()
            if self.saveimg:
                self.saveimg=False
                self.images.append(image)
                self.addimgtable(image,widgets.imgtable,self.i)
                self.i=self.i+1
                
            if self.savevid:
                self.vidlist.append(image.copy())
                if (time.time()-self.start_time) > 2:
                    self.videos.append(self.vidlist)
                    self.savevid=False
                    self.vidlist=[]
                    self.addimgtable(image,widgets.vidtable,self.j)
                    self.j=self.j+1
            self.setPhoto(image,widgets.vidlabel)

            key = cv2.waitKey(1) & 0xFF
            if not self.check:break
        cv2.destroyAllWindows


    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
