# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

import sys
import os
import platform
import cv2
import time
import numpy as np
from datetime import datetime
from PySide6.QtWidgets import QLabel as newlabel

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        title = "DeltaCare"
        description = "DeltaCare"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        UIFunctions.uiDefinitions(self)

        # BUTTONS CLICK
        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)


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
        self.new = QWidget()
        self.stream = True
        self.show_enhanced = False
        self.recording = False

        self.camera_index = 0
        self.vid = None
        self.video_writer = None
        self.recording_start_time = None
        self.current_test_type = 'morphology'

        #self.params = read_yaml()
        #self.microscopeSW = MicroscopeSW(self.params)
        #self.motility_analyzer = MotilityAnalayzer(self.params)
        #self.morphology_analyzer = MorphologyAnalyzer(self.params)
        self.analyzed_image = None
        self.last_selected_item = None

        #Listener(on_press = self.microscopeSW.key_handler).start()
        self.gui_results_dir = 'gui_results'
        self.saving_dir = os.path.join(self.gui_results_dir, datetime.now().strftime("%H-%M-%S"))

        os.makedirs(self.gui_results_dir, exist_ok=True)
        os.makedirs(self.saving_dir, exist_ok = True)

        self.items = []
        #_______________________________________________________________

        self.check=False
        self.inoutvalue=0
        self.leftrightvalue=0
        self.leftrightvalue=0
        self.images = []
        self.videos=[]
        self.i,self.j=0,0
        self.init_gui_logic()

    def test_type_callback(self, index):
        new_test_type = widgets.testtypebox.itemText(index)
        self.current_test_type = new_test_type
        #self.params['test_type'] = self.current_test_type  

    def start_camera(self):
        #TODO check if the selected camera index is not working (its camera is not working)
        local_camera_index = self.camera_index
        if self.vid : return # return if camera is already started
        self.vid = cv2.VideoCapture(local_camera_index, cv2.CAP_DSHOW)
        
        while self.stream:
            # s = time.time()
            ret, image = self.vid.read()

            if not ret : print("cannot read frame")
            # self.microscopeSW.update_image(image)

            if self.recording_start_time:
                if time.time() - self.recording_start_time < 3 :
                    self.video_writer.write(cv2.resize(image,(400,400)))
                    image = cv2.putText( image,'recording', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255) )
                else:
                    self.video_writer.release() 
                    self.recording_start_time = None
                    self.addimgtable(image, widgets.imgtable, self.i)
                    self.i += 1

                    
            
            if self.show_enhanced:
                image = cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)
            self.setPhoto(image, widgets.vidlabel)
            
            cv2.waitKey(1)
            if local_camera_index != self.camera_index:
                local_camera_index = self.camera_index
                self.vid.release()
                self.vid = cv2.VideoCapture(local_camera_index, cv2.CAP_DSHOW)

        print("releasing vid")
        self.vid.release()

    def imgselected(self,selected):
        if selected.indexes():
            id=selected.indexes()[0].row()
            if id >= len(self.items): return
            item = self.items[id]
            self.last_selected_item = item
            if item[0] == 'image':
                image = cv2.imread(item[1])
                self.setPhoto(image, widgets.imglabel)
            else:
                cam = cv2.VideoCapture(item[1]) 
                total = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
                for d in range(total):
                    ret, frame = cam.read()
                    if not ret: continue
                    self.setPhoto(frame, widgets.imglabel)
                    if cv2.waitKey(1) & 0xFF == ord('q'): break
   
    def save_video_callback(self):
        video_path = os.path.join(self.saving_dir, datetime.now().strftime("%H-%M-%S")) + '.avi'
        self.recording_start_time = time.time()
        self.video_writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*"MJPG"), 20,(400,400))
        #self.params['camera']['saving_fps'], (self.params['camera']['saving_size'], self.params['camera']['saving_size']))
        self.items.append(('video', video_path))

    def getimglabel(self,img,nimg=True):
        imagelabel = newlabel(self.new)
        imagelabel.setText("")
        imagelabel.setScaledContents(True)  
        if nimg: img = QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888).rgbSwapped()
        imagelabel.setPixmap(QPixmap(img))
        return imagelabel
   
    def addimgtable(self,img,table,i,nimg=True):
        item=self.getimglabel(img,nimg)
        table.setCellWidget(i,0,item)
        table.setRowHeight(i,100)
        table.setColumnWidth(0,200)
        
    def save_image_callback(self):
        image = widgets.vidlabel.grab().toImage()
        image_path = os.path.join(self.saving_dir, datetime.now().strftime("%H-%M-%S")) + '.jpg'
        image.save(image_path)
        self.addimgtable(image, widgets.imgtable, self.i,False) 
        self.i += 1
        self.items.append(('image', image_path))

    def setPhoto(self,img,label):
        pixmap = QPixmap(QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888).rgbSwapped())
        label.setPixmap(pixmap) 

    def closeEvent(self, event):
        print("closing")
        # self.microscopeSW.q.put('done')
        self.stream = False
        if self.recording: self.save_video()
        try: os.rmdir(self.saving_dir)
        except: pass
    
    def resetslider1(self):
        widgets.leftrightslider.setValue(0) 
    def resetslider2(self):
        widgets.updownslider.setValue(0) 
    def resetslider3(self):
        widgets.zoomslider.setValue(0)
    
    def changed_slider1(self):
        value = widgets.leftrightslider.value()
        if abs(value-self.leftrightvalue)==10:self.resetslider1()
        else:self.leftrightvalue=value
        print("Right/Left Value : ",value)
    def changed_slider2(self):
        value = widgets.updownslider.value()
        if abs(value-self.leftrightvalue)==10:self.resetslider2()
        else:self.updownvalue=value
        print("Up/Down Value : ",value)
    def changed_slider3(self):
        value = widgets.zoomslider.value()
        if abs(value-self.leftrightvalue)==10:self.resetslider3()
        else:self.inoutvalue=value
        print("Zoom Value : ",value)
        
    def analyze_callback(self):
        if self.last_selected_item is None : return # no image is selected yet
        #image = widgets.imglabel.grab().toImage
        #image = qimage2ndarray.rgb_view(image)
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #image = np.asarray(image)
        if self.last_selected_item[1].endswith('.jpg'):
            image = cv2.imread(self.last_selected_item[1])
            #self.analyzed_image = self.morphology_analyzer.analyze(image)
            #self.setPhoto(self.analyzed_image, widgets.imglabel)
        else:
            pass # motility

    def auto_focus_callback(self):
        return
        # self.microscopeSW.trigger_thread(self.current_test_type + '_focus')
     
    def changed_slider(self,slider,str):
        value = slider.value()
        print(str,": ",value)

    def change_camera_callback(self):
        self.camera_index = 0 if self.camera_index == 1 else 1
    # RESIZE EVENTS

    def init_gui_logic(self):
        widgets.testtypebox.addItems(['morphology', 'motility'])
        widgets.testtypebox.activated.connect(self.test_type_callback)
        widgets.startcamera.clicked.connect(self.start_camera)
        widgets.changecamera.clicked.connect(self.change_camera_callback)
        widgets.imgtable.selectionModel().selectionChanged.connect(self.imgselected)
        widgets.saveimage.clicked.connect(self.save_image_callback)
        widgets.savevideo.clicked.connect(self.save_video_callback)
        widgets.autofocus.clicked.connect(self.auto_focus_callback)
        widgets.analyze.clicked.connect(self.analyze_callback)

        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        
        widgets.leftrightslider.valueChanged.connect(self.changed_slider1)
        widgets.updownslider.valueChanged.connect(self.changed_slider2)
        widgets.zoomslider.valueChanged.connect(self.changed_slider3)
        
        widgets.leftrightslider.sliderReleased.connect(self.resetslider1)
        widgets.updownslider.sliderReleased.connect(self.resetslider2)
        widgets.zoomslider.sliderReleased.connect(self.resetslider3)


    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
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


        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')


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
