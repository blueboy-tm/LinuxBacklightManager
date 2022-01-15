from PyQt5 import QtCore, QtGui, QtWidgets
import qdarktheme
import sys
import os
import lbm
from qdarktheme.qtpy.QtWidgets import QColorDialog as DarkColorDialog
import pickle
import threading
import time
import struct
import re
import webbrowser




APP_VERSION = '1.0.0'


def get_file(name):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(getattr(sys, '_MEIPASS'), name)
    return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), name)


def get_evnt_path(device):
    out = os.popen("cat /proc/bus/input/devices | awk '/"+device+"/{for(a=0;a>=0;a++){getline;{if(/kbd/==1){ print ;exit 0;}}}}'").read()
    out = re.findall(r"event\d*", out)
    if out:
        return '/dev/input/'+out[0]


def load_config():
    global config
    datfile = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'setup.dat')
    if not os.path.isfile(datfile):
        data = {
            'theme': 'light',
            'left': 'ffffff',
            'center': 'ffffff',
            'extra': 'ffffff',
            'right': 'ffffff',
            'timer': 30,
            'key_event_driver': get_evnt_path("keyboard"),
            'tux_event_driver': get_evnt_path("TUXEDO"),
            'brightness': 255,
            'state': True
        }
        pickle.dump(data, open(datfile, 'wb'))
    config = pickle.load(open(datfile, 'rb'))

def save_config():
    datfile = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'setup.dat')
    pickle.dump(config, open(datfile, 'wb'))




def timer_turn_off():
    if '0' in lbm.get_value('state'):
        return
    if effect_is_active:
        return
    global timer_is_off
    for i in range(ui.colorLevelSlider.value(), 0, -2):
        if timer_is_off:
            os.system(f"echo {i} >  /sys/devices/platform/tuxedo_keyboard/brightness")
    if timer_is_off:
        os.system(f"echo 0 > /sys/devices/platform/tuxedo_keyboard/state")



def timer_before_off():
    global timer_is_off
    timer_is_off = True
    timer_turn_off()


def timer_turn_on():
    global timer_is_off
    if not timer_is_off:
        os.system(f"echo {ui.colorLevelSlider.value()} >  /sys/devices/platform/tuxedo_keyboard/brightness")
        os.system(f"echo 1 > /sys/devices/platform/tuxedo_keyboard/state")

def timer_key_event_manager():
    global timer_is_off
    global timer_object
    f = open(config.get("key_event_driver"), "rb")
    if config.get('state'):
        timer_turn_on()
    while config.get("timer"):
        if not config.get('state'):
            break
        if effect_is_active:
            break
        if timer_is_off:
            timer_is_off = False
            timer_turn_on()
        try:
            timer_object.cancel()
        except NameError:
            pass
        timer_object = threading.Timer(config.get("timer"), timer_before_off)
        timer_object.start()
        f.read(24)
    timer_is_off = False

def run_timer():
    global timer_is_off
    if config.get('timer') != 0:
        threading.Thread(target=timer_key_event_manager, args=()).start()


def boot_effect():
    colors = {'ff0000', '00ff00', '0000ff', 'ffff00', 'ff00ff', '00ffff', 'ffffff'}
    colors.add(config["left"])
    colors.add(config["center"])
    colors.add(config["extra"])
    colors.add(config["light"])
    color_index = 0
    while effect_is_active:
        for i in range(255, 0, -2):
            if not effect_is_active:
                break
            lbm.brightness(i)
            time.sleep(0.02)
        if not effect_is_active:
            break
        if color_index == len(colors):
            color_index = 0
        lbm.set_color('*', '#'+colors[color_index])
        color_index += 1
        for i in range(1, 256, 2):
            if not effect_is_active:
                break
            lbm.brightness(i)
            time.sleep(0.02)

def disco_effect():
    colors = {'ff0000', '00ff00', '0000ff', 'ffff00', 'ff00ff', '00ffff', 'ffffff'}
    colors.add(config["left"])
    colors.add(config["center"])
    colors.add(config["extra"])
    colors.add(config["light"])
    color_index = 0
    while effect_is_active:
        if color_index == len(colors):
            color_index = 0
        lbm.set_color('*', '#'+colors[color_index])
        color_index += 1
        time.sleep(0.5)

