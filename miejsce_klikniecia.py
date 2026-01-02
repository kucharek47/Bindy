from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Kliknięcie: {button} na pozycji ({x}, {y})")

with mouse.Listener(on_click=on_click) as listener:
    print("Nasłuchiwanie kliknięć myszy... (naciśnij Ctrl+C, aby zakończyć)")
    listener.join()
