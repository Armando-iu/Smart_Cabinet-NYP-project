from machine import Pin, I2C, ADC, Timer
from time import sleep
import ssd1306
import mlx90614 as mlx
import socket
import network
import _thread
from pulse_sensor import PulseSensor
import HR
import TEMP
import page_1

# Potentiometer setup
pot_pin = ADC(Pin(33))
pot_pin.atten(ADC.ATTN_11DB)
pot_pin.width(ADC.WIDTH_12BIT)

# Button setup
button_pin = Pin(25, Pin.IN, Pin.PULL_UP)

# OLED setup
i2c = I2C(sda=Pin(21), scl=Pin(22), freq=100000)
display = ssd1306.SSD1306_I2C(128, 64, i2c)
temp_sensor = mlx.MLX90614(i2c)

# Pulse Sensor setup
Hr_sensor = PulseSensor()

temp_sensor = mlx.MLX90614(i2c)

# WLAN setup
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
WIFI_SSID = "MFDAB Wifi"
WIFI_PASS = "SANJEEV1303"

# Socket Configuration
SERVER_IP = "192.168.18.2"  # Server IP
SERVER_PORT = 5001  # Server Port
s = None  # Socket object

def connect_wifi():
    sta_if.connect(WIFI_SSID, WIFI_PASS)
    while not sta_if.isconnected():
        sleep(1)
    print('Connected to Wi-Fi with IP:', sta_if.ifconfig()[0])


def server_comms(s):
    while True:
        try:
            data = s.recv(1024)  # <8 = ok
            if data == b"bpm":
                bpm_value = Hr_sensor.calculate_bpm_over_15sec()
                temperature = temp_sensor.read_object_temp()  # Correct way to read temperature
                s.send(f"{bpm_value:.2f},bpm".encode("utf-8"))
                s.send(f"{temperature:.2f},temp".encode("utf-8"))
        except OSError as e:
            print("Socket error:", e)
            # Handle the error as needed, e.g., reconnect or continue

def main_loop():
    while True:
        pot_value = pot_pin.read()
        button_state = button_pin.value()

        if pot_value == 0:
            page_1.select(3, 3)
                
        elif pot_value <= 1024:
            page_1.select(0, 0)
            if button_state == 0:
                sleep(0.5)
                HR.HR(display, button_pin)  # Pass display and button_pin to HR.HR
                page_1.select(3, 3)
                sleep(1)
                    
        elif pot_value <= 2048:
            page_1.select(1, 0)
                
        elif pot_value <= 3072:
            page_1.select(0, 1)
            if button_state == 0:
                sleep(0.2)
                while True:
                    button_state = button_pin.value()
                    if button_state == 1:
                        sleep(0.5)
                        TEMP.TEMP(display, button_pin, temp)
                        continue
                    elif button_state == 0:
                        break
                page_1.select(3, 3)
                sleep(1)
                    
        elif pot_value <= 4096:
            page_1.select(1, 1)

# Start main loop and server communications
connect_wifi() 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, SERVER_PORT))
print('Connected to server')
s.send(b"new~wch")

_thread.start_new_thread(server_comms, (s,))
main_loop()
