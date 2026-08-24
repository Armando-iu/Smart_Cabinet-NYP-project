from machine import Pin , PWM , TouchPad
import time
from cabinet.hx711 import HX711
from cabinet import wifi
from cabinet import sock
import _thread
import neopixel

'''
    In this program 
    - cap_touch_handler is not intertwined with other code. 
    - the button interrupt(func name: handle interrupt ), reqS_to_sendS and the main program are all connected:
        ideal output:
        Door Closed to Door open:
            press button -> reads weight -> send weight to server -> door or motor opens
        Door open to Door closed:
            press button -> close door or motor -> opens LED strips -> read and send weight to server
'''

WIFI_SSID = "TP-Link_66EC"
WIFI_PASS = "34252857"
SERVER_IP = '192.168.0.101'
SERVER_PORT = 5001
NO_OF_LED = 5

def handle_interrupt(pin):
    '''
        FYI:
            - The button requires a capacitor because it is very inconsistent without it
                - As in it will affect the chromatic glass's gpio 
    '''
    global door_open , send_info, lastDebounce
    current = time.ticks_ms()
    if time.ticks_diff(current, lastDebounce) <= 1500:
        print("Exiting interrupt")
        return
    time.sleep_ms(50)  # Short delay to filter out noise
    lastDebounce = current
    if btn.value() == 0:  # Check if the button is still pressed. for debounce
        door_open = not door_open
        send_info = True
        print(f"button {door_open}") 
        

def reqS_to_sendS(client_socket):
    global send_msg
    '''
    - in order to not overload the server, the server will always prompt clients first to send their info. not the other way around
    - all listeners are in this thread
        - This is to prevent listeners to wait indefinetly because the order of which the info was sent was wrong
    - to close the LEDs you could only do that from the server side by sending b'lof'
        - This is because u would only close it if the camera has taken a picture and only the server and the esp32 cam knows that.
    - The msg send to client is usually only 3 letters long
        - Hence "lof" and "img"(from esp32 cam) 
    '''
    while True:
        req_server = client_socket.recv(35)
        print(f"requested {req_server}")
        if req_server == b"lof": # request to close lights
            led_rgb_setter(led_strip  , NO_OF_LED , 0 , 0 ,0)

        if b"send" in req_server:
            send_msg = True

def send_weight(weight_sens , state):
    global send_msg
    '''
    - sending can only be in utf-8 or base64
    - I made a pretty weird protocol that looks like:
        https://www.canva.com/design/DAGJTyrvH_w/cjLpcchwf4Gd9K_r6uydag/edit?utm_content=DAGJTyrvH_w&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton
    - So to ensure there is always space for data packets to come into the server
    - However, u dont need to use this protocol to send information to the server
    
    Note:
        - the last time I checked, Sanjeev's smartwatch does not follow this convenient 
        - if i am not wrong it does not have a size declaration
    '''
    weight = float(weight_sens.read_average(times = 50)) * m / 10 #reads and gives average of 50 readings. based on trial and error, c is not used as it makes very innacurate readings and /10 makes it into grams
    print(f"weight {weight}")
    weight = str(weight).encode("utf-8") 
    client_socket.send(b"size-{}".format(len(weight))) # size declaration.
    while send_msg == False:
        continue
    weight = f"{state}-".encode("utf-8") + weight # declare what state it is and the weight. i.e. bfr-100
    client_socket.send(weight)
    send_msg = False

def led_rgb_setter(led_strip  , NO_OF_LED , r , g ,b):
    for led in range(NO_OF_LED):
        led_strip[led] = (r , g ,b) #loop throgh all the LEDs and give them the saem rgb value
    # Write values to LEDs
    led_strip.write()

def cap_touch_handler(glass ,touch_pin ):
    start_touch = time.time() - 5
    while True:
        touch_value = touch_pin.read()
        if touch_value < 90: # when one's hand is present
            start_touch = time.time()
            glass.off() 
        elif touch_value >= 90 and time.time() - start_touch > 5: # purpose: to not close automatically after 5s if one is touching the "capactive touch"(aluminium foil) .first half for clarity of what is the threshold of not touched
            glass.on()
        time.sleep(0.1)

def cali_weight(weight_sens , EMPTY_WEIGHT , CALI_WEIGHT):
    '''
        Idea:
            - the weight linearly increases/decreases (like a y = mx + c graph)
            - hence we can roughly know the ratio between loadcell reading and actual weight
    '''
    cali_go = True
    init_weight = 0
    const_weight = 0
    m =0
    c =0

    while cali_go:
        start_cali = input("cali: ")
        if start_cali == "e":
            init_weight = float(weight_sens.read_average(times = 50)) 
            print(f"init {init_weight}")
            print("empty done")
        if start_cali == "c":
            const_weight = float(weight_sens.read_average(times = 50))
            print(f"init {const_weight}")
            print("stuff in done")
        if start_cali == "ok":
            m = (CALI_WEIGHT - EMPTY_WEIGHT)/(const_weight - init_weight)
            c = init_weight
            print(m)
            cali_go = False
            # pure weight will be y = m * x where x is ur reading
    return m , c # based on trial and error c is not used as it is innacurate
    
door_open = False
send_info = False
send_msg = False
lastDebounce = time.ticks_ms()

# sensor and actuator initialisers
weight_sens = HX711(dout=26, pd_sck=27) # PD_SCK = digital out, Dout = digital in 
weight_sens.set_scale(10) 
weight_sens.tare()
motor = PWM(Pin(14) , freq = 50) 
btn = Pin(23 , Pin.IN) # external pullup, does work
led_pin = Pin(15 , Pin.OUT)
led_strip = neopixel.NeoPixel(led_pin, NO_OF_LED)
glass = Pin(17, Pin.OUT)
touch_pin = TouchPad(Pin(4))

EMPTY_WEIGHT = 140
CALI_WEIGHT = 481

m , c = cali_weight(weight_sens , EMPTY_WEIGHT , CALI_WEIGHT)  

_thread.start_new_thread(cap_touch_handler , (glass ,touch_pin,))
wifi.conn_wifi(WIFI_SSID , WIFI_PASS)
client_socket = sock._init(SERVER_IP , SERVER_PORT , "cab")
_thread.start_new_thread(reqS_to_sendS , (client_socket,))

btn.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)

motor.duty(30)# close
led_rgb_setter(led_strip  , NO_OF_LED , 0 , 0 ,0)#close all LEDs

print("start")
while True:
  if send_info == True and door_open:
    print(f"finish debouncing door open {door_open}")
    send_weight(weight_sens , "bfr")
    motor.duty(80)# open
    send_info = False
    print("done")
    
  elif send_info and not door_open:
    motor.duty(30) # close
    print(f"finish debouncing door open {door_open}")
    led_rgb_setter(led_strip  , NO_OF_LED , 255 , 255 ,255) #light up all LEDs
    time.sleep(5)
    print("open lights")
    send_weight(weight_sens, "aft")
    send_info = False
    print("done")