import numpy as np
from collections import deque
import time

class HandSpeedBPMCalculator:
    def __init__(self, speed_threshold=1000, still_threshold=100, dead_zone=80, decrease_rate=0.5, initial_bpm=104, min_bpm=100, max_bpm=125):
        self.speed_threshold = speed_threshold  # Maximum speed considered for BPM calculation
        self.still_threshold = still_threshold  # Speed below which hand is considered still
        self.dead_zone = dead_zone  # Speed range where small movements are ignored
        self.decrease_rate = decrease_rate  # Rate at which BPM decreases when hand is still
        self.current_bpm = initial_bpm  # Current BPM value
        self.min_bpm = min_bpm  # Minimum allowed BPM
        self.max_bpm = max_bpm  # Maximum allowed BPM
        self.last_position = None  # Last recorded hand position
        self.last_time = None  # Time of last update
        self.speeds = deque(maxlen=5)  # Queue to store recent speed values
        self.bpm_history = deque(maxlen=3)  # Queue to store recent BPM values
        self.no_hand_counter = 0  # Counter for frames without detected hand
        self.last_update_time = time.time()  # Time of last BPM update

    def update_config(self, key, value):
        # Update configuration parameters
        if key == 'MIN_BPM':
            self.min_bpm = value
        elif key == 'MAX_BPM':
            self.max_bpm = value
        elif key == 'INITIAL_BPM':
            self.current_bpm = value

    def update_bpm(self, hand_position):
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        
        if hand_position is not None:
            self.no_hand_counter = 0  # Reset no-hand counter
            if self.last_position is not None and self.last_time is not None:
                # Calculate hand speed
                distance = np.linalg.norm(np.array(hand_position) - np.array(self.last_position))
                speed = distance / time_diff if time_diff > 0 else 0
                self.speeds.append(speed)

                avg_speed = np.mean(self.speeds)
                
                if avg_speed < self.still_threshold:
                    # Hand is still, decrease BPM towards minimum
                    bpm_diff = self.current_bpm - self.min_bpm
                    decrease_amount = self.decrease_rate * time_diff
                    if abs(bpm_diff) < decrease_amount:
                        self.current_bpm = self.min_bpm
                    else:
                        self.current_bpm -= np.sign(bpm_diff) * decrease_amount
                    print(f"Hand is still. BPM decreasing to minimum: {self.current_bpm:.2f}")
                elif avg_speed < self.dead_zone:
                    # Small movement, maintain current BPM
                    print(f"Small movement detected. BPM maintained at {self.current_bpm:.2f}")
                else:
                    # Significant movement, update BPM
                    speed_ratio = ((avg_speed - self.dead_zone) / (self.speed_threshold - self.dead_zone)) ** 0.75
                    speed_ratio = max(0, min(speed_ratio, 1))
                    new_bpm = self.min_bpm + speed_ratio * (self.max_bpm - self.min_bpm)
                    
                    self.bpm_history.append(new_bpm)
                    self.current_bpm = np.mean(self.bpm_history)
                    
                    print(f"Avg Speed: {avg_speed:.2f}, Speed Ratio: {speed_ratio:.2f}, Current BPM: {self.current_bpm:.2f}")

            self.last_position = hand_position
            self.last_time = current_time
        else:
            # No hand detected
            self.no_hand_counter += 1
            if self.no_hand_counter > 30:
                print("No hand detected for 1 second. BPM maintained.")
            else:
                print("No hand detected. BPM maintained.")

        self.last_update_time = current_time
        return self.current_bpm

class PatternBPMCalculator:
    def __init__(self, window_size=4, initial_bpm=104, min_bpm=100, max_bpm=125):
        self.window_size = window_size  # Number of touches to consider for BPM calculation
        self.touch_times = deque(maxlen=window_size)  # Queue to store touch times
        self.current_bpm = initial_bpm  # Current BPM value
        self.last_valid_bpm = initial_bpm  # Last valid BPM calculated
        self.min_bpm = min_bpm  # Minimum allowed BPM
        self.max_bpm = max_bpm  # Maximum allowed BPM
        self.expected_pattern = ['down', 'left', 'right', 'up']  # Expected touch pattern
        self.pattern_index = 0  # Current index in the expected pattern

    def update_config(self, key, value):
        # Update configuration parameters
        if key == 'MIN_BPM':
            self.min_bpm = value
        elif key == 'MAX_BPM':
            self.max_bpm = value
        elif key == 'INITIAL_BPM':
            self.current_bpm = value
            self.last_valid_bpm = value

    def add_touch(self, touch_time, box_name):
        # Add a new touch if it matches the expected pattern
        if box_name == self.expected_pattern[self.pattern_index]:
            self.touch_times.append(touch_time)
            self.pattern_index = (self.pattern_index + 1) % len(self.expected_pattern)
            self._calculate_bpm()
            return True
        return False

    def _calculate_bpm(self):
        # Calculate BPM based on touch intervals
        if len(self.touch_times) >= 2:
            intervals = np.diff(self.touch_times)
            avg_interval = np.mean(intervals)
            bpm = 60 / avg_interval

            if self.min_bpm <= bpm <= self.max_bpm:
                self.current_bpm = bpm
                self.last_valid_bpm = bpm
            elif self.last_valid_bpm is not None:
                self.current_bpm = self.last_valid_bpm
        elif self.last_valid_bpm is not None:
            self.current_bpm = self.last_valid_bpm

    def get_bpm(self):
        # Return the current BPM
        return self.current_bpm

    def get_next_expected(self):
        # Return the next expected touch in the pattern
        return self.expected_pattern[self.pattern_index]