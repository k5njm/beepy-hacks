import RPi.GPIO as GPIO
import datetime
import os
import time

BUTTON_PIN = 17

SHORT_PRESS_TIME    = 0.5  # Less than 0.5 seconds
REPEAT_TIMEOUT      = 0.5  # Repeat short presses should be within 1s 
MEDIUM_PRESS_TIME   = 2    # Less than 2.0 seconds

SHORT_PRESS_COUNT = 0
BUTTON_PRESS_TIME = 0
BUTTON_RELEASE_TIME = 0
LED_ON         = 0

def my_callback(channel):
    global BUTTON_PRESS_TIME
    global SHORT_PRESS_COUNT
    global BUTTON_RELEASE_TIME

    now = time.time()
    if GPIO.input(channel):

        #print(f'Button Released {now}')
        button_duration = now - BUTTON_PRESS_TIME

        if .01 <= button_duration < SHORT_PRESS_TIME:       # Short Press
            SHORT_PRESS_COUNT += 1
            #print(SHORT_PRESS_COUNT)

        elif SHORT_PRESS_TIME <= button_duration < MEDIUM_PRESS_TIME:   # Medium Press      
            #print('Medium Press')
            os.system('sudo sh -c "echo 255 > /sys/firmware/beepy/led_green"')
            execute_script('medium_press.sh')
        elif button_duration >= MEDIUM_PRESS_TIME:          # Long Press
            #print('Long Press')
            execute_script('long_press.sh')

        BUTTON_RELEASE_TIME = now
    else:
        #print(f'Button Pressed {now}')
        BUTTON_PRESS_TIME = now


def handle_press():
    global SHORT_PRESS_COUNT
    global BUTTON_RELEASE_TIME
    global BUTTON_PRESS_TIME
    global LED_ON

    now = time.time()

    count = 0
    while not GPIO.input(BUTTON_PIN): # Button is being held
        now = time.time()
        if not LED_ON:
            with open('/sys/firmware/beepy/led', 'w') as led:
                led.write('1')
            with open('/sys/firmware/beepy/led_red', 'w') as led:
                led.write('0')
            with open('/sys/firmware/beepy/led_green', 'w') as led:
                led.write('0')
            with open('/sys/firmware/beepy/led_blue', 'w') as led:
                led.write('0')                                                
            LED_ON = 1

        if SHORT_PRESS_COUNT < 2 and now - BUTTON_PRESS_TIME > SHORT_PRESS_TIME < MEDIUM_PRESS_TIME:
            if count < 254:
                count += 0.1
            with open('/sys/firmware/beepy/led_red', 'w') as red:
                red.write(str(round(count)))
            with open('/sys/firmware/beepy/led_green', 'w') as green:
                green.write(str(round(count*.6)))                

        if SHORT_PRESS_COUNT < 2 and now - BUTTON_PRESS_TIME > MEDIUM_PRESS_TIME:
            with open('/sys/firmware/beepy/led_red', 'w') as red:
                red.write("255")
            with open('/sys/firmware/beepy/led_green', 'w') as green:
                green.write("0")              
                    

    if SHORT_PRESS_COUNT >= 3:
        with open('/sys/firmware/beepy/led_green', 'w') as green:
            green.write("0")          
        #print('Short Press (3x)')
        execute_script('short_press_3.sh')

    if SHORT_PRESS_COUNT == 2:
        # 100% red, 64.7% green 
        with open('/sys/firmware/beepy/led_red', 'w') as red:
            red.write("128")
        with open('/sys/firmware/beepy/led_green', 'w') as green:
            green.write("70")
        with open('/sys/firmware/beepy/led_blue', 'w') as blue:
            blue.write("0")                            
        if now - BUTTON_RELEASE_TIME > REPEAT_TIMEOUT:
            #print('Short Press (2x)')
            execute_script('short_press_2.sh')

    if SHORT_PRESS_COUNT == 1:
        with open('/sys/firmware/beepy/led_blue', 'w') as blue:
            blue.write("128")
        if now - BUTTON_RELEASE_TIME > REPEAT_TIMEOUT:
            #print('Short Press (1x)')
            #print(now, BUTTON_RELEASE_TIME, REPEAT_TIMEOUT)
            execute_script('short_press_1.sh')


def execute_script(script_name):
    global SHORT_PRESS_COUNT
    global LED_ON
    global BUTTON_PRESS_TIME
    SHORT_PRESS_COUNT = 0

    script_path = os.path.join(os.path.expanduser('~/bin'), script_name)
    if os.path.exists(script_path):
        os.system(script_path)
    else:
        print(f'Create a script at {script_path} for this action')
    
    time.sleep(0.5)
    with open('/sys/firmware/beepy/led_red', 'w') as led:
        led.write('0')
    with open('/sys/firmware/beepy/led_green', 'w') as led:
        led.write('0')
    with open('/sys/firmware/beepy/led_blue', 'w') as led:
        led.write('0')      
    BUTTON_PRESS_TIME = 0
    LED_ON = 0


try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=my_callback, bouncetime=50) # 50ms for de-bouncing

    while True:
        handle_press()

except KeyboardInterrupt:
    print("Goodbye!")
finally:
    GPIO.cleanup()
