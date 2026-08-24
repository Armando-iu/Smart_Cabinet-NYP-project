from machine import Pin, PWM, I2C, Timer, ADC
from time import sleep
import ssd1306
import HR
import TEMP
import framebuf





temp_data = [
                    0b00000011, 0b00000000,
                    0b00000100, 0b10011000,
                    0b00000100, 0b10000000,
                    0b00000100, 0b10011100,
                    0b00000100, 0b10000000,
                    0b00000100, 0b10010000,
                    0b00000100, 0b10000000,
                    0b00000100, 0b10011100,
                    0b00000100, 0b10000000,
                    0b00000100, 0b10011000,
                    0b00000100, 0b10000000,
                    0b00001000,	0b01000000,
                    0b00010000,	0b00100000,
                    0b00100000,	0b00010000,
                    0b00100000,	0b00010000,
                    0b00100000,	0b00010000,
                    0b00100000,	0b00010000,
                    0b00010000,	0b00100000,
                    0b00001000,	0b01000000,
                    0b00000111,	0b10000000,
                    
                    
    ]

def TEMP(display, button_pin, temp):
            display.fill(0)
            buffer = bytearray(temp_data)
            fb = framebuf.FrameBuffer(buffer, 16, 20, framebuf.MONO_HLSB)
            display.blit(fb, 49, 17)  # Adjust coordinates as needed for centering
            temperature = temp.read_object_temp()
            display.text("{:.2f}C".format(temperature), 52, 47, 1) 
            display.show()
            sleep(1)
 

