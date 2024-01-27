import time
import pyautogui
import keyboard

timeInterval = float(3)
moveInterval = float(3)
while moveInterval >= 0:
    print(f'please move mouse to specific place in {moveInterval}')
    time.sleep(1)
    moveInterval -= 1

position = pyautogui.position()
while True:
    pyautogui.click(position[0], position[1])
    time.sleep(timeInterval)
    if keyboard.is_pressed('esc') or keyboard.is_pressed('q') :
        break


