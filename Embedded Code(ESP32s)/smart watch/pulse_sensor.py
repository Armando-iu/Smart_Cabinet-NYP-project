from machine import Pin, ADC
from time import sleep, ticks_ms, ticks_diff
import time

class PulseSensor:
    def __init__(self, adc_pin=34, led_pin=2, low_threshold=1800, high_threshold=1900, smoothing_window_size=5, bpm_estimation_interval=15):
        self.adc = ADC(Pin(adc_pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.led = Pin(led_pin, Pin.OUT)

        # Threshold values
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

        # Peak detection variables
        self.previous_signal = 0
        self.peak_detected = False
        self.last_peak_time = 0

        # BPM calculation variables
        self.peak_times = []
        self.bpm_estimation_interval = bpm_estimation_interval  # 
        self.peak_count = 0
        self.start_time = time.ticks_ms()

        # Kalman filter variables
        self.Q = 0.1  # Process noise covariance
        self.R = 0.1  # Measurement noise covariance
        self.X = 0.0  # Value
        self.P = 1.0  # Estimation error covariance
        self.K = 0.0  # Kalman gain

        # Smoothing variables
        self.smoothing_window_size = smoothing_window_size
        self.signal_window = []

        # Peak count variables for 15-second interval BPM calculation
        self.peak_count = 0
        self.start_time = time.ticks_ms()

        # Method switch
        self.use_15sec_method = False

    def kalman_filter(self, value):
        self.P = self.P + self.Q
        self.K = self.P / (self.P + self.R)
        self.X = self.X + self.K * (value - self.X)
        self.P = (1 - self.K) * self.P
        return self.X

    def smooth_signal(self, signal):
        self.signal_window.append(signal)
        if len(self.signal_window) > self.smoothing_window_size:
            self.signal_window.pop(0)
        return sum(self.signal_window) / len(self.signal_window)

    def read_sensor(self):
        return self.adc.read()

    def detect_peaks_and_calculate_bpm(self):
        current_signal = self.read_sensor()  # Read the PulseSensor's value
        smoothed_signal = self.smooth_signal(current_signal)  # Smooth the signal
        filtered_signal = self.kalman_filter(smoothed_signal)  # Apply Kalman filter

        estimated_bpm = 0

        # Check if the signal is within the desired range
        if self.low_threshold < filtered_signal < self.high_threshold:
            if filtered_signal > self.previous_signal:
                self.peak_detected = True
            elif filtered_signal < self.previous_signal and self.peak_detected:
                # A peak is detected
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, self.last_peak_time) > 300:  # Minimum interval to avoid noise
                    self.last_peak_time = current_time
                    self.peak_times.append(current_time)

                    # Remove old peaks outside the estimation window
                    self.peak_times = [t for t in self.peak_times if time.ticks_diff(current_time, t) <= self.bpm_estimation_interval * 1000]

                    # Calculate BPM if there are at least two peaks
                    if len(self.peak_times) > 1:
                        intervals = [time.ticks_diff(self.peak_times[i], self.peak_times[i - 1]) for i in range(1, len(self.peak_times))]
                        avg_interval = sum(intervals) / len(intervals)
                        estimated_bpm = 60000 / avg_interval

                    self.led.on()  # Turn on LED for a heartbeat
                    print(f"Heartbeat detected, estimated BPM: {estimated_bpm:.2f}")
                self.peak_detected = False
            else:
                self.led.off()  # Turn off LED if no heartbeat is detected
        else:
            self.peak_detected = False
            self.led.off()  # Turn off LED if signal is out of range

        # Update previous signal
        self.previous_signal = filtered_signal

        # Print the signal for debugging
        print("Signal:", filtered_signal)

        return estimated_bpm

    # Inside PulseSensor class

    def calculate_bpm_over_15sec(self):
        self.start_time = time.ticks_ms()
        self.peak_count = 0
        while time.ticks_diff(time.ticks_ms(), self.start_time) < 15000:
            current_signal = self.read_sensor()  # Read the PulseSensor's value
            smoothed_signal = self.smooth_signal(current_signal)  # Smooth the signal
            filtered_signal = self.kalman_filter(smoothed_signal)  # Apply Kalman filter
            
            # Check if the signal is within the desired range
            if self.low_threshold < filtered_signal < self.high_threshold:
                if filtered_signal > self.previous_signal:
                    self.peak_detected = True
                elif filtered_signal < self.previous_signal and self.peak_detected:
                    # A peak is detected
                    self.peak_detected = False
                    self.peak_count += 1
                    self.led.on()  # Turn on LED for a heartbeat
                    print("Heartbeat detected")
                else:
                    self.led.off()  # Turn off LED if no heartbeat is detected
            else:
                self.peak_detected = False
                self.led.off()  # Turn off LED if signal is out of range
            
            # Update previous signal
            self.previous_signal = filtered_signal
            
            # Delay for stability
            time.sleep_ms(100)
        
        # Calculate BPM after 15 seconds
        bpm = self.peak_count * 4  # Calculate BPM based on peaks counted
        print(f"BPM: {bpm}")
        
        return bpm





