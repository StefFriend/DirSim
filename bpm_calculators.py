import numpy as np
import time
from collections import deque
from config import INITIAL_BPM, MIN_BPM, MAX_BPM

class HandSpeedBPMCalculator:
    def __init__(self, speed_threshold=1000, still_threshold=100, dead_zone=80, decrease_rate=0.5):
        self.current_bpm = INITIAL_BPM
        self.speed_threshold = speed_threshold
        self.still_threshold = still_threshold
        self.dead_zone = dead_zone
        self.decrease_rate = decrease_rate
        self.last_position = None
        self.last_time = None
        self.speeds = deque(maxlen=5)
        self.bpm_history = deque(maxlen=3)
        self.no_hand_counter = 0
        self.last_update_time = time.time()

    def update_bpm(self, hand_position):
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        
        if hand_position is not None:
            self.no_hand_counter = 0
            if self.last_position is not None and self.last_time is not None:
                distance = np.linalg.norm(np.array(hand_position) - np.array(self.last_position))
                speed = distance / time_diff if time_diff > 0 else 0
                self.speeds.append(speed)

                avg_speed = np.mean(self.speeds)
                
                if avg_speed < self.still_threshold:
                    bpm_diff = self.current_bpm - INITIAL_BPM
                    decrease_amount = self.decrease_rate * time_diff
                    if abs(bpm_diff) < decrease_amount:
                        self.current_bpm = INITIAL_BPM
                    else:
                        self.current_bpm -= np.sign(bpm_diff) * decrease_amount
                    print(f"Hand is still. BPM decreasing to initial: {self.current_bpm:.2f}")
                elif avg_speed < self.dead_zone:
                    print(f"Small movement detected. BPM maintained at {self.current_bpm:.2f}")
                else:
                    speed_ratio = ((avg_speed - self.dead_zone) / (self.speed_threshold - self.dead_zone)) ** 0.75
                    speed_ratio = max(0, min(speed_ratio, 1))
                    new_bpm = MIN_BPM + speed_ratio * (MAX_BPM - MIN_BPM)
                    
                    self.bpm_history.append(new_bpm)
                    self.current_bpm = np.mean(self.bpm_history)
                    
                    print(f"Avg Speed: {avg_speed:.2f}, Speed Ratio: {speed_ratio:.2f}, Current BPM: {self.current_bpm:.2f}")

            self.last_position = hand_position
            self.last_time = current_time
        else:
            self.no_hand_counter += 1
            if self.no_hand_counter > 30:
                print("No hand detected for 1 second. BPM maintained.")
            else:
                print("No hand detected. BPM maintained.")

        self.last_update_time = current_time
        return self.current_bpm

class PatternBPMCalculator:
    def __init__(self, window_size=4):
        self.window_size = window_size
        self.touch_times = deque(maxlen=window_size)
        self.current_bpm = INITIAL_BPM
        self.last_valid_bpm = INITIAL_BPM
        self.expected_pattern = ['down', 'left', 'right', 'up']
        self.pattern_index = 0

    def add_touch(self, touch_time, box_name):
        if box_name == self.expected_pattern[self.pattern_index]:
            self.touch_times.append(touch_time)
            self.pattern_index = (self.pattern_index + 1) % len(self.expected_pattern)
            self._calculate_bpm()
            return True
        return False

    def _calculate_bpm(self):
        if len(self.touch_times) >= 2:
            intervals = np.diff(self.touch_times)
            avg_interval = np.mean(intervals)
            bpm = 60 / avg_interval

            if MIN_BPM <= bpm <= MAX_BPM:
                self.current_bpm = bpm
                self.last_valid_bpm = bpm
            elif self.last_valid_bpm is not None:
                self.current_bpm = self.last_valid_bpm
        elif self.last_valid_bpm is not None:
            self.current_bpm = self.last_valid_bpm

    def get_bpm(self):
        return self.current_bpm

    def get_next_expected(self):
        return self.expected_pattern[self.pattern_index]