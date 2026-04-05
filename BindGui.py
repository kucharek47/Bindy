import os
import threading
import time
import sys
import ast
import wave
import numpy as np
import mss
import pyaudio
import sounddevice as sd
import keyboard as kb
from pynput import mouse, keyboard as pynput_keyboard
from PyQt6.QtCore import Qt, QTimer, qDebug
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QFrame
from ultralytics import YOLO
import cv2

qDebug("Debug message")


class WykrywanieSpike:
    def __init__(self, wyskosc=1440, szerokosc=2560, model_path="best.pt", miejsce_na_ekranie=None, conf=0.6,
                 czas_sprawdzania=0.1):
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            raise Exception(f"Nie udało się załadować modelu {model_path}. Błąd: {e}")

        if miejsce_na_ekranie is None:
            baza_w = 1920.0
            baza_h = 1080.0

            sx = szerokosc / baza_w
            sy = wyskosc / baza_h

            self.miejsce_na_ekranie = {
                "top": int(0 * sy),
                "left": int(700 * sx),
                "width": int(500 * sx),
                "height": int(400 * sy)
            }
        else:
            self.miejsce_na_ekranie = miejsce_na_ekranie

        self.conf = conf
        self._status = 0.0
        self._stop = False
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._detekcja, args=[czas_sprawdzania])
        self._thread.start()

    def _detekcja(self, czas_sprawdzania):
        with mss.mss() as sct:
            while not self._stop:
                sct_img = sct.grab(self.miejsce_na_ekranie)
                screen = np.array(sct_img)[:, :, :3]

                wynik = self.model.predict(source=screen, verbose=False, conf=self.conf, imgsz=640)

                szansa = 0.0

                if len(wynik) > 0:
                    obraz_podglad = wynik[0].plot()
                    cv2.imshow("Podglad AI", obraz_podglad)
                    cv2.waitKey(1)

                    if len(wynik[0].boxes) > 0:
                        szansa = wynik[0].boxes.conf[0].item()

                with self._lock:
                    self._status = szansa
                time.sleep(czas_sprawdzania)

    def status(self):
        with self._lock:
            return self._status

    def czekaj_na(self):
        while self.status() == 0.0:
            time.sleep(0.05)
        return True

    def stop(self):
        self._stop = True
        self._thread.join()


class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.kolor_trojkata = QColor("#ffffff")
        self.grubosci_lini_trojkata = 0
        self.ostatni_klucz = None
        self.ostatni = time.time()
        self.pierwszy_raz = True
        self.stop2 = False
        self.nadawwanie = False
        self.stan_okna = True
        self.odliczanie_trwa = False

        self.start()
        self.konf_okna()
        self.sprawdzanie_spike()

    def ustawienie_znacznika_spike(self, kolor, grubosc=5):
        print(f"Zmieniam kolor na: {kolor}, grubosc: {grubosc}")
        self.kolor_trojkata = QColor(kolor)
        self.grubosci_lini_trojkata = grubosc
        self.update()

    def reset_stanu(self):
        self.ustawienie_znacznika_spike("#ffffff", 0)
        self.odliczanie_trwa = False
        print("Koniec sekwencji")

    def sprawdz_spike(self):
        if self.odliczanie_trwa:
            return

        status = self.spike_detector.status()
        if status > 0:
            print(f"Wykryto z pewnością: {status * 100:.2f}%")
            self.odliczanie_trwa = True

            self.ustawienie_znacznika_spike("#00ff00")
            QTimer.singleShot(32000, lambda: self.ustawienie_znacznika_spike("#e8e700"))
            QTimer.singleShot(35000, lambda: self.ustawienie_znacznika_spike("#ff0000"))
            QTimer.singleShot(38000, lambda: self.ustawienie_znacznika_spike("#000000"))
            QTimer.singleShot(45000, lambda: self.ustawienie_znacznika_spike("#ffffff"))

            QTimer.singleShot(52000, self.reset_stanu)

    def sprawdzanie_spike(self):
        self.spike_detector = WykrywanieSpike(self.height(), self.width())
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
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_rect)

        try:
            files = [f[:2] + " " + f[2:-4] for f in os.listdir("dzwieki") if f.endswith(".wav")]
        except FileNotFoundError:
            files = []
            print("Katalog 'dzwieki' nie istnieje.")

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
        left_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        right_label = QLabel()
        right_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        right_label.setFixedWidth(200)
        right_label.setText(right_text)
        right_label.setStyleSheet("color: white;")
        right_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedWidth(2)
        separator.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        gui_layout = QHBoxLayout()
        gui_layout.setContentsMargins(0, 0, 0, 0)
        gui_layout.setSpacing(0)
        gui_layout.addWidget(left_label)
        gui_layout.addWidget(separator)
        gui_layout.addWidget(right_label)

        gui_widget = QWidget()
        gui_widget.setLayout(gui_layout)
        gui_widget.setFixedWidth(402)
        gui_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        gui_widget.setStyleSheet("background-color: rgba(0, 0, 0, 25);")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        spacer = QWidget()
        spacer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
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
        except Exception:
            print("Błąd wczytywania ustawień, wprowadź je ręcznie.")
            self.wyjsce = int(
                input("Podaj numer urządzenia dla 'CABLE Input (VB-Audio Virtual C, MME (0 in, 2 out))': "))
            self.volum1 = float(input("Moc oddtwarzania u Ciebie (0-1, 0 - WYŁĄCZONY, 1 - MAX): "))
            self.volum2 = float(input("Moc oddtwarzania u innych (0-1, 0 - WYŁĄCZONY, 1 - MAX): "))
            with open("ustawienie.txt", "w", encoding="utf-8") as f:
                f.write(str([self.wyjsce, self.volum1, self.volum2]))

        try:
            self.playlista = [f for f in os.listdir("dzwieki") if f.endswith(".wav")]
        except FileNotFoundError:
            self.playlista = []
            print("Nie znaleziono folderu 'dzwieki'.")

        try:
            with open("czestotliwosci uzytwania.txt", "r", encoding="utf-8") as f:
                self.slownik = ast.literal_eval(f.read())
        except Exception:
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
                if now - self.ostatni < 5 and self.ostatni_klucz is not None:
                    try:
                        first_index = valid_keys.index(self.ostatni_klucz)
                        second_index = valid_keys.index(vk)
                    except ValueError:
                        return

                    counter = 0
                    while self.nadawwanie:
                        if counter > 20:
                            break
                        self.stop2 = True
                        counter += 1
                        time.sleep(0.1)
                        print("Próba zatrzymania odtwarzania")

                    key_prefix = f"{first_index}{second_index}"
                    thread = threading.Thread(target=self.play_sound, args=(key_prefix,))
                    thread.start()
                    self.ostatni_klucz = None
                else:
                    self.ostatni_klucz = vk
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