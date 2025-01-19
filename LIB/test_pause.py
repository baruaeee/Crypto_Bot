from pynput import keyboard
import time

paused = False

def on_press(key):
    global paused
    if key == keyboard.Key.space:
        paused = not paused
        print("Script paused" if paused else "Script resumed")

listener = keyboard.Listener(on_press=on_press)
listener.start()

while True:
    if not paused:
        print("Running script ...")
        time.sleep(1)
