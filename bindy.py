import os
import threading
from pynput import mouse
import pynput.keyboard
from pynput import keyboard
import keyboard as kb
import pyaudio
import sounddevice as sd
import wave
import numpy as np
import time
import pyautogui
import sys

def play_sound(name):
    global pierwszy_raz, nadawwanie, stop2, slownik
    nadawwanie = True
    file_path = False
    utworzy = os.listdir("dzwieki")
    utworzy2 = []
    for x in utworzy:
        if x.endswith(".wav"):
            utworzy2.append(x)
    for x in utworzy2:
        if x.startswith(name):
            file_path = x
            stop = False
    print(file_path)
    if file_path:
        try:
            slownik[file_path] += 1
        except:
            slownik[file_path] = 1
        wf = wave.open("dzwieki\\" + file_path, 'rb')
        p = pyaudio.PyAudio()
        con.press("-")
        try:
            stream1 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True,
                            output_device_index=wyjsce)
            stream2 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(1024)
            while data:
                audio_data = np.frombuffer(data, dtype=np.int16)
                audio_data = (audio_data * volum1).astype(np.int16)
                data_out = audio_data.tobytes()
                stream1.write(data_out)
                stream2.write(data_out)
                data = wf.readframes(1024)
                if not kb.is_pressed("-") and not pierwszy_raz or stop2:
                    break
            pierwszy_raz = False
        finally:
            con.release("-")
            stream1.stop_stream()
            stream1.close()
            stream2.stop_stream()
            stream2.close()
            p.terminate()
            nadawwanie = False
            stop2 = False
            open("czestotliwosci uzytwania.txt","w",encoding="utf-8").write(str(slownik))
def on_press(key):
    global x,y, ostatni,play, stop2
    try:
        przycisk = key.vk
        if przycisk in [96, 97, 98, 99, 100, 101, 102, 103, 104, 105]:
            if time.time() - ostatni < 5:
                y = x
            ostatni = time.time()
            x = przycisk
            if y:
                x = [96, 97, 98, 99, 100, 101, 102, 103, 104, 105].index(int(x))
                y = [96, 97, 98, 99, 100, 101, 102, 103, 104, 105].index(int(y))
                licznenie = 0
                while nadawwanie:
                    if licznenie > 20:
                        break
                    stop2 = True
                    licznenie += 1
                    time.sleep(0.1)
                    print("proba zatrzymania")
                play = threading.Thread(target=play_sound, args=(f"{y}{x}",))
                play.start()
                x = False
                y = False
    except:
        pass
def on_click(x, y, button, pressed):
    def move_with_pause(start_x, start_y, end_x, end_y, duration):
        steps = 50  # Liczba kroków ruchu
        x_step = (end_x - start_x) / steps
        y_step = (end_y - start_y) / steps

        for i in range(steps):
            pyautogui.moveTo(start_x + x_step * i, start_y + y_step * i)
            time.sleep(duration / steps)  # Opóźnienie pomiędzy krokami
    if pressed and button == mouse.Button.x2:
        move_with_pause(285, 742, 285, 742, 0.5)
        pyautogui.click()
        time.sleep(0.1)

        move_with_pause(285, 742, 935, 750, 0.5)
        pyautogui.click()
        time.sleep(0.2)
def czekaj_na_klikniecie():
    print("Czekam na kliknięcie klawisza. Naciśnij dowolny klawisz.")
    listenerM = mouse.Listener(on_click=on_click)
    listenerK = keyboard.Listener(on_release=on_press)
    listenerM.start()
    listenerK.start()
    listenerK.join()
    listenerM.join()
if __name__ == "__main__":
    con = pynput.keyboard.Controller()
    print(sd.query_devices())
    try:
        ustawienia = eval(open("ustawienie.txt", "r", encoding="utf-8").read())
        print("pamietaj w razie zmiany stanu ilosciowego urzadzen wyjsciowo/wejsciowych numer bedzie nie prawidlowy, usun w tedy plik ustawienie.txt")
        wyjsce = ustawienia[0]
        for x in sd.query_devices():
            if "Line 1 (Virtual Audio Cable)" == x["name"] and x["max_input_channels"] == 0 and x["max_output_channels"] == 2:
                wyjsce = x["index"]
                print(wyjsce)
                break
        volum1 = ustawienia[1]
        volum2 = ustawienia[2]
    except:
        wyjsce = int(input("Podaj numer gdzie znajduje sie 'CABLE Input (VB-Audio Virtual C, MME (0 in, 2 out)' "))
        volum1 = float(input("moc oddtwarzania u ciebie (0-1 0-WYLACZONY 1-MAX) "))
        volum2 = float(input("moc oddtwarzania u innych (0-1 0-WYLACZONY 1-MAX) "))
        open("ustawienie.txt", "w", encoding="utf-8").write(str([wyjsce, volum1, volum2]))
    ostatni = time.time()
    pierwszy_raz = True
    x = False
    y = False
    stop2 = False
    nadawwanie = False
    slownik = eval(open("czestotliwosci uzytwania.txt","r",encoding="utf-8").read())
    play = threading.Thread(target=play_sound)
    czekaj_na_klikniecie()










