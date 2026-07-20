import cv2
import os
from datetime import datetime


class Webcam:

    def __init__(self, index=1):

        self.cap = cv2.VideoCapture(index)

        if not self.cap.isOpened():
            raise RuntimeError("Unable to open webcam.")


    def capture(self, output_dir, filename=None):

        success, frame = self.cap.read()

        if not success:
            raise RuntimeError("Failed to capture frame.")

        os.makedirs(output_dir, exist_ok=True)

        if filename is None:
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg")

        path = os.path.join(output_dir, filename)

        cv2.imwrite(path, frame)

        return path


    def release(self):

        self.cap.release()