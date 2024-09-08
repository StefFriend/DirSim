import cv2
from cvzone.HandTrackingModule import HandDetector

class HandTracker:
    def __init__(self, cap_width, cap_height):
        # Initialize the hand detector
        self.detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
        # Define interaction boxes on the screen
        self.boxes = self._define_boxes(cap_width, cap_height)
        # Initialize debug information string
        self.debug_info = ""

    def _define_boxes(self, cap_width, cap_height):
        # Define the dimensions and positions of interaction boxes
        r_hand_w_ratio, r_hand_h_ratio = 0.2, 0.2
        r_hand_w = int(cap_width * r_hand_w_ratio)
        r_hand_h = int(cap_height * r_hand_h_ratio)
        r_ratio_x = 0.201
        r_hand_x = int(cap_width * (1 - r_ratio_x) - r_hand_w)
        r_hand_y = int(cap_height * 0.1)

        # Return a dictionary of box coordinates
        return {
            "up": (r_hand_x, r_hand_y, r_hand_x + r_hand_w, r_hand_y + r_hand_h),
            "down": (r_hand_x, r_hand_y + r_hand_h * 2, r_hand_x + r_hand_w, r_hand_y + r_hand_h * 3),
            "left": (r_hand_x - r_hand_w, r_hand_y + r_hand_h, r_hand_x, r_hand_y + r_hand_h * 2),
            "right": (r_hand_x + r_hand_w, r_hand_y + r_hand_h, r_hand_x + r_hand_w * 2, r_hand_y + r_hand_h * 2),
        }

    def draw_boxes(self, img, next_expected):
        # Draw interaction boxes on the image
        for box_name, box_coords in self.boxes.items():
            color = (0, 0, 255)  # Default color: red
            if box_name == next_expected:
                color = (0, 255, 0)  # Green for the next expected box
            cv2.rectangle(img, (box_coords[0], box_coords[1]), (box_coords[2], box_coords[3]), color, 2)
            cv2.putText(img, box_name, (box_coords[0], box_coords[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        return img

    def process_hands(self, img, mode):
        # Process hand detections in the image
        hands, img = self.detector.findHands(img, draw=False)
        right_hand_position = None
        left_hand_fingers = None
        touched_boxes = []
        self.debug_info = ""

        if hands:
            for hand in hands:
                if mode == 1:  # Original mode
                    if hand["type"] == "Left":
                        right_hand_position = hand["lmList"][0][:2]
                        self.debug_info += f"Mode 1 - Right hand at {right_hand_position}\n"
                    elif hand["type"] == "Right":
                        left_hand_fingers = {
                            'index': hand["lmList"][8][:2],
                            'pinky': hand["lmList"][20][:2]
                        }
                        self.debug_info += f"Mode 1 - Left hand fingers at {left_hand_fingers}\n"
                else:  # Mode 2
                    if hand["type"] == "Left":
                        index_tip = hand["lmList"][8][:2]
                        self.debug_info += f"Mode 2 - Right hand at {index_tip}\n"
                        for box_name, box_coords in self.boxes.items():
                            if self._is_inside_box(index_tip, box_coords):
                                touched_boxes.append((box_name, hand['type']))
                                self.debug_info += f"Touched {box_name}\n"
                    elif hand["type"] == "Right":
                        left_hand_fingers = {
                            'index': hand["lmList"][8][:2],
                            'pinky': hand["lmList"][20][:2]
                        }
                        self.debug_info += f"Mode 2 - Left hand fingers at {left_hand_fingers}\n"

        return img, right_hand_position, left_hand_fingers, touched_boxes

    @staticmethod
    def _is_inside_box(point, box):
        # Check if a point is inside a given box
        x, y = point
        x1, y1, x2, y2 = box
        return x1 <= x <= x2 and y1 <= y <= y2