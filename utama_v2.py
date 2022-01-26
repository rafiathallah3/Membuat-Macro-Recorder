import sys, time, win32gui, win32con, enum
from PyQt5 import QtCore, QtGui, QtWidgets
from pynput.keyboard import Listener as KeyboardListener, Key, KeyCode
from pynput.mouse import Listener as MouseListener, Button

"""
    [17/01/2022 15:17] Ini akan diperbarui soalnya saya sudah menemukan bagaimana cara mendeteksi keybind
    [17/01/2022 18:59] Aku gk tau kenapa tidak bisa download `pip install pyqt5-tools` jadi harus di pause dulu
"""

class NamaAksiRecorder(enum.Enum):
    KLIK_KIRI_TAHAN = "Klik Kiri Tahan"
    KLIK_KIRI_LEPAS = "Klik Kiri Lepas"
    KLIK_KANAN_TAHAN = "Klik Kanan Tahan"
    KLIK_KANAN_LEPAS = "Klik Kanan Lepas"
    SCROLL_ATAS = "Scroll Atas"
    SCROLL_BAWAH = "Scroll Bawah"
    GERAKAN_MOUSE = "Gerakan Mouse"
    KETIK_TAHAN = "Ketik Tahan"
    KETIK_LEPAS = "Ketik Lepas"

class KeySamaMouse_Monitor(QtCore.QObject):
    tekanKey = QtCore.pyqtSignal(object, bool) #Kunci, Tekan
    KlikMouse = QtCore.pyqtSignal(dict) #{Kondisi: str, Pos: [x,y], Tombol: Button, Klik: bool, scroll: [dx,dy], gerakana?: pos} 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.keyboardListener = KeyboardListener(on_press=self.on_press, on_release=self.on_release)
        self.mouseListener = MouseListener(on_click=self.on_klik, on_scroll=self.on_scroll, on_move=self.on_move)

    def on_press(self, kunci):
        self.tekanKey.emit(kunci, True)

    def on_release(self, kunci):
        self.tekanKey.emit(kunci, False)

    def on_klik(self, x ,y, tombol, tekan):
        self.KlikMouse.emit({
            "Kondisi": "Klik",
            "Pos": [x,y],
            "Tombol": tombol,
            "Tekan": tekan
        })

    def on_scroll(self, x, y, dx, dy):
        self.KlikMouse.emit({
            "Kondisi": "Scroll",
            "Pos": [x,y],
            "Scroll": [dx,dy]
        })

    def on_move(self, x, y):
        self.KlikMouse.emit({
            "Kondisi": "Gerakan",
            "Pos": [x,y]
        })

    def startMonitor(self):
        self.keyboardListener.start()
        self.mouseListener.start()

    def stopMonitor(self):
        self.keyboardListener.stop()
        self.mouseListener.stop()

