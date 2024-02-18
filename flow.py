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

current_value = 30
min_value = 30   # Minimum threshold for current_value
max_value = 127 # Maximum threshold for current_value
prev_y_position = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Left half processing
    half_frame = frame[:, :half_width]
    gray = cv2.cvtColor(half_frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
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

            tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            current_y_position = tip.y

            if prev_y_position is not None:
                movement_speed = current_y_position - prev_y_position

                # Upward movement
                if movement_speed < 0:  
                    value_change_speed = 5 if abs(movement_speed) > 0.01 else 1
                    current_value = min(current_value + value_change_speed, max_value)
                # Downward movement
                elif movement_speed > 0:  
                    value_change_speed = 5 if movement_speed > 0.01 else 1
                    current_value = max(current_value - value_change_speed, min_value)

                print(f"Current Value: {current_value}, Movement Speed: {movement_speed}")

            prev_y_position = current_y_position

    # Value on the screen
    cv2.putText(right_half_frame, f"Value: {current_value}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


    # Combine and display the results for both processing part
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
