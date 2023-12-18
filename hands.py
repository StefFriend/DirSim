from cvzone.HandTrackingModule import HandDetector
from cvzone.FaceDetectionModule import FaceDetector

import cv2
from pythonosc.udp_client import SimpleUDPClient
import time

# Initialize the OSC client
osc_client = SimpleUDPClient("127.0.0.1", 57120)  # IP address and port

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# print(frame_width,frame_height)

# Initialize the hand detector
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=0, detectionCon=0.8, minTrackCon=0.2)

# Initialize the face detector
face_detector = FaceDetector(minDetectionCon=0.7)


def is_inside_box(point, box):
    x, y = point
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2

# Timers and flags for control
last_time_sent = {"up": 0, "down": 0, "left": 0, "right": 0, "dyn1": 0, "dyn2": 0, "dyn3": 0}
last_face_message_time = 0
face_detected = False
face_absent_duration = 30  # Duration in seconds to wait before sending the stop message

# right hand
r_hand_w = 100
r_hand_h = 100
r_ratio = 0.15
r_hand_l_t = int(cap_width*(1-r_ratio)-r_hand_w)

# left hand
l_hand_ratio = 0.33
l_hand_w = 100
l_hand_h = int(cap_height*l_hand_ratio)

boxes = {
        "up": (r_hand_l_t, 0, r_hand_l_t + r_hand_w, r_hand_h),
        "down": (r_hand_l_t, r_hand_h*2, r_hand_l_t+r_hand_w, r_hand_h+r_hand_h*2),
        "left": (int(r_hand_l_t-r_hand_w*1.5) , r_hand_h, int(r_hand_l_t- 0.5 * r_hand_w), int(r_hand_h*2)),
        "right": (int(r_hand_l_t+r_hand_w*1.5),r_hand_h,int(r_hand_l_t+r_hand_w*2.5),r_hand_h*2),
        "dyn1": (0, 0, l_hand_w, l_hand_h),
        "dyn2": (0, l_hand_h, l_hand_w, l_hand_h*2),
        "dyn3": (0, l_hand_h*2, l_hand_w, l_hand_h*3)
}


while True:
    success, img = cap.read()

    img = cv2.flip(img, 1)

    # Draw the boxes
    for box_name, box_coords in boxes.items():
        cv2.rectangle(img, (box_coords[0], box_coords[1]), (box_coords[2], box_coords[3]), (0, 255, 0), 2)

    # Hands detection
    hands, img = detector.findHands(img, draw=True, flipType=False)

    

    # Hands logic
    if hands:
        for hand in hands:
            center = hand['center']
            hand_type = hand['type']  # 'Right' or 'Left'

            # Define the boxes that should send OSC messages when interacted with by the right hand
            osc_boxes = {
                "Right": ["up", "down", "left", "right"]
                # "Left": []  # No OSC messages for left hand interactions currently
            }

            # Check if the current hand is the right hand and if it interacts with specific boxes
            if hand_type in osc_boxes:
                for box_name in osc_boxes[hand_type]:
                    box_coords = boxes[box_name]
                    if is_inside_box(center, box_coords):
                        current_time = time.time()
                        # Send OSC message if 400ms have passed since the last message for this box
                        if current_time - last_time_sent[box_name] > 0.4:
                            osc_client.send_message("/tapTempo", [])
                            print(f"OSC message sent when {hand_type} hand reached {box_name} box")
                            last_time_sent[box_name] = current_time


    # Face detection
    img, bboxs = face_detector.findFaces(img, draw=True)

    if bboxs:
        # Face is detected
        if not face_detected:
            osc_client.send_message("/play", [])
            print("OSC message sent: /play")
            face_detected = True

        # Update the time the face was last seen
        last_face_seen_time = time.time()

    else:
        # Face is not detected
        if face_detected:
            # Calculate time since the face was last seen
            time_since_last_seen = time.time() - last_face_seen_time if last_face_seen_time else 0
            time_left = max(face_absent_duration - time_since_last_seen, 0)

            # Print the reverse timer
            print(f"Time until /stop is sent: {int(time_left)} seconds", end='\r')

            # Check if the stop message should be sent
            if time_since_last_seen > face_absent_duration:
                osc_client.send_message("/stop", [])
                print("\nOSC message sent: /stop")
                face_detected = False
                last_face_seen_time = None  # Reset the last seen time


    cv2.imshow("Image", img)
    cv2.waitKey(1)
