import cv2

class SliderController:
    def __init__(self, min_value=0.3, max_value=1.0, initial_value=0.65):
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value

    def update(self, y_position, img_height):
        if y_position is not None:
            normalized_position = 1 - (y_position / img_height)
            self.value = self.min_value + normalized_position * (self.max_value - self.min_value)
            self.value = max(self.min_value, min(self.max_value, self.value))
        return self.value

    def draw(self, img, x_position, color):
        img_height = img.shape[0]
        slider_height = int(((self.value - self.min_value) / (self.max_value - self.min_value)) * img_height)
        cv2.rectangle(img, (x_position, img_height), (x_position + 30, img_height - slider_height), color, -1)
        cv2.putText(img, f"{self.value:.2f}", (x_position, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)