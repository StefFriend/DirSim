from cvzone.HandTrackingModule import HandDetector
import cv2
from pythonosc.udp_client import SimpleUDPClient
import time

# Initialize the OSC client
osc_client = SimpleUDPClient("127.0.0.1", 57120)  # IP address and port

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Initialize the hand detector
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=0, detectionCon=0.8, minTrackCon=0.2)

def is_inside_box(point, box):
    x, y = point
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2

# Timers for each box to control the message sending frequency
last_time_sent = {"up": 0, "down": 0, "left": 0, "right": 0, "dyn1": 0, "dyn2": 0, "dyn3": 0}

while True:
    success, img = cap.read()

    # Define the boxes
    boxes = {
        "up": (650, 0, 1130, 150),
        "down": (650, 570, 1130, 720),
        "left": (500, 150, 650, 570),
        "right": (1130, 150, 1280, 570),
        "dyn1": (0, 0, 150, 720),
        "dyn2": (150, 0, 300, 720),
        "dyn3": (300, 0, 450, 720)
    }

    img = cv2.flip(img, 1)

    # Draw the boxes
    for box_name, box_coords in boxes.items():
        cv2.rectangle(img, (box_coords[0], box_coords[1]), (box_coords[2], box_coords[3]), (0, 255, 0), 2)

    hands, img = detector.findHands(img, draw=True, flipType=False)

    if hands:
        for hand in hands:
            center = hand['center']
            hand_type = hand['type']

            # Define which boxes are allowed for each hand type
            allowed_boxes = {
                "Right": ["up", "down", "left", "right"],
                "Left": ["dyn1", "dyn2", "dyn3"]
            }

            for box_name in allowed_boxes[hand_type]:  # Check allowed boxes for the hand type
                box_coords = boxes[box_name]
                if is_inside_box(center, box_coords):
                    current_time = time.time()
                    # Send OSC message if 400ms have passed since the last message for this box
                    if current_time - last_time_sent[box_name] > 0.4:
                        osc_client.send_message("/tapTempo", [])
                        print(f"OSC message sent for {hand_type} hand at {box_name} box")
                        last_time_sent[box_name] = current_time

    cv2.imshow("Image", img)
    cv2.waitKey(1)
