import cv2
import time
from cvzone.FaceDetectionModule import FaceDetector
from pythonosc.udp_client import SimpleUDPClient
from bpm_calculators import HandSpeedBPMCalculator, PatternBPMCalculator
from hand_tracker import HandTracker
from slider_controller import SliderController

class MainProgram:
    def __init__(self, update_bpm_callback, update_frame_callback, config):
        self.update_bpm_callback = update_bpm_callback
        self.update_frame_callback = update_frame_callback
        self.config = config
        self.running = False

        self.osc_client = SimpleUDPClient(config['OSC_SERVER'], config['OSC_PORT'])

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
            decrease_rate=0.5
        )
        self.pattern_bpm_calculator = PatternBPMCalculator(window_size=4)
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

    def send_start_messages(self):
        self.osc_client.send_message('/stop', 1)
        self.osc_client.send_message('/time', '0:00.000')
        self.osc_client.send_message('/play', 1)
        print("OSC sent - Play message")

    def reset_bpm(self):
        self.current_bpm = self.config['INITIAL_BPM']
        self.hand_speed_bpm_calculator.current_bpm = self.config['INITIAL_BPM']
        self.pattern_bpm_calculator.current_bpm = self.config['INITIAL_BPM']
        self.pattern_bpm_calculator.last_valid_bpm = self.config['INITIAL_BPM']
        self.osc_client.send_message('/tempo/raw', int(self.config['INITIAL_BPM']))
        print(f"BPM reset to initial value: {self.config['INITIAL_BPM']}")

    def handle_key(self, key):
        if key == 'm':
            self.mode = 3 - self.mode
            if self.mode == 2:
                self.pattern_bpm_calculator = PatternBPMCalculator()
                self.pattern_bpm_calculator.current_bpm = self.current_bpm
                self.pattern_bpm_calculator.last_valid_bpm = self.current_bpm
            print(f"Switched to Mode {self.mode}")
        elif key == 's':
            self.osc_client.send_message('/stop', 1)
            self.osc_client.send_message('/time', '0:00.000')
            self.reset_bpm()
            self.start_message_sent = False
            print("OSC sent - Stop and Time messages, BPM reset")

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

            if not self.start_message_sent and (right_hand_position is not None or left_hand_fingers is not None):
                self.send_start_messages()
                self.start_message_sent = True

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
                self.osc_client.send_message('/tempo/raw', int(rounded_bpm))
                self.last_bpm_send_time = current_time
                print(f"OSC sent - BPM: {rounded_bpm}")

            if current_time - self.last_slider_send_time >= self.slider_send_interval:
                self.osc_client.send_message('/track/5/volume', self.slider1.value)
                self.osc_client.send_message('/track/4/volume', self.slider2.value)
                self.last_slider_send_time = current_time
                print(f"OSC sent - Track 5 Volume: {self.slider1.value:.2f}, Track 4 Volume: {self.slider2.value:.2f}")

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