import cv2
import mediapipe as mp
import collections

def average_position(landmarks, image_shape):
    domain = landmarks.landmark[3:4]
    x = [lm.x * image_shape[1] for lm in domain]
    y = [lm.y * image_shape[0] for lm in domain]
    avg_x = sum(x) / len(domain)
    avg_y = sum(y) / len(domain)
    return avg_x, avg_y

def calculate_moving_average(new_value, history, window_size=5):
    history.append(new_value)
    if len(history) > window_size:
        history.popleft()
    return sum(history) / len(history)

def put_text(image, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA):
    cv2.putText(image, text, org, font, fontScale, color, thickness, lineType)

# def check_pattern_from_history(direction_history):
#     return all([dh == p for dh, p in zip(direction_history, pattern)])

def find_most_common_direction_in_history(direction_history):
    if not direction_history:
        return ""
    most_common = collections.Counter(direction_history).most_common(1)
    return most_common[0][0]

def find_last_effective_direction(direction_history):
    for direction in reversed(direction_history):
        if direction != '':
            return direction
    return None


threshold = 15
history_x = collections.deque(maxlen=5)
history_y = collections.deque(maxlen=5)

# define a pattern history
direction_history = collections.deque(maxlen=4)
pattern = ['down', 'right', 'up', 'left']
previous_direction = ""

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

with mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as hands:
  prev_avg_position = None
  while cap.isOpened():
    success, image = cap.read()
    image = cv2.flip(image, 1)
    if not success:
      print("Ignoring empty camera frame.")
      continue

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    direction = ""
    if results.multi_hand_landmarks:
      for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
        if handedness.classification[0].label == 'Left':
          continue
        current_position = average_position(hand_landmarks, image.shape)
        avg_x = calculate_moving_average(current_position[0], history_x)
        avg_y = calculate_moving_average(current_position[1], history_y)
        avg_position = (avg_x, avg_y)

        if prev_avg_position is not None:
          dx = avg_position[0] - prev_avg_position[0]
          dy = avg_position[1] - prev_avg_position[1]
          if abs(dx) > threshold or abs(dy) > threshold:
            if abs(dx) > abs(dy): 
              direction = 'left' if dx < 0 else 'right'
            else: 
              direction = 'up' if dy < 0 else 'down'
          else:
            direction = ""

        # todo induct last direction
        if direction!="":
          direction_history.append(direction)
        current_direction = find_most_common_direction_in_history(direction_history)
        if current_direction!=previous_direction:
          print(current_direction)
          # print(direction_history,"previous:",previous_direction,"now:",current_direction)
        previous_direction = current_direction
        prev_avg_position = avg_position
        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
    
    put_text(image, direction, (50,50))
    cv2.imshow('MediaPipe Hands', image)
    
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
