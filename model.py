from array import array
from itertools import count
from tkinter import Image
import PIL
import numpy as np
import cv2
from sklearn.svm import LinearSVC

class Model:

    def __init__(self):
        """
        Constructor
        """
        self.model = LinearSVC()
    
    def train_model(self, counters):
        """
        training the model using Linear SVC
        """
        # initializing features array
        img_list = np.array([])

        # initializing labels array
        class_list = np.array([])

        folder_path = f"./new contracted pics"
        for imgpath in os.listdir(folder_path):
            img = cv2.imread(os.path.join(folder_path, imgpath))[:,:,0]
            img = cv2.resize(img, (500,400))
            img = img[120:,:]
            img = img/255.0
            img_list = np.append(img_list, [img])
            class_list = np.append(class_list, 1)

        folder_path = f"./new extended pics"
        for imgpath in os.listdir(folder_path):
            img = cv2.imread(os.path.join(folder_path, imgpath))[:,:,0]
            img = cv2.resize(img, (500,400))
            img = img[120:,:]
            img = img/255.0
            img_list = np.append(img_list, [img])
            class_list = np.append(class_list, 0)


        img_list = img_list.reshape(200, 280*500)
        self.model.fit(img_list, class_list)
        print("Model successfully trained!")

    def predict(self, frame):
        """
        performs predictions on the current frame
        """
        frame = frame[1]
        cv2.imwrite("frame.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))
        img = PIL.Image.open("frame.jpg")
        img.thumbnail((500,400), PIL.Image.ANTIALIAS)
        img.save("frame.jpg")

        img = cv2.imread("frame.jpg")[:,:,0]
        img = img[120:,:]
        img = img/255.0
        img = img.reshape(280*500)
        prediction = self.model.predict([img])
        return prediction[0]