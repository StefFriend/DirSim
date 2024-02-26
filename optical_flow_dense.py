import cv2
import mediapipe as mp
import numpy as np

# 
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

# 
ok, firstFrame = cap.read()
firstFrame = cv2.flip(firstFrame, 1)

# 
hsv_canvas = np.zeros_like(firstFrame)
frame_gray_init = cv2.cvtColor(firstFrame, cv2.COLOR_BGR2GRAY)
hsv_canvas[..., 1] = 255 

threshold = 10
frame_counter = 0

flow = None
while True:
    frame_counter += 1  
    if frame_counter > 1: 
      frame_counter = 0
      continue
    ok, frame = cap.read()
    if not ok:
        break
    hsv_canvas = np.zeros_like(frame)
    hsv_canvas[..., 1] = 255

    frame = cv2.flip(frame, 1)
    # 2 gray
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect hands
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        hand_landmarks = hand_landmarks.landmark 
        x_max = int(max(lm.x for lm in hand_landmarks) * frame.shape[1])
        x_min = int(min(lm.x for lm in hand_landmarks) * frame.shape[1])
        y_max = int(max(lm.y for lm in hand_landmarks) * frame.shape[0])
        y_min = int(min(lm.y for lm in hand_landmarks) * frame.shape[0])

        hand_roi_initial = frame_gray_init[y_min:y_max, x_min:x_max]
        hand_roi_current = frame_gray[y_min:y_max, x_min:x_max]

        if hand_roi_initial.size and hand_roi_current.size:
            flow = cv2.calcOpticalFlowFarneback(hand_roi_initial, hand_roi_current, None, 0.5, 3, 15, 3, 5, 1.1, 0)
            magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            
            horizontal_flow = np.mean(flow[..., 0])
            vertical_flow = np.mean(flow[..., 1])
            # 
            avg_angle = np.mean(angle)
            direction = 'Unknown'
            # if 0 <= avg_angle < np.pi/4 or 7*np.pi/4 <= avg_angle < 2*np.pi:
            #     direction = 'left'
            # elif np.pi/4 <= avg_angle < 3*np.pi/4:
            #     direction = 'up'
            # elif 3*np.pi/4 <= avg_angle < 5*np.pi/4:
            #     direction = 'right'
            # elif 5*np.pi/4 <= avg_angle < 7*np.pi/4:
            #     direction = 'down'
            if abs(horizontal_flow)>0.2 or abs(vertical_flow)>0.2:
                if horizontal_flow>vertical_flow and horizontal_flow>0:
                    direction = 'left'
                elif horizontal_flow>vertical_flow and horizontal_flow>0:
                    direction = 'right'
                elif horizontal_flow<vertical_flow and vertical_flow>0:
                    direction = 'up'
                else:
                    direction = 'down'
            avg_mag = np.mean(magnitude)
            # print(horizontal_flow,vertical_flow)
            # 
            
            cv2.putText(frame, f'Direction: {direction,horizontal_flow,vertical_flow}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            hsv_canvas[y_min:y_max, x_min:x_max, 0] = angle * (180 / (np.pi / 2))
            hsv_canvas[y_min:y_max, x_min:x_max, 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)

    frame_rgb = cv2.cvtColor(hsv_canvas, cv2.COLOR_HSV2BGR)
    cv2.imshow('Original Video', frame)
    # 
    cv2.imshow('Hand Optical Flow', frame_rgb)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_gray_init = frame_gray

cap.release()
cv2.destroyAllWindows()