def key_shortcutes():
    f = open(config.get('tux_event_driver'), 'rb')
    while True:
        data = struct.unpack('4IHHI', f.read(24))
        if (data[-2] == 230) and (data[-1] == 0):
            if not effect_is_active:
                ui.colorLevelSlider.setValue(config.get('brightness')+25)
            lbm.brightness(config.get('brightness'))
        
        elif (data[-2] == 229) and (data[-1] == 0):
            if (not config.get('brightness') <= 35) and (not effect_is_active):
                ui.colorLevelSlider.setValue(config.get('brightness')-25)
            lbm.brightness(config.get('brightness'))
        
        elif (data[-2] == 228) and (data[-1] == 0):
            ui.state(not config.get('state'))
        
        elif (data[-2] == 542) and (data[-1] == 0):
            lbm.set_color('left', '#'+config['left'])
            lbm.set_color('center', '#'+config['center'])
            lbm.set_color('right', '#'+config['right'])
            lbm.set_color('extra', '#'+config['extra'])
            if MainWindow.isHidden:
                MainWindow.show()
            else:
                MainWindow.hide()




class MyMainWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        MainWindow.hide()
        event.ignore()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(QtCore.QSize(1120, 700))
        MainWindow.setWindowIcon(QtGui.QIcon(get_file('icon/icon.png')))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1100, 658))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox3 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox3.setObjectName("groupBox3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.colorLevelSlider = QtWidgets.QSlider(self.groupBox3)
        self.colorLevelSlider.setOrientation(QtCore.Qt.Horizontal)
        self.colorLevelSlider.setObjectName("colorLevelSlider")
        self.gridLayout_4.addWidget(self.colorLevelSlider, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox3, 2, 1, 1, 1)
        self.groupBox2 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox2.setObjectName("groupBox2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.changeColorLeftButton = QtWidgets.QPushButton(self.groupBox2)
        self.changeColorLeftButton.setObjectName("changeColorLeftButton")
        self.gridLayout_3.addWidget(self.changeColorLeftButton, 0, 1, 1, 1)
        self.changeColorAllButton = QtWidgets.QPushButton(self.groupBox2)
        self.changeColorAllButton.setObjectName("changeColorAllButton")
        self.gridLayout_3.addWidget(self.changeColorAllButton, 0, 0, 1, 1)
        self.changeColorExtraButton = QtWidgets.QPushButton(self.groupBox2)
        self.changeColorExtraButton.setObjectName("changeColorExtraButton")
        self.gridLayout_3.addWidget(self.changeColorExtraButton, 0, 3, 1, 1)
        self.changeColorCenterButton = QtWidgets.QPushButton(self.groupBox2)
        self.changeColorCenterButton.setObjectName("changeColorCenterButton")
        self.gridLayout_3.addWidget(self.changeColorCenterButton, 0, 2, 1, 1)
        self.changeColorRightButton = QtWidgets.QPushButton(self.groupBox2)
        self.changeColorRightButton.setObjectName("changeColorRightButton")
        self.gridLayout_3.addWidget(self.changeColorRightButton, 0, 4, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox2, 2, 0, 1, 1)
        self.gridLayout1 = QtWidgets.QGridLayout()
        self.gridLayout1.setObjectName("gridLayout1")
        self.updateButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.updateButton.setObjectName("updateButton")
        self.gridLayout1.addWidget(self.updateButton, 0, 1, 1, 1)
        self.rescanButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.rescanButton.setObjectName("rescanButton")
        self.gridLayout1.addWidget(self.rescanButton, 0, 2, 1, 1)
        self.uninstallButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.uninstallButton.setObjectName("uninstallButton")
        self.gridLayout1.addWidget(self.uninstallButton, 0, 0, 1, 1)
        self.infoButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.infoButton.setObjectName("infoButton")
        self.gridLayout1.addWidget(self.infoButton, 0, 3, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout1, 5, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 6, 0, 1, 2)
        self.groupBox4 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox4.setObjectName("groupBox4")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox4)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.discoModeButton = QtWidgets.QPushButton(self.groupBox4)
        self.discoModeButton.setObjectName("discoModeButton")
        self.gridLayout_6.addWidget(self.discoModeButton, 0, 0, 1, 1)
        self.bootEffectModeButton = QtWidgets.QPushButton(self.groupBox4)
        self.bootEffectModeButton.setObjectName("bootEffectModeButton")
        self.gridLayout_6.addWidget(self.bootEffectModeButton, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox4, 3, 0, 1, 2)
        self.gridLayout2 = QtWidgets.QGridLayout()
        self.gridLayout2.setObjectName("gridLayout2")
        self.styleChangeButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.styleChangeButton.setObjectName("styleChangeButton")
        self.gridLayout2.addWidget(self.styleChangeButton, 0, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout2.addItem(spacerItem1, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout2, 7, 0, 1, 1)
        self.groupBox1 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox1.setObjectName("groupBox1")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox1)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.turnOnButton = QtWidgets.QPushButton(self.groupBox1)
        self.turnOnButton.setObjectName("turnOnButton")
        self.gridLayout_5.addWidget(self.turnOnButton, 0, 0, 1, 1)
        self.turnOffButton = QtWidgets.QPushButton(self.groupBox1)
        self.turnOffButton.setObjectName("turnOffButton")
        self.gridLayout_5.addWidget(self.turnOffButton, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox1, 0, 0, 1, 2)
        self.groupBox5 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox5.setObjectName("groupBox5")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox5)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label1 = QtWidgets.QLabel(self.groupBox5)
        self.label1.setObjectName("label1")
        self.gridLayout_7.addWidget(self.label1, 1, 0, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.groupBox5)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout_7.addWidget(self.spinBox, 1, 1, 1, 1)
        self.saveTimerButton = QtWidgets.QPushButton(self.groupBox5)
        self.saveTimerButton.setObjectName("saveTimerButton")
        self.gridLayout_7.addWidget(self.saveTimerButton, 1, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox5)
        self.label.setObjectName("label")
        self.gridLayout_7.addWidget(self.label, 0, 0, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem2, 1, 3, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox5, 4, 0, 1, 2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", f"Linux Backlight Manager {APP_VERSION}"))
        self.groupBox3.setTitle(_translate("MainWindow", "Light Level"))
        self.groupBox2.setTitle(_translate("MainWindow", "Backlight Color"))
        self.changeColorLeftButton.setText(_translate("MainWindow", "Left Keys"))
        self.changeColorAllButton.setText(_translate("MainWindow", "All Keys"))
        self.changeColorExtraButton.setText(_translate("MainWindow", "Extra Keys"))
        self.changeColorCenterButton.setText(_translate("MainWindow", "Center Keys"))
        self.changeColorRightButton.setText(_translate("MainWindow", "Right Keys"))
        self.updateButton.setText(_translate("MainWindow", "Update"))
        self.rescanButton.setText(_translate("MainWindow", "Rescan Device"))
        self.uninstallButton.setText(_translate("MainWindow", "Uninstall"))
        self.infoButton.setText(_translate("MainWindow", "Info"))
        self.groupBox4.setTitle(_translate("MainWindow", "Backlight Mode"))
        self.discoModeButton.setText(_translate("MainWindow", "Disco"))
        self.bootEffectModeButton.setText(_translate("MainWindow", "Boot Effect"))
        self.styleChangeButton.setText(_translate("MainWindow", "Light"))
        self.groupBox1.setTitle(_translate("MainWindow", "Backlight State"))
        self.turnOnButton.setText(_translate("MainWindow", "Turn On"))
        self.turnOffButton.setText(_translate("MainWindow", "Turn Off"))
        self.groupBox5.setTitle(_translate("MainWindow", "Timer"))
        self.label1.setText(_translate("MainWindow", "Seconds:"))
        self.saveTimerButton.setText(_translate("MainWindow", "Save"))
        self.label.setText(_translate("MainWindow", "Turn off backlight if not using keyboard"))
        self.uninstallButton.setStyleSheet("color:#cc0000;")
        self.styleChangeButton.clicked.connect(self.changetheme)
        self.turnOnButton.clicked.connect(lambda: self.state(True))
        self.turnOffButton.clicked.connect(lambda: self.state(False))
        self.colorLevelSlider.setRange(10, 255)
        self.colorLevelSlider.setPageStep(5)
        self.colorLevelSlider.valueChanged.connect(self.brightness)
        self.colorLevelSlider.setValue(config.get('brightness'))
        self.changeColorAllButton.clicked.connect(lambda: self.setcolor('*'))
        self.changeColorLeftButton.clicked.connect(lambda: self.setcolor('left'))
        self.changeColorCenterButton.clicked.connect(lambda: self.setcolor('center'))
        self.changeColorExtraButton.clicked.connect(lambda: self.setcolor('extra'))
        self.changeColorRightButton.clicked.connect(lambda: self.setcolor('right'))
        self.bootEffectModeButton.clicked.connect(lambda: self.starteffect('boot'))
        self.discoModeButton.clicked.connect(lambda: self.starteffect('disco'))
        self.spinBox.setMaximum(30*60)
        self.spinBox.setValue(config['timer'])
        self.saveTimerButton.clicked.connect(self.savetimer)
        self.infoButton.clicked.connect(lambda: webbrowser.open("https://github.com/blueboy-tm/LinuxBacklightManager#info"))
        self.updateButton.clicked.connect(lambda: webbrowser.open("https://github.com/blueboy-tm/LinuxBacklightManager#update"))
        self.rescanButton.clicked.connect(self.rescan)
        self.uninstallButton.clicked.connect(self.uninstall)

    
    def changetheme(self):
        if self.styleChangeButton.text() == 'Light':
            app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
            self.styleChangeButton.setText('Dark')
            config['theme'] = 'dark'
            save_config()
        else:
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))
            self.styleChangeButton.setText('Light')
            config['theme'] = 'light'
            save_config()
    
    def setcolor(self, key):
        color = DarkColorDialog.getColor(parent=MainWindow, options=DarkColorDialog.ColorDialogOption.DontUseNativeDialog).name()
        if color != '#000000':
            lbm.set_color(key, color)
            left = lbm.get_value('color_left').strip()
            center = lbm.get_value('color_center').strip()
            extra = lbm.get_value('color_extra').strip() 
            right = lbm.get_value('color_right').strip()
            config['left'] = left
            config['center'] = center
            config['extra'] = extra
            config['right'] = right
            save_config()
    
    def savetimer(self):
        old = config.get('timer')
        new = self.spinBox.value()
        if new == old:
            return
        elif new == 0:
            config['timer'] = 0
            save_config()
            lbm.state(True)
            lbm.brightness(255)
            try:
                timer_object.cancel()
            except NameError:
                pass
        elif (old == 0) and (new != 0):
            config['timer'] = new
            save_config()
            run_timer()
        else:
            config['timer'] = new
            save_config()
    
    def brightness(self, value: int):
        if (not timer_is_off) and (config.get("state")) and (not effect_is_active):
            lbm.brightness(value)
        config['brightness'] = value
        save_config()
        
    

    def state(self, turn: bool):
        if turn:
            config['state'] = True
            save_config()
            lbm.brightness(config.get('brightness'))
            lbm.state(True)
            run_timer()
        else:
            config['state'] = False
            save_config()
            lbm.state(False)
    
    def starteffect(self, em: str):
        global effect_is_active
        if not effect_is_active:
            effect_is_active = True
            try:
                timer_object.cancel()
            except NameError:
                pass
            lbm.brightness(255)
            lbm.state(True)
            if em == 'boot':
                threading.Thread(target=boot_effect, args=()).start()
            elif em == 'disco':
                threading.Thread(target=disco_effect, args=()).start()
        else:
            effect_is_active = False
            lbm.set_color('left', '#'+config['left'])
            lbm.set_color('center', '#'+config['center'])
            lbm.set_color('right', '#'+config['right'])
            lbm.set_color('extra', '#'+config['extra'])
            lbm.brightness(config.get('brightness'))
            lbm.state(config.get('state'))
            run_timer()
    
    def rescan(self):
        quiz = QtWidgets.QMessageBox()
        quiz.setText("The system must be restarted for scanning. You sure?")
        quiz.setWindowTitle("Restart System")
        quiz.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        quiz = quiz.exec()

        if quiz == QtWidgets.QMessageBox.Yes:
            os.system('reboot')
    

    def uninstall(self):
        quiz = QtWidgets.QMessageBox()
        quiz.setText("You sure?")
        quiz.setWindowTitle("Restart System")
        quiz.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        quiz = quiz.exec()

        if quiz == QtWidgets.QMessageBox.Yes:
            src =  os.popen("ls /usr/src/ | grep tuxedo").read()
            version = src.replace("tuxedo-keyboard-", "")
            src = src.replace("-"+version, "")
            cmd = f"sleep 2;dkms remove -m {src} -v {version} --all;rm -rf /usr/src/{src}-{version};rm /etc/modprobe.d/tuxedo_keyboard.conf;"\
                "systemctl disable lbm.service;rm /etc/systemd/system/lbm.service;rm /etc/xdg/autostart/lbm.desktop;rm -rf /opt/lbm-"+APP_VERSION+";"\
                    "sed '/tuxedo_keyboard/d' /etc/modules > /etc/modules;reboot"

            
            fileaddr = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "un000.sh")
            file = open(fileaddr, "a")
            file.write(cmd.replace(";", '\n'))
            file.close()
            os.popen(f"pkexec bash {fileaddr}")
            os.kill(os.getpid())



