import pyautogui as pag
import time
import keyboard

def perform_mouse_movement():
    # Get the current position of the mouse
    current_x, current_y = pag.position()
    # Move the mouse in a square pattern
    for i in range(0, 10, 2):
        pag.moveTo(current_x + i, current_y)
        time.sleep(0.1)
        pag.moveTo(current_x + 20, current_y + i)
        time.sleep(0.1)
        pag.moveTo(current_x + 20 - i, current_y + 20)
        time.sleep(0.1)
        pag.moveTo(current_x, current_y + 20 - i)
        time.sleep(0.1)
        pag.moveTo(current_x , current_y)
        time.sleep(0.1)

def move_the_m(waiting,key):
    # Wait for the specified time before moving the mouse
    time.sleep(waiting)
    # Repeat the movement until 'q' is pressed
    while not keyboard.is_pressed('q'):
        # Sleep for 240 seconds in small intervals, checking for 'q' key
        total_sleep = 240
        interval = 0.5
        elapsed = 0
        while elapsed < total_sleep:
            if keyboard.is_pressed(key):
                break
            time.sleep(interval)
            elapsed += interval
        if keyboard.is_pressed(key):
            break
        perform_mouse_movement()
        pag.click()

if __name__ == "__main__":
    move_the_m(10, 'q')
