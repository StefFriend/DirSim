import cv2
import time
from cvzone.FaceDetectionModule import FaceDetector
from pythonosc.udp_client import SimpleUDPClient
from config import INITIAL_BPM, OSC_SERVER, OSC_PORT
from bpm_calculators import HandSpeedBPMCalculator, PatternBPMCalculator
from hand_tracker import HandTracker
from slider_controller import SliderController

def main():
    window_name = "Hand Tracking BPM and Volume Control"
    osc_client = SimpleUDPClient(OSC_SERVER, OSC_PORT)

    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    hand_tracker = HandTracker(cap_width, cap_height)
    hand_speed_bpm_calculator = HandSpeedBPMCalculator()
    pattern_bpm_calculator = PatternBPMCalculator()
    face_detector = FaceDetector(minDetectionCon=0.6)

    slider1 = SliderController()
    slider2 = SliderController()

    last_bpm_send_time = 0
    last_slider_send_time = 0
    bpm_send_interval = 1
    slider_send_interval = 0.1

    mode = 1  # Start with mode 1
    current_bpm = INITIAL_BPM

    start_message_sent = False  # Flag to track if the start message has been sent

    def send_start_messages():
        osc_client.send_message('/stop', 1)
        osc_client.send_message('/time', '0:00.000')
        osc_client.send_message('/play', 1)
        print("OSC sent - Play message")

    def reset_bpm():
        nonlocal current_bpm
        current_bpm = INITIAL_BPM
        hand_speed_bpm_calculator.current_bpm = INITIAL_BPM
        pattern_bpm_calculator.current_bpm = INITIAL_BPM
        pattern_bpm_calculator.last_valid_bpm = INITIAL_BPM
        osc_client.send_message('/tempo/raw', int(INITIAL_BPM))
        print(f"BPM reset to initial value: {INITIAL_BPM}")

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame")
            break

        img = cv2.flip(img, 1)

        if mode == 2:
            next_expected = pattern_bpm_calculator.get_next_expected()
            img = hand_tracker.draw_boxes(img, next_expected)

        img, right_hand_position, left_hand_fingers, touched_boxes = hand_tracker.process_hands(img, mode)

        # Send start messages if a hand is detected for the first time
        if not start_message_sent and (right_hand_position is not None or left_hand_fingers is not None):
            send_start_messages()
            start_message_sent = True

        current_time = time.time()

        if mode == 1:
            current_bpm = hand_speed_bpm_calculator.update_bpm(right_hand_position)
        else:
            for box_name, hand_type in touched_boxes:
                if pattern_bpm_calculator.add_touch(current_time, box_name):
                    print(f"{hand_type} hand's index finger reached {box_name} box")
            current_bpm = pattern_bpm_calculator.get_bpm()

        if left_hand_fingers:
            slider1.update(left_hand_fingers['index'][1] if 'index' in left_hand_fingers else None, img.shape[0])
            slider2.update(left_hand_fingers['pinky'][1] if 'pinky' in left_hand_fingers else None, img.shape[0])

        slider1.draw(img, 50, (0, 255, 0))  # Green for slider1
        slider2.draw(img, img.shape[1] - 80, (255, 0, 0))  # Blue for slider2

        if current_time - last_bpm_send_time >= bpm_send_interval:
            rounded_bpm = round(current_bpm, 0)
            osc_client.send_message('/tempo/raw', int(rounded_bpm))
            last_bpm_send_time = current_time
            print(f"OSC sent - BPM: {rounded_bpm}")

        if current_time - last_slider_send_time >= slider_send_interval:
            osc_client.send_message('/track/5/volume', slider1.value)
            osc_client.send_message('/track/4/volume', slider2.value)
            last_slider_send_time = current_time
            print(f"OSC sent - Track 5 Volume: {slider1.value:.2f}, Track 4 Volume: {slider2.value:.2f}")

        # Always display BPM, regardless of mode
        cv2.putText(img, f"BPM: {current_bpm:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(img, f"Mode: {mode}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # Add debug information to the image
        debug_lines = hand_tracker.debug_info.split('\n')
        for i, line in enumerate(debug_lines):
            cv2.putText(img, line, (10, 150 + 30*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        img, _ = face_detector.findFaces(img, draw=False)

        cv2.imshow(window_name, img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            mode = 3 - mode  # Switch between 1 and 2
            if mode == 2:
                pattern_bpm_calculator = PatternBPMCalculator()
                pattern_bpm_calculator.current_bpm = current_bpm
                pattern_bpm_calculator.last_valid_bpm = current_bpm
            print(f"Switched to Mode {mode}")
        elif key == ord('s'):
            osc_client.send_message('/stop', 1)
            osc_client.send_message('/time', '0:00.000')
            reset_bpm()
            start_message_sent = False  # Reset the flag to allow hand recognition to send start message again
            print("OSC sent - Stop and Time messages, BPM reset")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()