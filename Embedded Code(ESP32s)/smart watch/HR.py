from machine import Pin, I2C, ADC
import ssd1306
import time
from pulse_sensor import PulseSensor


adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)  # Set the attenuation to read a wider range of voltages

MAX_HISTORY = 200
TOTAL_BEATS = 30
HEART = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 1, 1, 0],
    [1, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0],
]
last_y = 0

def refresh(bpm, beat, v, minima, maxima, display):
    global last_y

    display.vline(0, 0, 64, 0)
    display.scroll(-1, 0)  # Scroll left 1 pixel

    if maxima - minima > 0 and 1800 <= v <= 1900:
        # Draw beat line with larger scaling for visibility.
        y = 80 - int(100 * (v - minima) / (maxima - minima))  # Adjust the scaling factor for better visibility
        display.line(125, last_y, 126, y, 1)
        last_y = y

    # Clear top text area.
    display.fill_rect(0, 0, 128, 16, 0)  # Clear the top text area

    if bpm:
        display.text("%d bpm" % bpm, 12, 0)

    # Draw heart if beating.
    if beat:
        for y, row in enumerate(HEART):
            for x, c in enumerate(row):
                display.pixel(x, y, c)

    display.show()

def HR(display,button_pin):
    history = []
    beats = []
    beat = False
    bpm = None
    last_valid_bpm = None

    Hr_sensor = PulseSensor()

    while True:
        button_state = button_pin.value()
        if button_state == 1:
            bpm = Hr_sensor.detect_peaks_and_calculate_bpm()
            v = Hr_sensor.read_sensor()
            raw_data = adc.read()
            history.append(raw_data)

            # Get the tail, up to MAX_HISTORY length
            history = history[-MAX_HISTORY:]

            minima, maxima = 1700, 2000

            if bpm > 0:
                beat = True
                beats.append(time.time())
                # Truncate beats queue to max
                beats = beats[-TOTAL_BEATS:]
                last_valid_bpm = bpm  # Update last valid BPM
            else:
                beat = False
                bpm = last_valid_bpm  # Use last valid BPM if current BPM is zero

            refresh(bpm, beat, v, minima, maxima, display)

        elif button_state == 0:
            break




        