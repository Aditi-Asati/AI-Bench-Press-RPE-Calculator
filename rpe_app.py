import os
import cv2
import tkinter as tk
import PIL.Image, PIL.ImageTk
import camera
import model


class App:

    def __init__(self):
        """
        Constructor
        """
        self.window = tk.Tk()
        self.window.title = "Biceps Curl Counter"
        self.rep_counter = 0
        self.counters = [1,1]

        self.extended = False
        self.contracted= False
        self.last_prediction = 0

        self.model = model.Model()

        self.counting_enabled = False
        self.camera = camera.Camera()
        
        self.init_gui()
        self.delay = 15
        self.update()
        self.window.attributes("-topmost", True)

        self.window.mainloop()

    def init_gui(self):
        """
        initialization of the GUI 
        """

        self.canvas = tk.Canvas(self.window, width=self.camera.width, height=self.camera.height)
        self.canvas.pack()

        self.btn_toggleauto = tk.Button(self.window, text = "Toggle Counting", width=50, command=self.counting_toggle)
        self.btn_toggleauto.pack(anchor = tk.CENTER, expand=True)

        self.btn_class_one = tk.Button(self.window, text = "Extended", width=50, command= lambda: self.save_for_class(1))
        self.btn_class_one.pack(anchor = tk.CENTER, expand=True) 
        # when we click this button, the program is going to take a snapshot of the current image that we are seeing and put this into the directory which contains all "extended" arms images for the training set  

        self.btn_class_two = tk.Button(self.window, text = "Contracted", width=50, command= lambda: self.save_for_class(2))
        self.btn_class_two.pack(anchor = tk.CENTER, expand=True) 
        # when we click this button, the program is going to take a snapshot of the current image that we are seeing and put this into the directory which contains all "contracted" arms images for the training set  

        self.btn_train = tk.Button(self.window, text = "Train Model", width=50, command= lambda: self.model.train_model(self.counters))
        self.btn_train.pack(anchor = tk.CENTER, expand=True) 
        # As soon as we press this button, the program will train the model on the training set of the extended and contracted images of the arm

        self.btn_reset = tk.Button(self.window, text = "Reset", width=50, command= lambda: self.reset)
        self.btn_reset.pack(anchor = tk.CENTER, expand=True) 

        self.counter_label = tk.Label(self.window, text=f"{self.rep_counter}")
        self.counter_label.config(font=("Arial", 24))
        self.counter_label.pack(anchor = tk.CENTER, expand=True) 


    def update(self):
        """
        To update the GUI afterwards
        """
        if self.counting_enabled:
            self.predict()
        
        if self.contracted and self.extended:
            self.contracted, self.extended = False, False
            self.rep_counter +=1    
        
        self.counter_label.config(text=f"{self.rep_counter}")

        ret, frame = self.camera.get_frame()
        if ret:
            """
            updating the content of the canvas 
            """
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0,0,image=self.photo, anchor= tk.NW)

        self.window.after(self.delay, self.update)
        # the update function calls itself after every time interval defined by the delay atttribute

    def predict(self):
        """
        performs prediction on the frame each time the update function is called
        """
        frame = self.camera.get_frame()
        prediction = self.model.predict(frame)

        if prediction != self.last_prediction:
            if prediction == 1:
                self.extended = True
                self.last_prediction = 1
            if prediction == 2:
                self.contracted = True
                self.last_prediction = 2

    def counting_toggle(self):
        """
        to start or stop counting reps
        """
        self.counting_enabled = not self.counting_enabled

    def save_for_class(self, class_num):
        """
        saves the current image after converting it into black & white image and resizing it using PIL in the respective directories depending on the class (either "extended" or "contracted")
        """
        ret,  frame = self.camera.get_frame()

        if not os.path.exists("1"):
            os.mkdir("1")

        if not os.path.exists("2"):
            os.mkdir("2")

        # saving the image in the given directory and converting it into black and white
        cv2.imwrite(f"{class_num}/frame{self.counters[class_num-1]}.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))

        # opening the image using PIL
        img = PIL.Image.open(f"{class_num}/frame{self.counters[class_num-1]}.jpg")

        # resizing the image so that the model does not have to perform unnecessary computations
        img.thumbnail((150,150), PIL.Image.ANTIALIAS)

        # saving the image again using PIL
        img.save(f"{class_num}/frame{self.counters[class_num-1]}.jpg")

        self.counters[class_num-1] += 1

    def reset(self):
        """
        sets the number of reps to 0
        """
        self.rep_counter = 0