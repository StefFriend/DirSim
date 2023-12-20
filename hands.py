from cvzone.HandTrackingModule import HandDetector
from cvzone.FaceDetectionModule import FaceDetector

import cv2
from pythonosc.udp_client import SimpleUDPClient
import time

# Initialize the OSC client
osc_client = SimpleUDPClient("127.0.0.1", 57120)  # IP address and port

# Initialize the webcam
cap = cv2.VideoCapture(0)
# set size
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# print(frame_width,frame_height)

# Specify the window name and desired size
window_name = "DirSim"


# Initialize the hand detector
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.3)

# Initialize the face detector
face_detector = FaceDetector(minDetectionCon=0.6)


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
r_hand_w_ratio = 0.2
r_hand_h_ratio = 0.2
r_hand_w = int(cap_width*r_hand_w_ratio)
r_hand_h = int(cap_width*r_hand_h_ratio)
r_ratio_x = 0.15
r_ratio_y = 0.15
r_hand_x = int(cap_width*(1-r_ratio_x)-r_hand_w)
# r_hand_y = int(cap_height*r_ratio_y)
r_hand_y = 0

# left hand
l_hand_h_ratio = 0.33
l_hand_w_ratio = 0.15
l_hand_w = int(cap_width*l_hand_w_ratio)
l_hand_h = int(cap_height*l_hand_h_ratio)

boxes = {
        "up": (r_hand_x, r_hand_y, r_hand_x + r_hand_w, r_hand_y+r_hand_h),
        "down": (r_hand_x, r_hand_y+r_hand_h*2, r_hand_x+r_hand_w, r_hand_y+r_hand_h+r_hand_h*2),
        "left": (int(r_hand_x-r_hand_w*1) , r_hand_y+r_hand_h, int(r_hand_x), int(r_hand_y+r_hand_h*2)),
        "right": (int(r_hand_x+r_hand_w*1),r_hand_y+r_hand_h,int(r_hand_x+r_hand_w*2),r_hand_y+r_hand_h*2),
        "dyn1": (0, 0, l_hand_w, cap_height),
        "dyn2": (l_hand_w, 0, l_hand_w*2, cap_height),
        "dyn3": (l_hand_w*2, 0, l_hand_w*3, cap_height)
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

            
            if hands:
                for hand in hands:
                    # Get the list of all 21 landmarks for the hand
                    landmarks = hand['lmList']
                    hand_type = hand['type']  # 'Right' or 'Left'

                    if hand_type in osc_boxes:
                        for box_name in osc_boxes[hand_type]:
                            box_coords = boxes[box_name]
                            for landmark in landmarks:
                                # Extract x and y coordinates from the landmark
                                x, y = landmark[0], landmark[1]
                                if is_inside_box((x, y), box_coords):
                                    current_time = time.time()
                                    # Send OSC message if 400ms have passed since the last message for this box
                                    if current_time - last_time_sent[box_name] > 0.7:
                                        osc_client.send_message("/tapTempo", [])
                                        print(f"OSC message sent when {hand_type} hand's landmark reached {box_name} box")
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


    cv2.imshow(window_name, img)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and destroy all windows when done
cap.release()
cv2.destroyAllWindows()
