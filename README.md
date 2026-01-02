# Bindy - Soundboard

**Bindy** to projekt stworzony hobbystycznie, którego głównym celem jest ułatwienie komunikacji głosowej (Soundboard) oraz dostarczenie wizualnych wskazówek w grach (głównie **Valorant**).

Mimo że nakładka graficzna (GUI) została zaprojektowana z myślą o mechanikach Valoranta (np. licznik Spike'a), sam moduł Soundboardu jest uniwersalny i działa w każdym środowisku Windows.

## ⚠️ Cel Projektu

Program ten powstał w celach **edukacyjnych, humorystycznych oraz poprawiających "Quality of Life" podczas rozgrywki**.
**Nie służy do trollowania**, przeszkadzania innym graczom ani łamania zasad fair play. Używaj go odpowiedzialnie, aby poprawić atmosferę w drużynie, a nie ją psuć.

---

## 🚀 Funkcjonalności

1.  **Zaawansowany Soundboard**: Odtwarzanie plików `.wav` bezpośrednio na wejście mikrofonowe (słyszą to inni gracze) oraz na głośniki (słyszysz to Ty).
2.  **System Kombinacji Klawiszy**: Dźwięki wywoływane są sekwencją dwóch klawiszy na klawiaturze numerycznej (Numpad).
3.  **Nakładka (Overlay) GUI**:
    * Przezroczyste okno wyświetlające listę dostępnych dźwięków.
    * Wskaźnik statusu "Spike" (dla gry Valorant) – zmienia kolory w zależności od czasu od detonacji (zielony dużo czasu, żółty mało czasu, czerwony albo teraz albo wcale, czarny brak czasu na rozbrojenie).
4.  **Inteligentne Wykrywanie (OpenCV)**: Automatyczna detekcja ikon na ekranie w celu aktywacji timerów (np. podłożenie bomby).

---

## 🛠️ Wymagania i Instalacja

Aby program działał poprawnie, musisz wykonać poniższe kroki w podanej kolejności.

### 1. Wirtualny Kabel Audio (Wymagane!)
Aby dźwięki były słyszane przez mikrofon w grze/Discordzie, musisz zainstalować wirtualne urządzenie audio.

1.  Pobierz i zainstaluj **VB-CABLE Virtual Audio Device**:
    👉 [https://vb-audio.com/Cable/?gad_campaignid=266017394](https://vb-audio.com/Cable/?gad_campaignid=266017394)
2.  Po instalacji zrestartuj komputer.

### 2. Przygotowanie plików dźwiękowych
Program nie zawiera wbudowanych dźwięków. Musisz dodać je sam.

1.  W folderze z projektem utwórz nowy katalog o nazwie: `dzwieki`.
2.  Wgraj tam swoje pliki dźwiękowe.
3.  **Ważne:** Pliki muszą być w formacie `.wav`.
4.  **Nazewnictwo:** Aby przypisać dźwięk do skrótu, nazwa pliku musi zaczynać się od dwóch cyfr odpowiadających klawiszom Numpad (0-9).
    * *Przykład:* Plik `12witam.wav` zostanie odtworzony po wciśnięciu `Numpad1`, a następnie szybko `Numpad2`.

### 3. Instalacja Bibliotek Python
Upewnij się, że masz zainstalowanego Pythona. Następnie zainstaluj wymagane biblioteki:

```bash
pip install opencv-python numpy mss pynput keyboard pyaudio sounddevice PyQt6