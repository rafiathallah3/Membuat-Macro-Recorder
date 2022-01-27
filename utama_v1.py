"""
#Entah kenapa waktu file 'utama.py' terhapus terus.
#UPDATE: Windows mengangap file ini sebuah virus HackTool:Python/Keylogger.B
#Aku gk tau sejak kapan script ini bisa "crack" software lainnya
from PyQt5 import QtCore, QtGui, QtWidgets
from pynput.mouse import Button, Controller as mouseController, Listener as MouseListener
from pynput.keyboard import Controller as keyboardController, Listener as KeyboardListener, Key, KeyCode

import threading, sys, time, enum, win32gui, win32con, json, os

""
    
    [21/12/2021 22:21]  reminder: membuat semua nama aksi recorder, Supaya bisa mengirim 'HasilRecorder' dan proses selanjutnya
    [25/12/2021 15:16]  Fitur yang susah dibuat / ada bug dalam pembuatan jadi harus dicancel: 
                            1. membuat keybind untuk pause, mulai, stop recorder
    [27/12/2021 21:21]  Yang harus dibikin:
                            1. mengganti HasilRecorder menjadi data table ui
                            2. Membuat selalu diulang saat memulai
""

class NamaAksiRecorder (enum.Enum):
    KLIK_KIRI_TAHAN = "Klik Kiri Tahan"
    KLIK_KIRI_LEPAS = "Klik Kiri Lepas"
    KLIK_KANAN_TAHAN = "Klik Kanan Tahan"
    KLIK_KANAN_LEPAS = "Klik Kanan Lepas"
    SCROLL_ATAS = "Scroll Atas"
    SCROLL_BAWAH = "Scroll Bawah"
    KETIK_TAHAN = "Ketik Tahan"
    KETIK_LEPAS = "Ketik Lepas"

class WindowUtama():
    def __init__(self, MainWindow: QtWidgets.QMainWindow):
        self.MainWindow = MainWindow

        self.Rekam = self.Mulai = self._Pause = False
        self.HasilRecorder = {
            "MenggabaikanShortcut": False,
            "TopSaatRecord": False,
            "TopMauUnpause": False,
            "SelaluDiulang": False, 
            "TidakDiulang": True,
            "TopSaatSelesaiRecorder": True,
            "Aksi": []
        }
        self.WaktuMulaiRecorder = 0

        self.NamaAplikasi = "Macro Recorder - untitled"
        self.Aplikasi = self.path = None

        self.MouseController = mouseController()
        self.KeyboardController = keyboardController()

        self.KeyDariCTRL = {
            '\x01': 'a', '\x02': 'b', '\x03': 'c',
            '\x04': 'd', '\x05': 'e', '\x06': 'f',
            '\x07': 'g', '\x08': 'h', '\t': 'i',
            '\n': 'j', '\x0b': 'k', '\x0c': 'l',
            '\r': 'm', '\x0e': 'n', '\x0f': 'o',
            '\x10': 'p', '\x11': 'q', '\x12': 'r',
            '\x13': 's', '\x14': 't', '\x15': 'u',
            '\x16': 'v', '\x17': 'w', '\x18': 'x',
            '\x19': 'y', '\x1a': 'z'
        }
    
    def MendapatkanUserInput(self):
        def TambahinAksi(nama, nilai):
            if win32gui.GetWindowText(win32gui.GetForegroundWindow()) != self.NamaAplikasi:
                self.HasilRecorder["Aksi"].append({
                    "Aksi": nama,
                    "Nilai": nilai,
                    "Waktu": "{:.2f}".format(time.perf_counter() - self.WaktuMulaiRecorder)
                })

        # Masalah dari on_press sama on_release adalah "key", soalnya "key" typenya bukan string melainkan classEnum (pynput.keyboard.KeyCode) 
        # Jadi yang harus dilakukan adalah, mendapatkan "key" value, contohnya key = ctrl_l (Control left) kalau di valuekan menjadi "<162>"
        # Tapi, ada masalah juga, key.value itu menghasilkan type classEnum (pynput.keyboard.KeyCode), untungnya bisa distring jadi kita convert "<162>" ke KeyCode, menggunakan class Keycode() dari pynput keyboard
        def MendapatkanKeyCode(key):
            KeyValue = " "
            if hasattr(key, 'value'):
                #Kalau ini false, kemungkinan key.value itu spasi |" "|
                if any(i.isdigit() for i in str(key.value)):
                    KeyValue = int(''.join(filter(str.isdigit, str(key.value))))
            else:
                KeyValue = self.KeyDariCTRL.setdefault(key.char,key.char)

            return KeyValue
            
        def on_press(key):
            if not self.Rekam: return False
            if self.Pause or ((key == Key.ctrl_l or key == Key.ctrl_r) and self.HasilRecorder["MenggabaikanShortcut"]): return True

            TambahinAksi(NamaAksiRecorder.KETIK_TAHAN.value, MendapatkanKeyCode(key))

        def on_release(key):
            if not self.Rekam: return False
            if self.Pause or ((key == Key.ctrl_l or key == Key.ctrl_r) and self.HasilRecorder["MenggabaikanShortcut"]): return True

            TambahinAksi(NamaAksiRecorder.KETIK_LEPAS.value, MendapatkanKeyCode(key))

        def on_click(x, y, button, pressed):
            if not self.Rekam: return False
            if self.Pause: return True
            
            if pressed: TambahinAksi(NamaAksiRecorder.KLIK_KIRI_TAHAN.value if button == Button.left else NamaAksiRecorder.KLIK_KANAN_TAHAN.value, ",".join(str(v) for v in [x,y]))
            else: TambahinAksi(NamaAksiRecorder.KLIK_KIRI_LEPAS.value if button == Button.left else NamaAksiRecorder.KLIK_KANAN_LEPAS.value, ",".join(str(v) for v in [x,y]))

        def on_scroll(x, y, dx, dy):
            if not self.Rekam: return False
            if self.Pause: return True

            TambahinAksi(NamaAksiRecorder.SCROLL_ATAS.value if dy > 0 else NamaAksiRecorder.SCROLL_BAWAH.value, f"{dx},{dy}")

        keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
        mouse_listener = MouseListener(on_click=on_click, on_scroll=on_scroll)

        keyboard_listener.start()
        mouse_listener.start()
        keyboard_listener.join()
        mouse_listener.join()

    def KlikTombolRecord(self):
        if not self.Rekam:
            print("Mulai record")
            self.Rekam = True
            self.HasilRecorder["Aksi"] = []
            self.WaktuMulaiRecorder = time.perf_counter()
            self.TombolRecord.setEnabled(False)
            self.TombolMulai.setEnabled(False)
            self.TombolStop.setEnabled(True)
            self.TombolPause.setEnabled(True)

            if not self.HasilRecorder["TopSaatRecord"]:
                win32gui.ShowWindow(self.Aplikasi, win32con.SW_MINIMIZE)

            x = threading.Thread(target=self.MendapatkanUserInput)
            x.start()

    def KlikTombolStop(self):
        if self.Rekam:
            print("Stop Recorder")
            self.Rekam = self.Pause = False
                        
            self.TombolRecord.setEnabled(True)
            self.TombolMulai.setEnabled(True)
            self.TombolStop.setEnabled(False)
            self.TombolPause.setEnabled(False)

            self.GantiTableUiDariHasilRecorder()

    def KlikTombolMulai(self):
        if not self.HasilRecorder["Aksi"]:
            self.TombolMulai.setEnabled(True)
            return

        while True:
            print("Mulai")
            self.Mulai = True
            WaktuTombolMulai = time.perf_counter()
            
            win32gui.ShowWindow(self.Aplikasi, win32con.SW_MINIMIZE)
            for i in self.HasilRecorder["Aksi"]:
                WaktuDiTunggu = WaktuTombolMulai + float(i["Waktu"])

                while time.perf_counter() < WaktuDiTunggu:...
                else:
                    aksi = i["Aksi"]

                    if aksi == NamaAksiRecorder.KLIK_KIRI_TAHAN.value or aksi == NamaAksiRecorder.KLIK_KANAN_TAHAN.value:
                        self.MouseController.position = tuple(int(j) for j in i["Nilai"].split(','))
                        self.MouseController.press(Button.left if aksi == NamaAksiRecorder.KLIK_KIRI_TAHAN.value else Button.right)
                        
                    elif aksi == NamaAksiRecorder.KLIK_KIRI_LEPAS.value or aksi == NamaAksiRecorder.KLIK_KANAN_LEPAS.value:
                        self.MouseController.position = tuple(int(j) for j in i["Nilai"].split(','))
                        time.sleep(.01) #Ini di tunggu supaya... apa ya, susa juga dijelasin, coba aja di pake ke notepad terus tahan dan ke text lain terus ada warna background birunya, kalau tidak ada penunggu, jadi background birunya tidak ada
                        self.MouseController.release(Button.left if aksi == NamaAksiRecorder.KLIK_KIRI_LEPAS.value else Button.right)

                    elif aksi == NamaAksiRecorder.SCROLL_ATAS.value or aksi == NamaAksiRecorder.SCROLL_BAWAH.value:
                        self.MouseController.scroll(*tuple(int(j) for j in i["Nilai"].split(',')))
                        
                    elif aksi == NamaAksiRecorder.KETIK_TAHAN.value:
                        self.KeyboardController.press(KeyCode(i["Nilai"]) if isinstance(i["Nilai"], int) else i["Nilai"])
                    elif aksi == NamaAksiRecorder.KETIK_LEPAS.value:
                        self.KeyboardController.release(KeyCode(i["Nilai"]) if isinstance(i["Nilai"], int) else i["Nilai"])

            time.sleep(1)
            print("Selesai")
            self.Mulai = False
            if self.HasilRecorder["TopSaatSelesaiRecorder"] or self.HasilRecorder["TidakDiulang"]:
                win32gui.ShowWindow(self.Aplikasi, win32con.SHOW_OPENWINDOW)
            
            if self.HasilRecorder["TidakDiulang"]: break

    def KlikTombolPause(self):
        # Kita mengganti TombolMulai menjadi TombolUnpuase
        if self.Rekam and not self.Pause:
            print("Pause")
            self.WaktuMulaiPause = time.perf_counter()
            self.Pause = True

    def KlikTombolUnpause(self):
        if self.Pause:
            print("Unpause")
            self.WaktuMulaiRecorder = time.perf_counter() - (self.WaktuMulaiPause - self.WaktuMulaiRecorder)
            self.Pause = False
            # print(f"Waktu pause: {self.WaktuMulaiRecorder=}, time: {time.perf_counter()}, kalau dikuraning: {time.perf_counter() - self.WaktuMulaiRecorder}")

    def MenyimpanSettingDariSettingDialog(self, MenggabaikanShortcut, TopSaatRecord, TopMauUnpause, SelaluDiulang, TidakDiulang, TopSaatSelesaiRecorder):
        self.HasilRecorder["MenggabaikanShortcut"] = MenggabaikanShortcut
        self.HasilRecorder["TopSaatRecord"] = TopSaatRecord
        self.HasilRecorder["TopMauUnpause"] = TopMauUnpause
        self.HasilRecorder["SelaluDiulang"] = SelaluDiulang
        self.HasilRecorder["TidakDiulang"] = TidakDiulang
        self.HasilRecorder["TopSaatSelesaiRecorder"] = TopSaatSelesaiRecorder

    def KlikTombolSetting(self):
        ui = Ui_Dialog(self.MenyimpanSettingDariSettingDialog)
        ui.setupUi()
        
        self.MenggabaikanShortcut, self.TopSaatRecord, self.TopMauUnpause, self.SelaluDiulang, self.TidakDiulang, self.TopSaatSelesaiRecorder = ui.SemuaSetting()
        self.MenggabaikanShortcut.setChecked(self.HasilRecorder["MenggabaikanShortcut"])
        self.TopSaatRecord.setChecked(self.HasilRecorder["TopSaatRecord"])
        self.TopMauUnpause.setChecked(self.HasilRecorder["TopMauUnpause"])
        self.SelaluDiulang.setChecked(self.HasilRecorder["SelaluDiulang"])
        self.TidakDiulang.setChecked(self.HasilRecorder["TidakDiulang"])
        self.TopSaatSelesaiRecorder.setChecked(self.HasilRecorder["TopSaatSelesaiRecorder"])

        ui.show()
        ui.exec_()

    def KlikTombolHapus(self):
        for i in sorted(self.tableWidget.selectionModel().selectedRows()):
            self.tableWidget.removeRow(i.row())
            del self.HasilRecorder["Aksi"][i.row()-1]

    def ShortcutPauseRecorderFunc(self):
        if self.Rekam:
            if not self.Pause: self.KlikTombolPause()
            else: self.KlikTombolUnpause()

    def TabelBarisDipilih(self):
        #sumber: https://www.youtube.com/watch?v=BH19o9GlN20
        self.TombolHapus.setEnabled(bool(self.tableWidget.selectionModel().selectedRows()))

    def dialog_error(self, pesan):
        doi = QtWidgets.QMessageBox(self.MainWindow)
        doi.setText(pesan)
        doi.setIcon(QtWidgets.QMessageBox.Critical)
        doi.show()

    def BukaFileFunc(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self.MainWindow, "Open file", "", "Json files (*.json)")

        if path:
            try:
                with open(path) as f:
                    hasil_json = json.load(f)
                
            except Exception as e:
                self.dialog_error(e)
            else:
                self.path = path
                self.HasilRecorder = hasil_json
                self.GantiTableUiDariHasilRecorder()
                self.TombolMulai.setEnabled(True)

                self.UpdateNamaWindow(f"Macro Recorder - {os.path.basename(self.path) if self.path else 'untitled'}")

    def SaveFunc(self):
        if not self.HasilRecorder["Aksi"]: return

        if not self.path:
            return self.SaveAsFunc()
        self.SaveKePath()

    def SaveAsFunc(self):
        if not self.HasilRecorder["Aksi"]: return

        self.path, _ = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow, "Save file", "", "Json files (*.json)")
        if not self.path: return
 
        self.SaveKePath()

    def SaveKePath(self):
        file_json = json.dumps(self.HasilRecorder, indent=4)

        try:
            with open(self.path, 'w') as f:
                f.write(file_json)
        except Exception as e:
            self.dialog_error(e)
        else:
            self.UpdateNamaWindow(f"Macro Recorder - {os.path.basename(self.path) if self.path else 'untitled'}")

    def winEnumHandler(self, hwnd, ctx):
        #sumber: https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == self.NamaAplikasi:
            self.Aplikasi = hwnd

    def GantiTableUiDariHasilRecorder(self):
        self.tableWidget.setRowCount(len(self.HasilRecorder["Aksi"]))
        for i,v in enumerate(self.HasilRecorder["Aksi"]):
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(v["Aksi"]))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(v["Nilai"]))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(v["Waktu"]+" detik"))
    
    def UpdateNamaWindow(self, nama):
        self.NamaAplikasi = nama
        self.MainWindow.setWindowTitle(nama)

    @property
    def Pause(self):
        return self._Pause

    @Pause.setter
    def Pause(self, PauseValue):
        self.TombolPause.setEnabled(not PauseValue)
        self.TombolMulai.setEnabled(PauseValue)
        self.TombolMulai.setToolTip("Unpause" if PauseValue else "Mulai hasil recorder")
        
        if not PauseValue and self.Rekam and not self.HasilRecorder["TopMauUnpause"]: #Kalau di unpause, aplikasinya akan di minimize
            win32gui.ShowWindow(self.Aplikasi, win32con.SW_MINIMIZE)

        self._Pause = PauseValue

        self.TombolMulai.clicked.disconnect()
        self.TombolMulai.clicked.connect(self.KlikTombolUnpause if PauseValue else self.KlikTombolMulai)

    def setupUi(self):
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(497, 430)
        self.MainWindow.setFixedSize(self.MainWindow.size())
        self.MainWindow.setMouseTracking(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui\\../icon/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.MainWindow.setWindowIcon(icon)
        self.MainWindow.setToolTipDuration(-1)
        self.MainWindow.setAutoFillBackground(False)
        self.MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(self.MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(497, 0))
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.TombolRecord = QtWidgets.QPushButton(self.centralwidget)
        self.TombolRecord.setEnabled(True)
        self.TombolRecord.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TombolRecord.setMouseTracking(False)
        self.TombolRecord.setStyleSheet("")
        self.TombolRecord.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("ui\\../icon/record.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.TombolRecord.setIcon(icon1)
        self.TombolRecord.setIconSize(QtCore.QSize(16, 16))
        self.TombolRecord.setCheckable(False)
        self.TombolRecord.setObjectName("TombolRecord")
        self.TombolRecord.setToolTip("Mulai record")
        self.horizontalLayout.addWidget(self.TombolRecord)
        self.TombolMulai = QtWidgets.QPushButton(self.centralwidget)
        self.TombolMulai.setEnabled(False)
        self.TombolMulai.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TombolMulai.setMouseTracking(False)
        self.TombolMulai.setStyleSheet("")
        self.TombolMulai.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("ui\\../icon/play-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.TombolMulai.setIcon(icon2)
        self.TombolMulai.setIconSize(QtCore.QSize(16, 16))
        self.TombolMulai.setCheckable(False)
        self.TombolMulai.setObjectName("TombolMulai")
        self.TombolMulai.setToolTip("Mulai hasil recorder")
        self.horizontalLayout.addWidget(self.TombolMulai)
        self.TombolPause = QtWidgets.QPushButton(self.centralwidget)
        self.TombolPause.setEnabled(False)
        self.TombolPause.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TombolPause.setMouseTracking(False)
        self.TombolPause.setStyleSheet("")
        self.TombolPause.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("ui\\../icon/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.TombolPause.setIcon(icon3)
        self.TombolPause.setCheckable(False)
        self.TombolPause.setObjectName("TombolPause")
        self.TombolPause.setToolTip("Pause")
        self.horizontalLayout.addWidget(self.TombolPause)
        self.TombolStop = QtWidgets.QPushButton(self.centralwidget)
        self.TombolStop.setEnabled(False)
        self.TombolStop.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TombolStop.setMouseTracking(False)
        self.TombolStop.setStyleSheet("")
        self.TombolStop.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("ui\\../icon/stop-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.TombolStop.setIcon(icon4)
        self.TombolStop.setCheckable(False)
        self.TombolStop.setObjectName("TombolStop")
        self.TombolStop.setToolTip("Stop")
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
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 477, 337))
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
        self.tableWidget.setColumnWidth(2, 125)
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tableWidget.selectionModel().selectionChanged.connect(self.TabelBarisDipilih)
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
        self.actionSave = QtWidgets.QAction(self.MainWindow, shortcut=QtGui.QKeySequence.Save)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtWidgets.QAction(self.MainWindow, shortcut=QtGui.QKeySequence("Ctrl+Shift+S"))
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionOpen = QtWidgets.QAction(self.MainWindow, shortcut=QtGui.QKeySequence.Open)
        self.actionOpen.setObjectName("actionOpen")
        self.actionPauseUnpause = QtWidgets.QAction(self.MainWindow, shortcut=QtGui.QKeySequence("F6"))
        self.actionPauseUnpause.setObjectName("actionPauseUnpause")
        self.actionStop = QtWidgets.QAction(self.MainWindow, shortcut=QtGui.QKeySequence("F7"))
        self.actionStop.setObjectName("actionStop")
        self.actionExit = QtWidgets.QAction(self.MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPauseUnpause)
        self.menuFile.addAction(self.actionStop)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        # MainWindow.setWindowFlags(MainWindow.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        # MainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", self.NamaAplikasi))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Aksi"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Nilai"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Waktu"))
        self.TombolHapus.setToolTip(_translate("MainWindow", "Menghapus aksi dari table"))
        self.TombolHapus.setText(_translate("MainWindow", "Hapus"))

        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSaveAs.setText(_translate("MainWindow", "Save As"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionPauseUnpause.setText(_translate("MainWindow", "Pause/Unpause recorder"))
        self.actionStop.setText(_translate("MainWindow", "Stop recorder"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))

        self.actionSave.triggered.connect(self.SaveFunc)
        self.actionSaveAs.triggered.connect(self.SaveAsFunc)
        self.actionOpen.triggered.connect(self.BukaFileFunc)
        self.actionPauseUnpause.triggered.connect(self.ShortcutPauseRecorderFunc)
        self.actionStop.triggered.connect(self.KlikTombolStop)
        self.actionExit.triggered.connect(lambda: self.MainWindow.close())

        self.TombolRecord.clicked.connect(self.KlikTombolRecord)
        self.TombolMulai.clicked.connect(self.KlikTombolMulai)
        self.TombolPause.clicked.connect(self.KlikTombolPause)
        self.TombolStop.clicked.connect(self.KlikTombolStop)
        self.TombolHapus.clicked.connect(self.KlikTombolHapus)
        self.TombolSetting.clicked.connect(self.KlikTombolSetting)

class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self, closeSettingFunc):
        super().__init__()
        self.closeSettingFunc = closeSettingFunc

    def closeEvent(self, a0: QtGui.QCloseEvent):
        self.closeSettingFunc(self.MenggabaikanShortcut.isChecked(), self.TopSaatRecord.isChecked(), self.TopMauUnpause.isChecked(), self.SelaluDiulang.isChecked(), self.TidakDiulang.isChecked(), self.TopSaatSelesaiRecorder.isChecked())

    def SemuaSetting(self):
        return self.MenggabaikanShortcut, self.TopSaatRecord, self.TopMauUnpause, self.SelaluDiulang, self.TidakDiulang, self.TopSaatSelesaiRecorder

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(400, 300)
        self.setFixedSize(self.size())
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui\\../icon/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.formLayoutWidget = QtWidgets.QWidget(self)
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
        self.TidakDiulang.setChecked(True)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.TidakDiulang)
        self.SelaluDiulang = QtWidgets.QRadioButton(self.formLayoutWidget)
        self.SelaluDiulang.setObjectName("SelaluDiulang")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.SelaluDiulang)
        self.formLayoutWidget_2 = QtWidgets.QWidget(self)
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
        self.TopSaatSelesaiRecorder = QtWidgets.QCheckBox(self.formLayoutWidget_2)
        self.TopSaatSelesaiRecorder.setObjectName("TopSaatSelesaiRecorder")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.TopSaatSelesaiRecorder)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Setting"))
        self.label.setText(_translate("Dialog", "Settingan loop"))
        self.TidakDiulang.setText(_translate("Dialog", "Tidak diulang"))
        self.SelaluDiulang.setText(_translate("Dialog", "Selalu diulang"))
        self.label_2.setText(_translate("Dialog", "Settingan       "))
        self.MenggabaikanShortcut.setText(_translate("Dialog", "Mengabaikan keyboard shortcuts"))
        self.TopSaatRecord.setText(_translate("Dialog", "Always top saat mulai recorder"))
        self.TopMauUnpause.setText(_translate("Dialog", "Always top saat mau unpause"))
        self.TopSaatSelesaiRecorder.setText(_translate("Dialog", "Always top saat selesai record"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = WindowUtama(MainWindow)
    ui.setupUi()
    MainWindow.show()
    win32gui.EnumWindows(ui.winEnumHandler, None)
    sys.exit(app.exec_())
"""