import cv2
import numpy as np
import time
import mediapipe as mp

def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(int)
    fx, fy = flow[y, x].T

    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(img_bgr, lines, False, (0, 255, 0))
    for (x1, y1), _ in lines:
        cv2.circle(img_bgr, (x1, y1), 1, (0, 255, 0), -1)
    return img_bgr

def calculate_bpm(flow, scaling_factor=30):
    magnitudes = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
    avg_magnitude = np.mean(magnitudes)
    return avg_magnitude * scaling_factor

# MediaPipe Part
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

# Initialize webcam capture
cap = cv2.VideoCapture(1)
ret, prev_frame = cap.read()

frame_width = prev_frame.shape[1]
half_width = frame_width // 2

prev_gray = cv2.cvtColor(prev_frame[:, :half_width], cv2.COLOR_BGR2GRAY)

bpm_values = []
last_bpm = 0  
start_time = time.time()

value1 = 30
value2 = 30
min_value = 30
max_value = 127
prev_y_position = None  # For tracking vertical hand movement


def is_finger_open(finger_tip, finger_dip, finger_pip, finger_mcp):
    # Logic to check if a finger is open
    return finger_tip.y < finger_dip.y < finger_pip.y and finger_tip.y < finger_mcp.y

def is_thumb_open(thumb_tip, thumb_ip, thumb_mcp):
    # Logic to check if the thumb is open
    return thumb_tip.x < thumb_ip.x and thumb_tip.x < thumb_mcp.x

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Left half processing
    half_frame = frame[:, :half_width]
    gray = cv2.cvtColor(half_frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 120, 30, 5, 5, 1.2, 0)
    bpm = calculate_bpm(flow)
    
    if abs(bpm - last_bpm) > 10:
        bpm_values.append(bpm)
        last_bpm = bpm
    
    flow_overlay_half = draw_flow(gray, flow)
    left_half_processed = flow_overlay_half.copy()
    prev_gray = gray.copy()

    # Right half processing
    right_half_frame = frame[:, half_width:]
    right_half_frame_rgb = cv2.cvtColor(right_half_frame, cv2.COLOR_BGR2RGB)
    right_half_results = hands.process(right_half_frame_rgb)

    if right_half_results.multi_hand_landmarks:
        for hand_landmarks in right_half_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(right_half_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract landmarks for fingers
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
            thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]

            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_dip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP]
            index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
            index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]


            # Check hand poses
            thumb_open = is_thumb_open(thumb_tip, thumb_ip, thumb_mcp)
            index_open = is_finger_open(index_tip, index_dip, index_pip, index_mcp)
            

            all_fingers_closed = not any([thumb_open, index_open, ...])  # Check if all fingers are closed
            all_fingers_open = all([thumb_open, index_open, ...])  # Check if all fingers are open

            # Track vertical hand movement
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            current_y_position = wrist.y

            if prev_y_position is not None:
                movement_speed = current_y_position - prev_y_position

                # Adjust value1 and value2 based on hand pose and movement
                if index_open and all([not thumb_open, ...]):  # Only index finger open
                    if movement_speed < 0:  # Hand moving up
                        value1 = min(value1 + 1, max_value)
                    elif movement_speed > 0:  # Hand moving down
                        value1 = max(value1 - 1, min_value)
                elif all_fingers_open:
                    if movement_speed < 0:  # Hand moving up
                        value2 = min(value2 + 1, max_value)
                    elif movement_speed > 0:  # Hand moving down
                        value2 = max(value2 - 1, min_value)

            prev_y_position = current_y_position

            print(f"Value1: {value1}, Value2: {value2}")


    # Display values on the screen
    cv2.putText(right_half_frame, f"Value1: {value1}, Value2: {value2}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)



    # Display results
    combined_frame = np.concatenate((left_half_processed, right_half_frame), axis=1)
    cv2.imshow('DirSim', combined_frame)

    if time.time() - start_time >= 1:
        if bpm_values:
            mean_bpm = np.mean(bpm_values)
            print(f"Estimated BPM: {mean_bpm}")
        else:
            print("No BPM change detected")
        bpm_values = []
        start_time = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
