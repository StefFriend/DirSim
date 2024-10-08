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

        self.osc_lock = threading.Lock()
        self.osc_client = None
        self.osc_message_queue = []

        self.create_osc_client()
        self.osc_thread = threading.Thread(target=self.send_osc_messages, daemon=True)
        self.osc_thread.start()

        self.cap = cv2.VideoCapture(config.get('CAMERA_INDEX', 0))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        cap_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.hand_tracker = HandTracker(cap_width, cap_height)
        self.hand_speed_bpm_calculator = HandSpeedBPMCalculator(
            speed_threshold=config.get('SENSITIVITY', 1000),
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
            max_bpm=config['MAX_BPM'],
            touch_count=config.get('TOUCH_COUNT', 4)
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
        self.program_started = False

        self.debug_mode = config.get('DEBUG_MODE', False)

    def change_camera(self, index):
        if self.cap.isOpened():
            self.cap.release()
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

    def set_debug_mode(self, debug_mode):
        self.debug_mode = debug_mode

    def create_osc_client(self):
        with self.osc_lock:
            self.osc_client = SimpleUDPClient(self.config['OSC_SERVER'], self.config['OSC_PORT'])
        print(f"Created OSC client: {self.config['OSC_SERVER']}:{self.config['OSC_PORT']}")

    def queue_osc_message(self, address, value):
        with self.osc_lock:
            self.osc_message_queue.append((address, value))

    def send_osc_messages(self):
        while True:
            with self.osc_lock:
                if self.osc_message_queue and self.osc_client:
                    address, value = self.osc_message_queue.pop(0)
                    try:
                        self.osc_client.send_message(address, value)
                        print(f"Sent OSC message: {address} {value}")
                    except Exception as e:
                        print(f"Error sending OSC message: {e}")
            time.sleep(0.01)

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
        if key in ['MIN_BPM', 'MAX_BPM', 'INITIAL_BPM', 'SENSITIVITY', 'TOUCH_COUNT']:
            self.config[key] = value
            if key in ['MIN_BPM', 'MAX_BPM', 'INITIAL_BPM']:
                self.hand_speed_bpm_calculator.update_config(key, value)
                self.pattern_bpm_calculator.update_config(key, value)
            elif key == 'SENSITIVITY':
                self.config[key] = value
                self.hand_speed_bpm_calculator.update_config(key, value)
            elif key == 'TOUCH_COUNT':
                self.pattern_bpm_calculator.update_config(key, value)
        elif key in ['OSC_SERVER', 'OSC_PORT']:
            self.config[key] = value
            self.create_osc_client()  # Recreate OSC client with new settings
            print(f"Updated OSC settings: {key} = {value}")
        else:
            self.config[key] = value

    def handle_key(self, key):
        if key == 'm':
            self.mode = 3 - self.mode  # Switch between mode 1 and 2
            if self.mode == 2:
                self.pattern_bpm_calculator = PatternBPMCalculator(
                    window_size=4,
                    initial_bpm=self.current_bpm,
                    min_bpm=self.config['MIN_BPM'],
                    max_bpm=self.config['MAX_BPM'],
                    touch_count=self.config.get('TOUCH_COUNT', 4)
                )
            # We don't reset start_message_sent, hand_detected, or mode2_touch_sequence here anymore
            print(f"Switched to Mode {self.mode}")
        elif key == 's':
            self.queue_osc_message('/stop', 1)
            self.queue_osc_message('/time', '0:00.000')
            self.reset_bpm()
            self.start_message_sent = False
            self.hand_detected = False
            self.mode2_touch_sequence = []
            self.program_started = False
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

            if not self.program_started:
                if self.mode == 1:
                    if right_hand_position is not None or left_hand_fingers is not None:
                        self.hand_detected = True
                        self.send_start_messages()
                        self.program_started = True
                else:  # Mode 2
                    if touched_boxes:
                        for box_name, _ in touched_boxes:
                            if box_name not in self.mode2_touch_sequence:
                                self.mode2_touch_sequence.append(box_name)
                        
                        if len(self.mode2_touch_sequence) == 4 and self.mode2_touch_sequence == self.expected_sequence:
                            self.send_start_messages()
                            self.program_started = True
                            self.mode2_touch_sequence = []
            else:
                # Program has started, handle mode-specific logic
                if self.mode == 1:
                    self.current_bpm = self.hand_speed_bpm_calculator.update_bpm(right_hand_position)
                else:  # Mode 2
                    current_time = time.time()
                    for box_name, hand_type in touched_boxes:
                        if self.pattern_bpm_calculator.add_touch(current_time, box_name):
                            print(f"{hand_type} hand's index finger reached {box_name} box")
                    self.current_bpm = self.pattern_bpm_calculator.get_bpm()

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
                self.queue_osc_message('/track/1/volume', self.slider1.value)
                self.queue_osc_message('/track/2/volume', self.slider2.value)
                self.last_slider_send_time = current_time
                print(f"OSC queued - Track 1 Volume: {self.slider1.value:.2f}, Track 2 Volume: {self.slider2.value:.2f}")

            if self.debug_mode:
                cv2.putText(img, f"BPM: {self.current_bpm:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f"Mode: {self.mode}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                debug_lines = self.hand_tracker.debug_info.split('\n')
                for i, line in enumerate(debug_lines):
                    cv2.putText(img, line, (10, 150 + 30*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            #if self.debug_mode:
            #    img, _ = self.face_detector.findFaces(img, draw=True)
            #else:
            #    img, _ = self.face_detector.findFaces(img, draw=False)

            self.update_frame_callback(img)
            self.update_bpm_callback(self.current_bpm)

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
    
    def release_resources(self):
        if self.cap.isOpened():
            self.cap.release()  # Release the camera


if __name__ == "__main__":
    def dummy_update_bpm(bpm):
        print(f"BPM: {bpm}")

    def dummy_update_frame(frame):
        cv2.imshow("Frame", frame)

    config = {
        'INITIAL_BPM': 36,
        'MIN_BPM': 36,
        'MAX_BPM': 50,
        'OSC_SERVER': "127.0.0.1",
        'OSC_PORT': 57121,
        'SENSITIVITY': 1000,
        'TOUCH_COUNT': 4
    }

    program = MainProgram(dummy_update_bpm, dummy_update_frame, config)
    program.run()
    cv2.destroyAllWindows()