class Ui_WindowUtama(object):
    def __init__(self, MainWindow: QtWidgets.QMainWindow) -> None:
        self.MainWindow = MainWindow

        self.Keybind = {
            "Record": {
                "Nama": "F6",
                "KeyValue": Key.f6
            },
            "Mulai": {
                "Nama": "F7",
                "KeyValue": Key.f7
            },
            "Pause": {
                "Nama": "F8",
                "KeyValue": Key.f8
            }
        }

        self.HasilRecorder = {
            "BolehRecordMouseGerakan": False,
            "MenggabaikanShortcut": False,
            "TopSaatRecord": False,
            "TopMauUnpause": False,
            "SelaluDiulang": False, 
            "TidakDiulang": True,
            "TopSaatSelesaiRecorder": True,
            "Aksi": []
        }

        self.Pause = False
        self._MulaiRecorder = False
        self.WaktuMulaiRecorder = 0
        self.NamaAplikasi = "Macro Recorder - untitled"
        self.Aplikasi = self.path = None

        self.Monitor = KeySamaMouse_Monitor()
        self.Monitor.tekanKey.connect(self.TekanKeyFunc)
        self.Monitor.KlikMouse.connect(self.KlikMosFunc)
        self.Monitor.startMonitor()

    @property
    def MulaiRecorder(self):
        return self._MulaiRecorder

    @MulaiRecorder.setter
    def MulaiRecorder(self, val):
        self.TombolRecord.setDisabled(val)
        self.TombolMulai.setDisabled(val)
        self.TombolStop.setDisabled(not val)
        self.TombolPause.setDisabled(not val)

        if val:
            self.HasilRecorder["Aksi"] = []
            self.WaktuMulaiRecorder = time.perf_counter()

            if not self.HasilRecorder["TopSaatRecord"]:
                win32gui.ShowWindow(self.Aplikasi, win32con.SW_MINIMIZE)
        else:
            self.Pause = val
            self.GantiTableUiDariHasilRecorder()

        self._MulaiRecorder = val

    def KlikTombolRecord(self):
        self.MulaiRecorder = True

    def KlikTombolMulai(self):
        ...

    def KlikTombolStop(self):
        self.MulaiRecorder = False

    def TekanKeyFunc(self, key, tekan):
        # if key == self.Keybind["KeyValue"] and tekan:
        #     self.MulaiRecorder = not self.MulaiRecorder

        if self.MulaiRecorder:
            self.TambahinAksi(NamaAksiRecorder.KETIK_TAHAN.value if tekan else NamaAksiRecorder.KETIK_LEPAS.value, key)

    def KlikMosFunc(self, Hasil):
        if self.MulaiRecorder:
            if Hasil["Kondisi"] == "Gerakan" and self.HasilRecorder["BolehRecordMouseGerakan"]:
                self.TambahinAksi(NamaAksiRecorder.GERAKAN_MOUSE.value, Hasil["Pos"])

            if Hasil["Kondisi"] == "Klik":
                if Hasil["Tekan"]: self.TambahinAksi(NamaAksiRecorder.KLIK_KIRI_TAHAN.value if Hasil["Tombol"] == Button.left else NamaAksiRecorder.KLIK_KANAN_TAHAN.value, Hasil["Pos"])
                else: self.TambahinAksi(NamaAksiRecorder.KLIK_KIRI_LEPAS.value if Hasil["Tombol"] == Button.left else NamaAksiRecorder.KLIK_KANAN_LEPAS.value, Hasil["Pos"])

            if Hasil["Kondisi"] == "Scroll":
                self.TambahinAksi(NamaAksiRecorder.SCROLL_ATAS.value if Hasil["Scroll"][1] > 0 else NamaAksiRecorder.SCROLL_BAWAH.value, Hasil["Scroll"])

    def TambahinAksi(self, nama, nilai):
        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) != self.NamaAplikasi:
            self.HasilRecorder["Aksi"].append({
                "Aksi": nama,
                "Nilai": nilai,
                "Waktu": "{:.2f}".format(time.perf_counter() - self.WaktuMulaiRecorder)
            })

    def GantiTableUiDariHasilRecorder(self):
        self.tableWidget.setRowCount(len(self.HasilRecorder["Aksi"]))
        for i,v in enumerate(self.HasilRecorder["Aksi"]):
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(v["Aksi"]))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(v["Nilai"])))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(v["Waktu"]+" detik"))

    def winEnumHandler(self, hwnd, ctx):
        #sumber: https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == self.NamaAplikasi:
            self.Aplikasi = hwnd

    def setupUi(self):
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(497, 430)
        self.MainWindow.setMouseTracking(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui\\../icon/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.MainWindow.setWindowIcon(icon)
        self.MainWindow.setToolTipDuration(-1)
        self.MainWindow.setAutoFillBackground(False)
        self.MainWindow.setStyleSheet("")
        self.MainWindow.setFixedSize(self.MainWindow.size())

        self.centralwidget = QtWidgets.QWidget(self.MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(497, 0))
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("ui\\../icon/record.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.TombolRecord = QtWidgets.QPushButton(self.centralwidget)
        self.TombolRecord.setEnabled(True)
        self.TombolRecord.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TombolRecord.setMouseTracking(False)
        self.TombolRecord.setStyleSheet("")
        self.TombolRecord.setText("")
        self.TombolRecord.setIcon(icon1)
        self.TombolRecord.setIconSize(QtCore.QSize(16, 16))
        self.TombolRecord.setCheckable(False)
        self.TombolRecord.setObjectName("TombolRecord")
        
        self.horizontalLayout.addWidget(self.TombolRecord)
        
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("ui\\../icon/play-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.TombolMulai = QtWidgets.QPushButton(self.centralwidget)
        self.TombolMulai.setEnabled(True)
        self.TombolMulai.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TombolMulai.setMouseTracking(False)
        self.TombolMulai.setStyleSheet("")
        self.TombolMulai.setText("")
        self.TombolMulai.setIcon(icon2)
        self.TombolMulai.setIconSize(QtCore.QSize(16, 16))
        self.TombolMulai.setCheckable(False)
        self.TombolMulai.setObjectName("TombolMulai")
        
        self.horizontalLayout.addWidget(self.TombolMulai)
        
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("ui\\../icon/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.TombolPause = QtWidgets.QPushButton(self.centralwidget)
        self.TombolPause.setEnabled(True)
        self.TombolPause.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TombolPause.setMouseTracking(False)
        self.TombolPause.setStyleSheet("")
        self.TombolPause.setText("")
        self.TombolPause.setIcon(icon3)
        self.TombolPause.setCheckable(False)
        self.TombolPause.setObjectName("TombolPause")
        
        self.horizontalLayout.addWidget(self.TombolPause)
        
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("ui\\../icon/stop-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.TombolStop = QtWidgets.QPushButton(self.centralwidget)
        self.TombolStop.setEnabled(True)
        self.TombolStop.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TombolStop.setMouseTracking(False)
        self.TombolStop.setStyleSheet("")
        self.TombolStop.setText("")
        self.TombolStop.setIcon(icon4)
        self.TombolStop.setCheckable(False)
        self.TombolStop.setObjectName("TombolStop")
        
        self.horizontalLayout.addWidget(self.TombolStop)
        
        self.TombolSetting = QtWidgets.QPushButton(self.centralwidget)
        self.TombolSetting.setEnabled(True)
        self.TombolSetting.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TombolSetting.setMouseTracking(False)
        self.TombolSetting.setText("")
        self.TombolSetting.setIcon(icon)
        self.TombolSetting.setCheckable(False)
        self.TombolSetting.setObjectName("TombolSetting")
        
        self.horizontalLayout.addWidget(self.TombolSetting)
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 477, 308))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        self.tableWidget = QtWidgets.QTableWidget(self.scrollAreaWidgetContents)
        self.tableWidget.setStyleSheet("")
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnWidth(0, 175)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 130)
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        
        self.horizontalLayout_2.addWidget(self.tableWidget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        
        self.TombolHapus = QtWidgets.QPushButton(self.centralwidget)
        self.TombolHapus.setEnabled(False)
        self.TombolHapus.setObjectName("TombolHapus")
        
        self.verticalLayout.addWidget(self.TombolHapus)
        self.MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(self.MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 497, 21))
        self.menubar.setObjectName("menubar")
        
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtWidgets.QStatusBar(self.MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.MainWindow.setStatusBar(self.statusbar)
        
        self.actionSave = QtWidgets.QAction(self.MainWindow)
        self.actionSave.setObjectName("actionSave")
        
        self.actionOpen = QtWidgets.QAction(self.MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        
        self.actionExit = QtWidgets.QAction(self.MainWindow)
        self.actionExit.setObjectName("actionExit")
        
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "Macro Recorder"))
        
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Aksi"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Nilai"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Waktu"))
        
        self.TombolHapus.setToolTip(_translate("MainWindow", "Menghapus aksi dari table"))
        self.TombolHapus.setText(_translate("MainWindow", "Hapus"))
        
        self.TombolMulai.setDisabled(True)
        self.TombolHapus.setDisabled(True)
        self.TombolStop.setDisabled(True)
        self.TombolPause.setDisabled(True)

        self.menuFile.setTitle(_translate("MainWindow", "File"))

        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))

        self.TombolRecord.clicked.connect(self.KlikTombolRecord)
        self.TombolMulai.clicked.connect(self.KlikTombolMulai)
        self.TombolStop.clicked.connect(self.KlikTombolStop)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_WindowUtama(MainWindow)
    ui.setupUi()
    MainWindow.show()
    win32gui.EnumWindows(ui.winEnumHandler, None)
    sys.exit(app.exec_())
