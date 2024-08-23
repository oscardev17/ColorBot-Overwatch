# ================================== #
# This program was created by Oscar  #
# ================================== #

from grabber import *
import time
import dxcam
import keyboard
import serial
import threading
import time

def coolup(cooldown_bool,wait):
    time.sleep(wait)
    cooldown_bool[0] = True

MONITOR_SCALE = 3 # You need to set the FOV (3 recommended). 
serialcomm = serial.Serial('COM3',115200, timeout = 0)
grabber = Grabber()
grabber.find_dimensions(MONITOR_SCALE,1920,1080)
aim_bot_toggle = [True]
aim_bot = False
trigger_bot_toggle = [True]
trigger_bot = False
camera = dxcam.create(device_idx=0, output_idx=0, output_color= "BGRA")
camera.start(region=grabber.dimensions,target_fps=200)
start_time = time.time()

uwu3 = 1
uwu2 = 0

while True:
    og = camera.get_latest_frame()
    frame = grabber.process_frame(og)
    contours = grabber.detect_contours(frame, 100)
    uwu2+= 1
    if(time.time() - start_time) > uwu3:
        uwu = "fps:"+ str(int(uwu2/(time.time() - start_time)))
        print(uwu)
        uwu2 = 0
        start_time = time.time()
    if keyboard.is_pressed('`'):
        if aim_bot_toggle[0] == True:
            aim_bot = not aim_bot
            # print(aim_bot)
            aim_bot_toggle[0] = False
            thread = threading.Thread(target=coolup, args=(aim_bot_toggle,0.2,))
            thread.start()
    if keyboard.is_pressed('alt'):
        if trigger_bot_toggle[0] == True:
            trigger_bot = not trigger_bot
            # print(trigger_bot)
            trigger_bot_toggle[0] = False
            thread = threading.Thread(target=coolup, args=(trigger_bot_toggle,0.2,))
            thread.start()
    if contours:
        try:
            rec, x, y = grabber.compute_centroid(contours)
            if aim_bot:
                data = f"{int(x/4)}:{int(y/4)}"
                serialcomm.write(data.encode())
            if trigger_bot and grabber.on_target(contours):
                serialcomm.write("shoot".encode())
        except:
            print("",end="")