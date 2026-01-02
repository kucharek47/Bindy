import os
import threading
from pynput import mouse, keyboard as pynput_keyboard
import keyboard as kb
import pyaudio
import sounddevice as sd
import wave
import numpy as np
import time
from PyQt6.QtCore import Qt, QTimer, qDebug
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QFrame
import sys
import ast
from test import WykryanieSpike

qDebug("Debug message")

class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.kolor_trojkata = QColor("#ffffff")
        self.grubosci_lini_trojkata = 0
        self.last_key = None
        self.ostatni = time.time()
        self.pierwszy_raz = True
        self.stop2 = False
        self.nadawwanie = False
        self.stan_okna = True
        self.start()
        self.konf_okna()
        self.sprawdzanie_spike()
    def ustawienie_znacznika_spike(self,kolor,grubosc=5):
        print(kolor,grubosc)
        self.kolor_trojkata = QColor(kolor)
        self.grubosci_lini_trojkata = grubosc
        self.update()

    def sprawdz_spike(self):
        status = self.spike_detector.status()
        print(status)
        if status:
            self.ustawienie_znacznika_spike("#00ff00")
            time.sleep(31)
            self.ustawienie_znacznika_spike("#e8e700")
            time.sleep(3)
            self.ustawienie_znacznika_spike("#ff0000")
            time.sleep(3)
            self.ustawienie_znacznika_spike("#000000")
            time.sleep(7)
            self.ustawienie_znacznika_spike("#ffffff",0)

    def sprawdzanie_spike(self):
        self.spike_detector = WykrywanieSpike(self.height(),self.width())
        self.timer = QTimer()
        self.timer.timeout.connect(self.sprawdz_spike)
        self.timer.start(250)

    def paintEvent(self, event):
        painter = QPainter(self)

        base_w = 1920.0
        base_h = 1080.0

        sx = self.width() / base_w
        sy = self.height() / base_h

        painter.scale(sx, sy)

        pen = QPen(QColor("red"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(228, 240, 228, 40)

        pen_trojkat = QPen(self.kolor_trojkata)
        pen_trojkat.setWidth(self.grubosci_lini_trojkata)
        painter.setPen(pen_trojkat)
        painter.drawLine(900, 10, 1020, 10)
        painter.drawLine(1020, 15, 960, 110)
        painter.drawLine(960, 110, 900, 15)

    def konf_okna(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_rect)

        files = [f[:2] + " " + f[2:-4] for f in os.listdir("dzwieki") if f.endswith(".wav")]
        mid = int(len(files) // 2)
        left_files = files[:mid]
        right_files = files[mid:]

        body_style = "font-size:13px; color:white; margin:0; padding:0; line-height:1.1; margin-top:30px;"
        hr_style = "border:1px solid black; margin:0; padding:0;"

        left_text = f"<html><body style='{body_style}'>"
        for i, fname in enumerate(left_files, start=1):
            left_text += fname + "<br>"
            if i % 10 == 0:
                left_text += f"<hr style='{hr_style}'>"
        left_text += "</body></html>"

        right_text = f"<html><body style='{body_style}'>"
        for i, fname in enumerate(right_files, start=1):
            right_text += fname + "<br>"
            if i % 10 == 0:
                right_text += f"<hr style='{hr_style}'>"
        right_text += "</body></html>"

        left_label = QLabel()
        left_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        left_label.setFixedWidth(200)
        left_label.setText(left_text)
        left_label.setStyleSheet("color: white;")

        right_label = QLabel()
        right_label.setFixedWidth(200)
        right_label.setText(right_text)
        right_label.setStyleSheet("color: white;")

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedWidth(2)

        gui_layout = QHBoxLayout()
        gui_layout.setContentsMargins(0, 0, 0, 0)
        gui_layout.setSpacing(0)
        gui_layout.addWidget(left_label)
        gui_layout.addWidget(separator)
        gui_layout.addWidget(right_label)

        gui_widget = QWidget()
        gui_widget.setLayout(gui_layout)
        gui_widget.setFixedWidth(402)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        spacer = QWidget()
        main_layout.addWidget(spacer)
        main_layout.addWidget(gui_widget)

        self.setLayout(main_layout)

    def start(self):
        self.con = pynput_keyboard.Controller()
        print("Dostępne urządzenia audio:")
        print(sd.query_devices())

        try:
            with open("ustawienie.txt", "r", encoding="utf-8") as f:
                ustawienia = ast.literal_eval(f.read())
            print("Ustawienia załadowane. Jeśli zmieni się liczba urządzeń, usuń plik ustawienie.txt.")
            self.wyjsce = ustawienia[0]
            for device in sd.query_devices():
                if device["name"] == "Line 1 (Virtual Audio Cable)" and \
                   device["max_input_channels"] == 0 and device["max_output_channels"] == 2:
                    self.wyjsce = device["index"]
                    print(f"Znaleziono Virtual Audio Cable o indeksie: {self.wyjsce}")
                    break
            self.volum1 = ustawienia[1]
            self.volum2 = ustawienia[2]
        except Exception as e:
            print("Błąd wczytywania ustawień, wprowadź je ręcznie.")
            self.wyjsce = int(input("Podaj numer urządzenia dla 'CABLE Input (VB-Audio Virtual C, MME (0 in, 2 out))': "))
            self.volum1 = float(input("Moc oddtwarzania u Ciebie (0-1, 0 - WYŁĄCZONY, 1 - MAX): "))
            self.volum2 = float(input("Moc oddtwarzania u innych (0-1, 0 - WYŁĄCZONY, 1 - MAX): "))
            with open("ustawienie.txt", "w", encoding="utf-8") as f:
                f.write(str([self.wyjsce, self.volum1, self.volum2]))

        self.playlista = [f for f in os.listdir("dzwieki") if f.endswith(".wav")]
        try:
            with open("czestotliwosci uzytwania.txt", "r", encoding="utf-8") as f:
                self.slownik = ast.literal_eval(f.read())
        except Exception as e:
            print("Nie udało się wczytać 'czestotliwosci uzytwania.txt'. Inicjalizuję pusty słownik.")
            self.slownik = {}
        self.czekaj_na_klikniecie()

    def play_sound(self, name):
        self.nadawwanie = True
        file_path = None
        for filename in self.playlista:
            if filename.startswith(name):
                file_path = filename
                break

        print(file_path)
        if file_path:
            self.slownik[file_path] = self.slownik.get(file_path, 0) + 1
            wf_path = os.path.join("dzwieki", file_path)
            wf = wave.open(wf_path, 'rb')
            p = pyaudio.PyAudio()
            self.con.press("-")
            try:
                stream1 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True,
                                 output_device_index=self.wyjsce)
                stream2 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)
                data = wf.readframes(1024)
                while data:
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    data_out1 = (audio_data * self.volum2).astype(np.int16).tobytes()
                    data_out2 = (audio_data * self.volum1).astype(np.int16).tobytes()
                    stream1.write(data_out1)
                    stream2.write(data_out2)
                    data = wf.readframes(1024)
                    if (not kb.is_pressed("-") and not self.pierwszy_raz) or self.stop2:
                        break
                self.pierwszy_raz = False
            finally:
                self.con.release("-")
                stream1.stop_stream()
                stream1.close()
                stream2.stop_stream()
                stream2.close()
                p.terminate()
                self.nadawwanie = False
                self.stop2 = False
                with open("czestotliwosci uzytwania.txt", "w", encoding="utf-8") as f:
                    f.write(str(self.slownik))
        else:
            print(f"Nie znaleziono pliku zaczynającego się od: {name}")

    def on_press(self, key):
        try:
            if hasattr(key, 'vk'):
                vk = key.vk
            else:
                return

            valid_keys = [96, 97, 98, 99, 100, 101, 102, 103, 104, 105]
            if vk in valid_keys:
                now = time.time()
                if now - self.ostatni < 5 and self.last_key is not None:
                    first_index = valid_keys.index(self.last_key)
                    second_index = valid_keys.index(vk)
                    counter = 0
                    while self.nadawwanie:
                        if counter > 20:
                            break
                        self.stop2 = True
                        counter += 1
                        time.sleep(0.1)
                        print("Próba zatrzymania odtwarzania")
                    # Prefiks nazwy pliku oparty o numery klawiszy
                    key_prefix = f"{first_index}{second_index}"
                    thread = threading.Thread(target=self.play_sound, args=(key_prefix,))
                    thread.start()
                    self.last_key = None
                else:
                    self.last_key = vk
                self.ostatni = now
        except Exception as e:
            print(f"Błąd w on_press: {e}")

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.x2:
            if self.stan_okna:
                self.hide()
            else:
                self.show()
            self.stan_okna = not self.stan_okna


    def czekaj_na_klikniecie(self):
        print("Czekam na kliknięcie klawisza. Naciśnij dowolny klawisz.")
        self.listenerM = mouse.Listener(on_click=self.on_click)
        self.listenerK = pynput_keyboard.Listener(on_release=self.on_press)
        self.listenerM.start()
        self.listenerK.start()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransparentWindow()
    window.show()
    sys.exit(app.exec())
