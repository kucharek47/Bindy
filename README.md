# Bindy - Valorant AI Soundboard & Spike Detector

Zaawansowana nakładka (overlay) do gry Valorant, łącząca funkcje inteligentnego soundboardu oraz asystenta wykrywania Spike'a opartego na modelu YOLO. Aplikacja działa "zawsze na wierzchu", jest przezroczysta dla kliknięć myszy i nie zakłóca rozgrywki.

## 🚀 Główne Funkcje

### 1. Wykrywanie Spike'a (AI)
* Wykorzystuje model **YOLO** (`best.pt`) do analizy obrazu w czasie rzeczywistym.
* Automatycznie wykrywa Spike'a na ekranie (w zdefiniowanym obszarze).
* **Wizualny Timer**: Po wykryciu Spike'a wyświetla znacznik (trójkąt), który zmienia kolory w czasie, pomagając ocenić czas do wybuchu:
    * 🟢 Zielony: Wykryto / bezpiecznie.
    * 🟡 Żółty (po 32s): Ostrzeżenie.
    * 🔴 Czerwony (po 35s): Krytyczny czas.
    * ⚫ Czarny (po 38s): Wybuch nie unikniony.

### 2. Soundboard z Audio Routingiem
* Odtwarza dźwięki `.wav` z folderu `dzwieki`.
* **Dual Audio Output**: Dźwięk jest odtwarzany jednocześnie na:
    * Twoich słuchawkach/głośnikach.
    * Wirtualnym kablu (Line 1 / VB-Audio Cable) – dzięki temu słyszą go inni gracze na voice chacie.
* **Sterowanie Klawiszami**: Uruchamianie dźwięków za pomocą sekwencji dwóch klawiszy NumPad (0-9).
    * Np. wciśnięcie `0` a potem `1` odtworzy plik zaczynający się od `01`.
* Automatyczne wciskanie klawisza push-to-talk (domyślnie `-`) podczas odtwarzania.

### 3. Nakładka (Overlay)
* Niewidoczna dla myszy (`TransparentForMouseEvents`) – możesz klikać "przez" okno.
* Nie zabiera focusu z gry (`WindowDoesNotAcceptFocus`).
* Wyświetla listę dostępnych dźwięków po lewej i prawej stronie ekranu.
* Możliwość ukrycia/pokazania nakładki dodatkowym przyciskiem myszy (X2).

---

## 🛠️ Wymagania

1.  **Python 3.10+**
2.  **VB-Audio Virtual Cable** (lub inny wirtualny kabel audio) – wymagane do puszczania dźwięków na mikrofon.
3.  Zainstalowane biblioteki Python:
    ```bash
    pip install ultralytics opencv-python mss pyaudio sounddevice keyboard pynput PyQt6 numpy
    ```
4.  Plik modelu `best.pt` w głównym katalogu (wytrenowany model YOLO).

---

## ⚙️ Konfiguracja

### Pierwsze uruchomienie
Przy pierwszym uruchomieniu aplikacja poprosi w konsoli o skonfigurowanie urządzeń audio (jeśli nie znajdzie ich automatycznie). Zostanie utworzony plik `ustawienie.txt`.

1.  **Urządzenie wyjściowe (Mic)**: Wybierz indeks urządzenia "CABLE Input" lub "Line 1".
2.  **Głośność (Ty)**: 0.0 - 1.0 (np. 0.5 to 50%).
3.  **Głośność (Inni)**: 0.0 - 1.0.

### Pliki Dźwiękowe
Umieść pliki `.wav` w folderze `dzwieki/`. Nazwy plików muszą zaczynać się od dwucyfrowego kodu, który będzie skrótem klawiszowym, np.:
* `01_witam.wav` -> Uruchamiane sekwencją `NumPad 0` + `NumPad 1`.
* `25_smiech.wav` -> Uruchamiane sekwencją `NumPad 2` + `NumPad 5`.

---

## 🎮 Sterowanie

| Klawisz / Akcja | Funkcja |
| :--- | :--- |
| **NumPad 0-9 (x2)** | Odtworzenie dźwięku (sekwencja dwóch cyfr). |
| **Mouse Button X2** | Pokaż / Ukryj nakładkę. |
| **Klawisz `-`** | Automatyczny Push-To-Talk (symulowany przez skrypt). |

---

## 📂 Struktura Plików

* `BindGui.py` - Główny kod aplikacji.
* `best.pt` - Model AI do detekcji.
* `dzwieki/` - Folder z plikami `.wav`.
* `ustawienie.txt` - Zapisana konfiguracja audio (generowany automatycznie).
* `czestotliwosci uzytwania.txt` - Statystyki użycia dźwięków (generowany automatycznie).

## ⚠️ Uwagi
* Aplikacja korzysta z `mss` do zrzutów ekranu, co jest bardzo szybkie i mało obciążające.
* Upewnij się, że gra działa w trybie **"Okno bez ramek" (Borderless Window)** lub "W oknie", aby nakładka była widoczna nad grą.