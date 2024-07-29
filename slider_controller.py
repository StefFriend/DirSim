import cv2

class SliderController:
    def __init__(self, min_value=0.3, max_value=1.0, initial_value=0.65):
        # Initialize the slider with min, max, and initial values
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value

    def update(self, y_position, img_height):
        # Update the slider value based on the y-position of the hand
        if y_position is not None:
            # Normalize the y-position (0 at bottom, 1 at top)
            normalized_position = 1 - (y_position / img_height)
            # Map the normalized position to the slider range
            self.value = self.min_value + normalized_position * (self.max_value - self.min_value)
            # Clamp the value to the allowed range
            self.value = max(self.min_value, min(self.max_value, self.value))
        return self.value

    def draw(self, img, x_position, color):
        # Draw the slider on the image
        img_height = img.shape[0]
        # Calculate the height of the slider based on its current value
        slider_height = int(((self.value - self.min_value) / (self.max_value - self.min_value)) * img_height)
        # Draw the slider rectangle
        cv2.rectangle(img, (x_position, img_height), (x_position + 30, img_height - slider_height), color, -1)
        # Draw the current value text
        cv2.putText(img, f"{self.value:.2f}", (x_position, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)