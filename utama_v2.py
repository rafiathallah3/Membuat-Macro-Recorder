from __future__ import annotations

import sys, time, win32gui, win32con, enum, threading, json, os
from PyQt5 import QtCore, QtGui, QtWidgets

from pynput.keyboard import Listener as KeyboardListener, Key, Controller as keyboardController, KeyCode
from pynput.mouse import Listener as MouseListener, Button, Controller as mouseController

"""
    "komentar"
    [27/01/2022 19:07]  COK! KOK BISA TERHAPUS UTAMA VERSI 1 ?? 
                        emang aneh ni github
                        cok ini "Merge bance master" artinya apaaan????? 
                        cara menghidupkan projek utama versi 1 gua gimana ya?
                        projek gua dulu, hilang :(
    [27/01/2022 19:20]  Alhamdullilaah, untuuung aja gua ada buka browser github gua langsung ke projek utama_v1, alhamdullilaaaah

    "info"
    [17/01/2022 15:17]  Ini akan diperbarui soalnya ada apdet dan fitur lainnya yang mau ditambahin
                        "Kenapa tidak disatukan dengan utama v1?" Karena kodenya jadi berantakan
    [17/01/2022 18:59]  Aku gk tau kenapa tidak bisa `pip install pyqt5-tools` jadi harus di pause dulu
    [24/01/2022 17:32]  Akhirnya bisa mendapatkan qt_tools, hal ini disebabkan karena qt_tools tidak support python versi 3.10
    [26/01/2022 22:53]  Yang harus di buat adalah tombol mulai
    [27/01/2022 18:51]  Masalah saat menambahkan nilai recorder, waktu ingin record input, program pynput (modul untuk mendapatkan input keyboard&mause)
                        akan ngereturn keycode / key class, Masalahnya kalo kita save recordernya maka ada error karena keycodenya bukan string
                        kalau kita buat dia string, ada masalah lagi untuk ngeload filenya, kita tidak bisa mengkontorl value tersebut. Sheesh.
                        jadi kemungkinan fixnya dengan cara: 
                        
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
    def __init__(self, MainWindow: QtWidgets.QMainWindow):
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
            "RecordGerakanMouse": False,
            "MenggabaikanShortcut": False,
            "TopSaatRecord": False,
            "TopMauUnpause": False,
            "SelaluDiulang": False, 
            "TidakDiulang": True,
            "TopSaatSelesaiRecorder": True,
            "Aksi": [] #Dalam aksi: {"Aksi": Nama aksinya, "keyValue": value yang berisi value macro, "keyName": nama yang berisi nama macro "Waktu": Waktu record macronya}
        }

        self.WaktuMulaiRecorder = self.WaktuMulaiPause = 0
        self._NamaAplikasi = "Macro Recorder - untitled"
        self._MulaiRecorder = self._MulaiMacro = self._Pause = False
        self.Aplikasi = self.path = self.setting = None

        self.KeyboardKontoller = keyboardController()
        self.MouseKontoller = mouseController()

        self.Monitor = KeySamaMouse_Monitor()
        self.Monitor.tekanKey.connect(self.TekanKeyFunc)
        self.Monitor.KlikMouse.connect(self.KlikMosFunc)
        self.Monitor.startMonitor()

    #Klik Tombol Function
    def KlikTombolStop(self):
        self.MulaiRecorder = False
        self.MulaiMacro = False

    def KlikTombolSetting(self):
        if self.MulaiRecorder or self.MulaiMacro: return
        # "RecordGerakanMouse": False,
        # "MenggabaikanShortcut": False,
        # "TopSaatRecord": False,
        # "TopMauUnpause": False,
        # "TopSaatSelesaiRecorder": True,
        # "SelaluDiulang": False, 
        # "TidakDiulang": True,

        self.setting = UI_Setting(self.settingTutupFunc)

        i: QtWidgets.QCheckBox
        for i in [
                self.setting.RecordGerakanMouse,
                self.setting.MenggabaikanShortcut,
                self.setting.TopSaatRecord, 
                self.setting.TopMauUnpause, 
                self.setting.SelaluDiulang,
                self.setting.TidakDiulang,
                self.setting.TopSaatSelesaiRecorder
            ]:
            i.setChecked(self.HasilRecorder[i.objectName()])

        self.setting.exec_()
        
    #Keyboard mouse input function
    def TekanKeyFunc(self, key, tekan):
        if self.MulaiRecorder and not (key == self.Keybind["Record"]["KeyValue"] or key == self.Keybind["Mulai"]["KeyValue"] or key == self.Keybind["Pause"]["KeyValue"]):
            #kita dapatkan ordinary karena di pynput kalau kamu tekan tombol control dan alphabet key lainnya, maka ditunjukkan emot
            if self.HasilRecorder['MenggabaikanShortcut'] and len(key.char if isinstance(key, KeyCode) else key.value.char) != 1:
                return

            self.TambahinAksi(
                NamaAksiRecorder.KETIK_TAHAN.value if tekan else NamaAksiRecorder.KETIK_LEPAS.value,
                key.vk if isinstance(key, KeyCode) else key.value.vk,
                chr(key.vk).lower() if isinstance(key, KeyCode) else str(key)[4:]
            )
            
        if key == self.Keybind["Record"]["KeyValue"] and tekan and not self.MulaiMacro:
            self.MulaiRecorder = not self.MulaiRecorder

        if key == self.Keybind["Mulai"]["KeyValue"] and tekan and not self.MulaiRecorder and self.HasilRecorder["Aksi"]:
            self.MulaiMacro = not self.MulaiMacro

        if key == self.Keybind["Pause"]["KeyValue"] and tekan and self.MulaiRecorder:
            self.Pause = not self.Pause

        if self.setting and self.setting.GantiKeybind and tekan:
            NamaKey = key.char.upper() if isinstance(key, KeyCode) else str(key)[4:].upper()
            self.Keybind[self.setting.NamaGantiKeybind['jenis']]['Nama'] = NamaKey
            self.Keybind[self.setting.NamaGantiKeybind['jenis']]['KeyValue'] = key
            self.setting.BerikanKey(NamaKey)

    def KlikMosFunc(self, Hasil):
        if self.MulaiRecorder:
            if Hasil["Kondisi"] == "Gerakan" and self.HasilRecorder["RecordGerakanMouse"]:
                self.TambahinAksi(
                    NamaAksiRecorder.GERAKAN_MOUSE.value,
                    Hasil["Pos"],
                    " ".join([str(x) for x in Hasil["Pos"]])
                )

            if Hasil["Kondisi"] == "Klik":
                if Hasil["Tekan"]: self.TambahinAksi(
                    NamaAksiRecorder.KLIK_KIRI_TAHAN.value if Hasil["Tombol"] == Button.left else NamaAksiRecorder.KLIK_KANAN_TAHAN.value,
                    Hasil["Pos"],
                    " ".join([str(x) for x in Hasil["Pos"]])
                )
                else: self.TambahinAksi(
                    NamaAksiRecorder.KLIK_KIRI_LEPAS.value if Hasil["Tombol"] == Button.left else NamaAksiRecorder.KLIK_KANAN_LEPAS.value,
                    Hasil["Pos"],
                    " ".join([str(x) for x in Hasil["Pos"]])
                )

            if Hasil["Kondisi"] == "Scroll":
                self.TambahinAksi(
                    NamaAksiRecorder.SCROLL_ATAS.value if Hasil["Scroll"][1] > 0 else NamaAksiRecorder.SCROLL_BAWAH.value,
                    Hasil["Scroll"],
                    " ".join([str(x) for x in Hasil["Pos"]])
                )

    #Function Lainnya
    def TambahinAksi(self, namaAksi, nilai, nama):
        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) != self.NamaAplikasi and not self.Pause:
            self.HasilRecorder["Aksi"].append({
                "Aksi": namaAksi,
                "keyValue": nilai,
                "keyName": nama if nama else nilai,
                "Waktu": "{:.2f}".format(time.perf_counter() - self.WaktuMulaiRecorder)
            })

    def GantiTableUiDariHasilRecorder(self):
        self.tableWidget.setRowCount(len(self.HasilRecorder["Aksi"]))
        for i,v in enumerate(self.HasilRecorder["Aksi"]):
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(v["Aksi"]))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(v["keyName"])))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(v["Waktu"]+" detik"))

    def settingTutupFunc(self, setting: UI_Setting):
        i: QtWidgets.QCheckBox
        for i in [
                setting.RecordGerakanMouse,
                setting.MenggabaikanShortcut,
                setting.TopSaatRecord, 
                setting.TopMauUnpause, 
                setting.SelaluDiulang,
                setting.TidakDiulang,
                setting.TopSaatSelesaiRecorder
            ]:
            self.HasilRecorder[i.objectName()] = i.isChecked()

        self.setting = None

    def ThreadMulaiMacro(self):
        while True:
            WaktuTombolMulai = time.perf_counter()
            for i in self.HasilRecorder["Aksi"]:
                if not self.MulaiMacro: break
                WaktuDiTunggu = WaktuTombolMulai + float(i["Waktu"])

                while time.perf_counter() < WaktuDiTunggu:...
                else:
                    aksi = i["Aksi"]

                    if aksi == NamaAksiRecorder.KLIK_KIRI_TAHAN.value or aksi == NamaAksiRecorder.KLIK_KANAN_TAHAN.value:
                        self.MouseKontoller.position = i["keyValue"]
                        self.MouseKontoller.press(Button.left if aksi == NamaAksiRecorder.KLIK_KIRI_TAHAN.value else Button.right)
                        
                    elif aksi == NamaAksiRecorder.KLIK_KIRI_LEPAS.value or aksi == NamaAksiRecorder.KLIK_KANAN_LEPAS.value:
                        self.MouseKontoller.position = i["keyValue"]
                        time.sleep(.01) #Ini di tunggu supaya... apa ya, susa juga dijelasin, coba aja di pake ke notepad terus tahan dan ke text lain terus ada warna background birunya, kalau tidak ada penunggu, background birunya tidak ada
                        self.MouseKontoller.release(Button.left if aksi == NamaAksiRecorder.KLIK_KIRI_LEPAS.value else Button.right)

                    elif aksi == NamaAksiRecorder.SCROLL_ATAS.value or aksi == NamaAksiRecorder.SCROLL_BAWAH.value:
                        self.MouseKontoller.scroll(i["keyValue"])
                        
                    elif aksi == NamaAksiRecorder.KETIK_TAHAN.value:
                        self.KeyboardKontoller.press(KeyCode(vk=i["keyValue"]))
                    elif aksi == NamaAksiRecorder.KETIK_LEPAS.value:
                        self.KeyboardKontoller.release(KeyCode(vk=i["keyValue"]))

            if self.HasilRecorder['TidakDiulang'] or not self.MulaiMacro: break

    def Buka_File(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self.MainWindow, 'Buka file', "", 'Json files (*.json)')

        if path:
            try:
                with open(path) as f:
                    hasil_json = json.load(f)

                if len(hasil_json) != 8:
                    raise Exception('Ada kesalahan saat membuka file tersebut!')

            except Exception as e:
                self.dialog_error(e)
            else:
                self.path = path
                self.HasilRecorder = hasil_json
                self.GantiTableUiDariHasilRecorder()
                self.TombolMulai.setEnabled(bool(self.HasilRecorder['Aksi']))
                self.NamaAplikasi = f'Macro Recorder - {os.path.basename(self.path) if self.path else "untitled"}'

    def simpan_File(self):
        if not self.HasilRecorder['Aksi']: return

        if not self.path:
            return self.SimpanSebagai_File()
        self.SimpanKePath()

    def SimpanSebagai_File(self):
        if not self.HasilRecorder['Aksi']: return

        self.path, _ = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow, "Save file", "", "Json file (*.json)")
        if not self.path: return

        self.SimpanKePath()

    def SimpanKePath(self):
        file_json = json.dumps(self.HasilRecorder, indent=4)

        try:
            with open(self.path, 'w') as f:
                f.write(file_json)
        except Exception as e:
            self.dialog_error(e)
        else:
            self.NamaAplikasi = f"Macro Recorder - {os.path.basename(self.path) if self.path else 'untitled'}"

    def dialog_error(self, pesan):
        dia = QtWidgets.QMessageBox(self.MainWindow)
        dia.setWindowTitle('Masalah')
        dia.setText(str(pesan))
        dia.setIcon(QtWidgets.QMessageBox.Critical)
        dia.show()

    #cuman property 
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
            print("Mulai")
            self.HasilRecorder["Aksi"] = []
            self.WaktuMulaiRecorder = time.perf_counter()

            if not self.HasilRecorder["TopSaatRecord"]:
                win32gui.ShowWindow(self.Aplikasi, win32con.SW_MINIMIZE)
        else:
            print("Stop")
            self.Pause = False
            self.TombolPause.setEnabled(False)
            self.TombolMulai.clicked.disconnect()
            self.TombolMulai.clicked.connect(lambda: setattr(self, "MulaiMacro", not self.MulaiMacro))

            self.TombolMulai.setEnabled(bool(self.HasilRecorder["Aksi"]))
            self.GantiTableUiDariHasilRecorder()

        self._MulaiRecorder = val

    @property
    def MulaiMacro(self):
        return self._MulaiMacro
    
    @MulaiMacro.setter
    def MulaiMacro(self, val):
        self._MulaiMacro = val

        win32gui.ShowWindow(self.Aplikasi, win32con.SW_MINIMIZE if val else win32con.SW_MAXIMIZE)
        if val:
            t = threading.Thread(target=self.ThreadMulaiMacro)
            t.start()

    @property
    def Pause(self):
        return self._Pause

    @Pause.setter
    def Pause(self, val):
        if val:
            print("PAUSEE")
            if self.MulaiRecorder and not self.Pause:
                self.WaktuMulaiPause = time.perf_counter()
        else:
            print("Unpause")
            self.WaktuMulaiRecorder = time.perf_counter() - (self.WaktuMulaiPause - self.WaktuMulaiRecorder)

            if not self.HasilRecorder['TopMauUnpause']:
                win32gui.ShowWindow(self.Aplikasi, win32con.SW_MINIMIZE)
        
        self.TombolPause.setEnabled(not val)
        self.TombolMulai.setEnabled(val)
        self.TombolMulai.setToolTip("Unpause" if val else "Mulai hasil recorder")

        self._Pause = val

        self.TombolMulai.clicked.disconnect()
        self.TombolMulai.clicked.connect(lambda: setattr(self, "Pause", False) if val else lambda: setattr(self, "MulaiMacro", True))

    @property
    def NamaAplikasi(self):
        return self._NamaAplikasi
    
    @NamaAplikasi.setter
    def NamaAplikasi(self, val):
        self._NamaAplikasi = val
        self.MainWindow.setWindowTitle(val)

    #Setup ui
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
        
        self.actionSimpan = QtWidgets.QAction(self.MainWindow)
        self.actionSimpan.setObjectName("actionSave")
        
        self.actionSimpanSebagai = QtWidgets.QAction(self.MainWindow)
        self.actionSimpanSebagai.setObjectName("actionSaveAs")

        self.actionBuka = QtWidgets.QAction(self.MainWindow)
        self.actionBuka.setObjectName("actionOpen")
        
        self.actionKeluar = QtWidgets.QAction(self.MainWindow)
        self.actionKeluar.setObjectName("actionExit")
        
        self.menuFile.addAction(self.actionSimpan)
        self.menuFile.addAction(self.actionSimpanSebagai)
        self.menuFile.addAction(self.actionBuka)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionKeluar)
        
        self.menubar.addAction(self.menuFile.menuAction())

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
        
        self.TombolMulai.setDisabled(True)
        self.TombolHapus.setDisabled(True)
        self.TombolStop.setDisabled(True)
        self.TombolPause.setDisabled(True)

        self.menuFile.setTitle(_translate("MainWindow", "File"))

        self.actionSimpan.setText(_translate("MainWindow", "Simpan"))
        self.actionSimpanSebagai.setText(_translate("MainWindow", "Simpan Sebagai"))
        self.actionBuka.setText(_translate("MainWindow", "Buka"))
        self.actionKeluar.setText(_translate("MainWindow", "Keluar"))

        self.actionSimpan.setShortcut('ctrl+S')
        self.actionSimpanSebagai.setShortcut('ctrl+shift+S')
        self.actionBuka.setShortcut('ctrl+O')

        self.actionSimpan.triggered.connect(self.simpan_File)
        self.actionSimpanSebagai.triggered.connect(self.SimpanSebagai_File)
        self.actionBuka.triggered.connect(self.Buka_File)
        self.actionKeluar.triggered.connect(lambda: self.MainWindow.close())
        
        self.TombolRecord.clicked.connect(lambda: setattr(self, "MulaiRecorder", True))
        self.TombolMulai.clicked.connect(lambda: setattr(self, "MulaiMacro", True))
        self.TombolPause.clicked.connect(lambda: setattr(self, "Pause", not self.Pause))
        self.TombolStop.clicked.connect(self.KlikTombolStop)
        self.TombolSetting.clicked.connect(self.KlikTombolSetting)

class UI_Setting(QtWidgets.QDialog):
    def __init__(self, settingFunc):
        super().__init__()
        self.settingFunc = settingFunc
        
        self.NamaGantiKeybind: dict = None
        self.NamaKeybind = ""
        self.GantiKeybind = False
        
        self.setupUi()

    def closeEvent(self, event):
        self.settingFunc(self)

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(400, 300)
        self.setToolTip("")

        self.formLayoutWidget = QtWidgets.QWidget(self)
        self.formLayoutWidget.setGeometry(QtCore.QRect(70, 110, 261, 71))
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
        
        self.formLayoutWidget_2 = QtWidgets.QWidget(self)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(70, 10, 261, 100))
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

        self.RecordGerakanMouse = QtWidgets.QCheckBox(self.formLayoutWidget_2)
        self.RecordGerakanMouse.setObjectName("RecordGerakanMouse")
        
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.RecordGerakanMouse)

        font = QtGui.QFont()
        font.setPointSize(8)
        self.TombolGantiRecord = QtWidgets.QPushButton(self)
        self.TombolGantiRecord.setGeometry(QtCore.QRect(70, 170, 141, 31))
        self.TombolGantiRecord.setFont(font)
        self.TombolGantiRecord.setObjectName("TombolGantiRecord")
        
        font = QtGui.QFont()
        font.setPointSize(18)
        self.labelKeybindRecord = QtWidgets.QLineEdit(self)
        self.labelKeybindRecord.setFont(font)
        self.labelKeybindRecord.setGeometry(QtCore.QRect(260, 170, 61, 31))
        self.labelKeybindRecord.setAlignment(QtCore.Qt.AlignCenter)
        self.labelKeybindRecord.setReadOnly(True)
        self.labelKeybindRecord.setObjectName("labelKeybindRecord")
        
        font = QtGui.QFont()
        font.setPointSize(8)
        self.TombolGantiMulai = QtWidgets.QPushButton(self)
        self.TombolGantiMulai.setGeometry(QtCore.QRect(70, 210, 141, 31))
        self.TombolGantiMulai.setFont(font)
        self.TombolGantiMulai.setObjectName("TombolGantiMulai")
        
        font = QtGui.QFont()
        font.setPointSize(18)
        self.labelKeybindMulai = QtWidgets.QLineEdit(self)
        self.labelKeybindMulai.setGeometry(QtCore.QRect(260, 210, 61, 31))
        self.labelKeybindMulai.setFont(font)
        self.labelKeybindMulai.setAlignment(QtCore.Qt.AlignCenter)
        self.labelKeybindMulai.setReadOnly(True)
        self.labelKeybindMulai.setObjectName("labelKeybindMulai")
        
        font = QtGui.QFont()
        font.setPointSize(18)
        self.labelKeybindPause = QtWidgets.QLineEdit(self)
        self.labelKeybindPause.setGeometry(QtCore.QRect(260, 250, 61, 31))
        self.labelKeybindPause.setFont(font)
        self.labelKeybindPause.setAlignment(QtCore.Qt.AlignCenter)
        self.labelKeybindPause.setReadOnly(True)
        self.labelKeybindPause.setObjectName("labelKeybindPause")
        
        font = QtGui.QFont()
        font.setPointSize(8)
        self.TombolGantiPause = QtWidgets.QPushButton(self)
        self.TombolGantiPause.setGeometry(QtCore.QRect(70, 250, 141, 31))
        self.TombolGantiPause.setFont(font)
        self.TombolGantiPause.setObjectName("TombolGantiPause")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        
        self.label.setText(_translate("Dialog", "Settingan loop"))
        
        self.TidakDiulang.setText(_translate("Dialog", "Tidak diulang"))
        self.SelaluDiulang.setText(_translate("Dialog", "Selalu diulang"))
        
        self.label_2.setText(_translate("Dialog", "Settingan       "))
        
        self.MenggabaikanShortcut.setText(_translate("Dialog", "Mengabaikan keyboard shortcuts"))
        self.TopSaatRecord.setText(_translate("Dialog", "Always top saat mulai recorder"))
        self.TopMauUnpause.setText(_translate("Dialog", "Always top saat mau unpause"))
        self.TopSaatSelesaiRecorder.setText(_translate("Dialog", "Always top saat selesai Recording"))
        self.RecordGerakanMouse.setText(_translate("Dialog", "Record gerakan mouse"))
        
        self.TombolGantiRecord.setText(_translate("Dialog", "Ganti Keybind Record/Stop"))
        self.TombolGantiMulai.setText(_translate("Dialog", "Ganti Keybind Mulai/Stop"))
        self.TombolGantiPause.setText(_translate("Dialog", "Keybind Pause/Unpause"))
        
        self.labelKeybindMulai.setText(_translate("Dialog", "F7"))
        self.labelKeybindRecord.setText(_translate("Dialog", "F6"))
        self.labelKeybindPause.setText(_translate("Dialog", "F8"))        
        
        self.TombolGantiMulai.clicked.connect(lambda: self.GantiKeybindFunc(self.labelKeybindMulai, "Mulai", self.TombolGantiMulai))
        self.TombolGantiRecord.clicked.connect(lambda: self.GantiKeybindFunc(self.labelKeybindRecord, "Record", self.TombolGantiRecord))
        self.TombolGantiPause.clicked.connect(lambda: self.GantiKeybindFunc(self.labelKeybindPause, "Pause", self.TombolGantiPause))

    def GantiKeybindFunc(self, label: QtWidgets.QLineEdit, jenis: str, tombol: QtWidgets.QPushButton):
        # Walaupun sudah di set datanya SEBELUM variabelnya diganti, tetap aja pyqt5 akan mengganti data tersebut
        self.NamaGantiKeybind = {"label": label, "tombol": tombol, "tombol text": tombol.text(),"jenis": jenis}
        self.GantiKeybind = True

        tombol.setText('Menunggu tekanan...')

    def BerikanKey(self, key: str):
        self.NamaGantiKeybind['label'].setText(key)
        self.NamaGantiKeybind['tombol'].setText(self.NamaGantiKeybind['tombol text'])
        self.GantiKeybind = False

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_WindowUtama(MainWindow)
    ui.setupUi()
    MainWindow.show()
    win32gui.EnumWindows(ui.winEnumHandler, None)
    try:
        sys.exit(app.exec_())
    except:
        print("Ini supaya tidak ada terjadi error ketika sang pengguna applikasi menekan tombol close dari appnya")