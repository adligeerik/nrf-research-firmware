from pynput.keyboard import Listener, Key
import time
from check_calc import *

MAX_12B = 2047
MIN_12B = -2048
step = 1
running = True
x = 0
y = 0

def on_press(key):  # The function that's called when a key is pressed
    global x, y, MAX_12B, MIN_12B, step

    if step < 20:
        step += 1

    if key == Key.up:
        y += step
        if y > MAX_12B:
            y = MAX_12B
        print('Up key pressed: ' + str(y))

    elif key == Key.down:
        y -= step
        if y < MIN_12B:
            y = MIN_12B
        print('Down key pressed: '+ str(y))
    
    elif key == Key.left:
        x -= step
        if x < MIN_12B:
            x = MIN_12B
        print('Left key pressed: ' + str(x))
    
    elif key == Key.right:
        x += step
        if x > MAX_12B:
            x = MAX_12B
        print('Right key pressed: ' + str(x))

def on_release(key):  # The function that's called when a key is released
    global x,y,running,step 
    
    step = 1
    if key == Key.up:
        y = 0
        print('Up key de-pressed: ' + str(y))
    elif key == Key.down:
        y = 0
        print('Down key de-pressed: ' + str(y))
    elif key == Key.left:
        x = 0
        print('Left key de-pressed: ' + str(x))
    elif key == Key.right:
        x = 0
        print('Right key de-pressed: ' + str(x))
    elif key == Key.esc:
        print("Esc key de-pressed")
        running = False

def two_comp(val,bits):
    t_val = val
    if val < 0:
        t_val = 2**12 + val 
    return t_val

def build_payload(button,x,y,x_scroll,y_scroll):

    x_pld = hex(two_comp(x,12)).replace('0x','').zfill(3)
    y_pld = hex(two_comp(y,12)).replace('0x','').zfill(3)
    
    xs_pld = hex(two_comp(x_scroll,8)).replace('0x','').zfill(2)
    ys_pld = hex(two_comp(y_scroll,8)).replace('0x','').zfill(2)
    
    pream = '00'
    cmd = 'C2'
    unused = '00'
    button_pld = '00'

    pld = pream + cmd + button_pld + unused + x_pld[1:3] + y_pld[2] + x_pld[0] + y_pld[0:2] + xs_pld + ys_pld
    pld = pld + calc_checksum(pld)
    return pld

def main():
    global running

    listener = Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
    
    while running:
        time.sleep(0.1)
    
    listener.stop()

if __name__ == '__main__':
    main()
