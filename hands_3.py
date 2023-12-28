import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

threshold = 0.01
frame_rate = cap.get(cv2.CAP_PROP_FPS)
time_interval = 1 / frame_rate

prev_landmarks = None  

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # for right hand momently
            if handedness.classification[0].label == 'Left':
                continue
            current_landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]

            if prev_landmarks is not None:
                # movements in two directions
                horizontal_displacements = [(cl[0] - pl[0]) for cl, pl in zip(current_landmarks, prev_landmarks)]
                vertical_displacements = [(cl[1] - pl[1]) for cl, pl in zip(current_landmarks, prev_landmarks)]
                # print(horizontal_displacements,vertical_displacements)

                median_horizontal_displacement = np.median(horizontal_displacements)
                median_vertical_displacement = np.median(vertical_displacements)

                # velocity
                velocity = np.sqrt(median_horizontal_displacement**2 + median_vertical_displacement**2) / time_interval

                # direction
                if(abs(median_horizontal_displacement)>threshold or abs(median_vertical_displacement)>threshold):
                    if abs(median_horizontal_displacement) > abs(median_vertical_displacement):
                        direction = 'horizontal'
                        if median_horizontal_displacement > 0:
                            sub_direction = 'right'
                        else:
                            sub_direction = 'left'
                    else:
                        direction = 'vertical'
                        if median_vertical_displacement > 0:
                            sub_direction = 'down'
                        else:
                            sub_direction = 'up'
                # print(velocity)
                    cv2.putText(frame, f'Direction: {sub_direction}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, f'Velocity: {velocity:.2f}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            prev_landmarks = current_landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
    
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