if __name__ == "__main__":
    load_config()
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'boot':
            config['key_event_driver'] = get_evnt_path("keyboard")
            config['tux_event_driver'] = get_evnt_path("TUXEDO")
            save_config()
            os.system('chmod 777 /sys/devices/platform/tuxedo_keyboard/brightness')
            os.system('chmod 777 /sys/devices/platform/tuxedo_keyboard/color_*')
            os.system('chmod 777 /sys/devices/platform/tuxedo_keyboard/extra')
            os.system('chmod 777 /sys/devices/platform/tuxedo_keyboard/mode')
            os.system('chmod 777 /sys/devices/platform/tuxedo_keyboard/state')
            os.system('chmod 777 /sys/devices/platform/tuxedo_keyboard/uevent')
            os.system('chmod 777 /sys/devices/platform/tuxedo_keyboard/driver_override')
            os.system('chmod 777 /sys/devices/platform/tuxedo_keyboard/modalias')
            os.system('chmod 777 {}'.format(config.get("key_event_driver")))
            os.system('chmod 777 {}'.format(config.get("tux_event_driver")))
            os.system('chmod 777 {}'.format(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'setup.dat')))
            lbm.set_color('left', '#'+config['left'])
            lbm.set_color('center', '#'+config['center'])
            lbm.set_color('right', '#'+config['right'])
            lbm.set_color('extra', '#'+config['extra'])
            lbm.brightness(config.get('brightness'))
            lbm.state(config.get('state'))
            os.system(f'echo "options tuxedo_keyboard mode=0 color_left=0x{config["left"]} color_center=0x{config["center"]} color_right=0x{config["right"]}" > /etc/modprobe.d/tuxedo_keyboard.conf')
            sys.exit()

    timer_is_off = False
    effect_is_active = False
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("light"))
    MainWindow = MyMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    if config.get('theme') != 'light':
        ui.changetheme()


    run_timer()
    threading.Thread(target=key_shortcutes, args=()).start()


    tray = QtWidgets.QSystemTrayIcon()
    tray.setIcon(QtGui.QIcon(get_file('icon/icon.png')))
    tray.setVisible(True)

    menu = QtWidgets.QMenu()
    open_application = QtWidgets.QAction("Open Application")
    quit = QtWidgets.QAction("Quit")

    open_application.triggered.connect(MainWindow.show)
    quit.triggered.connect(app.quit)

    menu.addAction(open_application)
    # menu.addAction(quit)
    tray.setContextMenu(menu)

    sys.exit(app.exec_())



