import cv2
import time
from cvzone.FaceDetectionModule import FaceDetector
from pythonosc.udp_client import SimpleUDPClient
from bpm_calculators import HandSpeedBPMCalculator, PatternBPMCalculator
from hand_tracker import HandTracker
from slider_controller import SliderController
import threading

class MainProgram:
    def __init__(self, update_bpm_callback, update_frame_callback, config):
        self.update_bpm_callback = update_bpm_callback
        self.update_frame_callback = update_frame_callback
        self.config = config
        self.running = False

        self.osc_client = SimpleUDPClient(config['OSC_SERVER'], config['OSC_PORT'])
        self.osc_message_queue = []
        self.osc_thread = threading.Thread(target=self.send_osc_messages, daemon=True)
        self.osc_thread.start()

        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        cap_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.hand_tracker = HandTracker(cap_width, cap_height)
        self.hand_speed_bpm_calculator = HandSpeedBPMCalculator(
            speed_threshold=1000,
            still_threshold=100,
            dead_zone=80,
            decrease_rate=0.5,
            initial_bpm=config['INITIAL_BPM'],
            min_bpm=config['MIN_BPM'],
            max_bpm=config['MAX_BPM']
        )
        self.pattern_bpm_calculator = PatternBPMCalculator(
            window_size=4,
            initial_bpm=config['INITIAL_BPM'],
            min_bpm=config['MIN_BPM'],
            max_bpm=config['MAX_BPM']
        )
        self.face_detector = FaceDetector(minDetectionCon=0.6)

        self.slider1 = SliderController()
        self.slider2 = SliderController()

        self.last_bpm_send_time = 0
        self.last_slider_send_time = 0
        self.bpm_send_interval = 1
        self.slider_send_interval = 0.1

        self.mode = 1
        self.current_bpm = config['INITIAL_BPM']

        self.start_message_sent = False
        self.hand_detected = False
        self.mode2_touch_sequence = []
        self.expected_sequence = ['down', 'left', 'right', 'up']

    def queue_osc_message(self, address, value):
        self.osc_message_queue.append((address, value))

    def send_osc_messages(self):
        while True:
            if self.osc_message_queue:
                address, value = self.osc_message_queue.pop(0)
                self.osc_client.send_message(address, value)
                time.sleep(0.01)  # Small delay between messages
            else:
                time.sleep(0.01)  # Sleep to prevent busy-waiting

    def send_start_messages(self):
        self.queue_osc_message('/stop', 1)
        self.queue_osc_message('/time', '0:00.000')
        self.queue_osc_message('/play', 1)
        print("OSC messages queued - Play message")
        self.start_message_sent = True

    def reset_bpm(self):
        self.current_bpm = self.config['INITIAL_BPM']
        self.hand_speed_bpm_calculator.update_config('INITIAL_BPM', self.config['INITIAL_BPM'])
        self.pattern_bpm_calculator.update_config('INITIAL_BPM', self.config['INITIAL_BPM'])
        self.queue_osc_message('/tempo/raw', int(self.config['INITIAL_BPM']))
        print(f"BPM reset to initial value: {self.config['INITIAL_BPM']}")

    def update_config(self, key, value):
        if key == 'MIN_BPM':
            if value <= self.config['MAX_BPM']:
                self.config[key] = value
                self.hand_speed_bpm_calculator.update_config(key, value)
                self.pattern_bpm_calculator.update_config(key, value)
            else:
                print(f"Warning: MIN_BPM ({value}) cannot be greater than MAX_BPM ({self.config['MAX_BPM']})")
        elif key == 'MAX_BPM':
            if value >= self.config['MIN_BPM']:
                self.config[key] = value
                self.hand_speed_bpm_calculator.update_config(key, value)
                self.pattern_bpm_calculator.update_config(key, value)
            else:
                print(f"Warning: MAX_BPM ({value}) cannot be less than MIN_BPM ({self.config['MIN_BPM']})")
        elif key == 'INITIAL_BPM':
            if self.config['MIN_BPM'] <= value <= self.config['MAX_BPM']:
                self.config[key] = value
                self.reset_bpm()
            else:
                print(f"Warning: INITIAL_BPM ({value}) must be between MIN_BPM ({self.config['MIN_BPM']}) and MAX_BPM ({self.config['MAX_BPM']})")
        else:
            self.config[key] = value

    def handle_key(self, key):
        if key == 'm':
            self.mode = 3 - self.mode
            if self.mode == 2:
                self.pattern_bpm_calculator = PatternBPMCalculator(
                    window_size=4,
                    initial_bpm=self.current_bpm,
                    min_bpm=self.config['MIN_BPM'],
                    max_bpm=self.config['MAX_BPM']
                )
            self.start_message_sent = False
            self.hand_detected = False
            self.mode2_touch_sequence = []
            print(f"Switched to Mode {self.mode}")
        elif key == 's':
            self.queue_osc_message('/stop', 1)
            self.queue_osc_message('/time', '0:00.000')
            self.reset_bpm()
            self.start_message_sent = False
            self.hand_detected = False
            self.mode2_touch_sequence = []
            print("OSC messages queued - Stop and Time messages, BPM reset")

    def run(self):
        self.running = True
        while self.running:
            success, img = self.cap.read()
            if not success:
                print("Failed to grab frame")
                break

            img = cv2.flip(img, 1)

            if self.mode == 2:
                next_expected = self.pattern_bpm_calculator.get_next_expected()
                img = self.hand_tracker.draw_boxes(img, next_expected)

            img, right_hand_position, left_hand_fingers, touched_boxes = self.hand_tracker.process_hands(img, self.mode)

            # Handle start message logic
            if self.mode == 1:
                if (right_hand_position is not None or left_hand_fingers is not None) and not self.start_message_sent:
                    self.hand_detected = True
                    self.send_start_messages()
            else:  # Mode 2
                if touched_boxes:
                    for box_name, _ in touched_boxes:
                        if box_name not in self.mode2_touch_sequence:
                            self.mode2_touch_sequence.append(box_name)
                    
                    if len(self.mode2_touch_sequence) == 4 and self.mode2_touch_sequence == self.expected_sequence:
                        if not self.start_message_sent:
                            self.send_start_messages()
                        self.mode2_touch_sequence = []  # Reset the sequence after sending start messages

            current_time = time.time()

            if self.mode == 1:
                self.current_bpm = self.hand_speed_bpm_calculator.update_bpm(right_hand_position)
            else:
                for box_name, hand_type in touched_boxes:
                    if self.pattern_bpm_calculator.add_touch(current_time, box_name):
                        print(f"{hand_type} hand's index finger reached {box_name} box")
                self.current_bpm = self.pattern_bpm_calculator.get_bpm()

            if left_hand_fingers:
                self.slider1.update(left_hand_fingers['index'][1] if 'index' in left_hand_fingers else None, img.shape[0])
                self.slider2.update(left_hand_fingers['pinky'][1] if 'pinky' in left_hand_fingers else None, img.shape[0])

            self.slider1.draw(img, 50, (0, 255, 0))  # Green for slider1
            self.slider2.draw(img, img.shape[1] - 80, (255, 0, 0))  # Blue for slider2

            if current_time - self.last_bpm_send_time >= self.bpm_send_interval:
                rounded_bpm = round(self.current_bpm, 0)
                self.queue_osc_message('/tempo/raw', int(rounded_bpm))
                self.last_bpm_send_time = current_time
                print(f"OSC queued - BPM: {rounded_bpm}")

            if current_time - self.last_slider_send_time >= self.slider_send_interval:
                self.queue_osc_message('/track/5/volume', self.slider1.value)
                self.queue_osc_message('/track/4/volume', self.slider2.value)
                self.last_slider_send_time = current_time
                print(f"OSC queued - Track 5 Volume: {self.slider1.value:.2f}, Track 4 Volume: {self.slider2.value:.2f}")

            cv2.putText(img, f"BPM: {self.current_bpm:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img, f"Mode: {self.mode}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            debug_lines = self.hand_tracker.debug_info.split('\n')
            for i, line in enumerate(debug_lines):
                cv2.putText(img, line, (10, 150 + 30*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            img, _ = self.face_detector.findFaces(img, draw=False)

            self.update_frame_callback(img)
            self.update_bpm_callback(self.current_bpm)

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    def dummy_update_bpm(bpm):
        print(f"BPM: {bpm}")

    def dummy_update_frame(frame):
        cv2.imshow("Frame", frame)

    config = {
        'INITIAL_BPM': 104,
        'MIN_BPM': 100,
        'MAX_BPM': 125,
        'OSC_SERVER': "127.0.0.1",
        'OSC_PORT': 57121
    }

    program = MainProgram(dummy_update_bpm, dummy_update_frame, config)
    program.run()
    cv2.destroyAllWindows()