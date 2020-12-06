from pynput.keyboard import Listener, Key
import time


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