import os
import cv2
import tkinter as tk
import PIL.Image, PIL.ImageTk
import camera
import model
import time


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
        self.rep_times = []
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

        self.btn_train = tk.Button(self.window, text = "Train Model", width=50, command=self.model.train_model)
        self.btn_train.pack(anchor = tk.CENTER, expand=True) 


        self.btn_toggleauto = tk.Button(self.window, text = "Toggle Counting", width=50, command=self.counting_toggle)
        self.btn_toggleauto.pack(anchor = tk.CENTER, expand=True)


        self.btn_reset = tk.Button(self.window, text = "Reset", width=50, command= lambda: self.reset)
        self.btn_reset.pack(anchor = tk.CENTER, expand=True) 

        self.counter_label = tk.Label(self.window, text=f"{self.rep_counter}")
        self.counter_label.config(font=("Arial", 24))
        self.counter_label.pack(anchor = tk.CENTER, expand=True) 

        self.btn_reset = tk.Button(self.window, text = "Calculate RPE", width=50, command= self.RPE_calc)
        self.btn_reset.pack(anchor = tk.CENTER, expand=True) 

        self.RPE_label = tk.Label(self.window)
        self.RPE_label.config(font=("Arial", 24))
        self.RPE_label.pack(anchor = tk.CENTER, expand=True) 

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
            rep_time = time.time()
            if prediction == 1:
                self.contracted = True
                self.last_prediction = 1
                self.rep_times.append(f"1_{rep_time}")
            elif prediction == 0:
                self.extended = True
                self.last_prediction = 0
                self.rep_times.append(f"0_{rep_time}")

    def counting_toggle(self):
        """
        to start or stop counting reps
        """
        self.counting_enabled = not self.counting_enabled


    def reset(self):
        """
        sets the number of reps to 0
        """
        self.rep_counter = 0

    def RPE_calc(self):
        """
        Calculates the RPE based on VL(velocity Loss) and REP% which is the percentage of repetitions completed (%REP) with respect to the maximum possible number over each analysis interval
        """
        self.times = []
        if self.rep_times[0].split("_")[0] == 0:
            for i in range(0, len(self.rep_times), 2):
                time = abs(float(self.rep_times[i].split("_")[-1]) - float(self.rep_times[i+1].split("_")[-1]))
                self.times.append(time)

        elif self.rep_times[0].split("_")[0] == 1:
            for i in range(1, len(self.rep_times), 2):
                time = abs(float(self.rep_times[i].split("_")[-1]) - float(self.rep_times[i+1].split("_")[-1]))
                self.times.append(time)

        self.distance = 1.0
        self.MV_Best = self.distance/min(self.times)
        self.MV_Last = self.distance/self.times[-1]
        self.VL = 100*((self.MV_Best - self.MV_Last)/self.MV_Best)
        self.max_reps = 15
        self.perf_reps = len(self.times)
        self.REP_percent = 100*(self.perf_reps/self.max_reps)
        
        self.RPE_label.config(text = f"{self.RPE}")