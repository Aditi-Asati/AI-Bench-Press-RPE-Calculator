# This python script is for camera processing
import cv2

class Camera:

    def __init__(self):
        """
        Constructor
        """
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise ValueError("Camera not found")
    
        self.width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def __del__(self):
        if self.camera.isOpened():
            self.camera.release()

    def get_frame(self):
        """
        This function is going to give us the picture we are seeing rn
        """
        if self.camera.isOpened():
            ret, frame = self.camera.read()

            if ret:
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RBG)
                # cv2 by default has BGR color scheme so changing it to RBG
            else:
                return ret, None
        else:
            return None
