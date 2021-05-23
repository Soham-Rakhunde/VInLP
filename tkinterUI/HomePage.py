import threading
from tkinter import *
import tkinter.filedialog
from tkinter import ttk
import time

import cv2
from PIL import Image, ImageTk
import constants
from datetime import datetime
from VideoProcessor import VideoProcessor


class HomePage(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, padx=20, bg=constants.colors['main']['bg'])
        self.grid(row=1, column=1)

        self.nowTimeVar = StringVar(self, value=datetime.now().strftime("Date-%d-%m-%Y Time-%H:%M:%S"))

        timeLabel = Label(self, textvariable=self.nowTimeVar, bg=constants.colors['main']['bg'], padx=10)
        self.openVideoButton = ttk.Button(self, text='Open Video to Process', command=self.open_vid)

        # grid
        timeLabel.grid(row=0, column=0, columnspan=2, sticky=N + S + E)
        self.openVideoButton.grid(row=1, column=0, columnspan=2, sticky=N + W + S + E, ipady=10, ipadx=40, pady=280, padx=240)
        self.updater()

    def imageRefresh(self, photoLabel, plateLabel, dirname):
        vidProcessor = VideoProcessor(dirname)
        self.openVideoButton.grid_forget()
        while vidProcessor.isFrameAvailable:
            img_rgb = cv2.cvtColor(vidProcessor.frame, cv2.COLOR_BGR2RGB)
            photoPIL = Image.fromarray(img_rgb)
            photowidth, photoheight = photoPIL.size
            aspectr = photowidth / photoheight
            photoPIL = photoPIL.resize((945, int(945 / aspectr)), Image.ANTIALIAS)
            frame_image = ImageTk.PhotoImage(photoPIL)
            photoLabel.config(image=frame_image, pady=10)
            photoLabel.image = frame_image

            img_rgb = cv2.cvtColor(vidProcessor.plateImage, cv2.COLOR_BGR2RGB)
            photoPIL = Image.fromarray(img_rgb)
            photowidth, photoheight = photoPIL.size
            aspectr = photowidth / photoheight
            photoPIL = photoPIL.resize((400, int(400 / aspectr)), Image.ANTIALIAS)
            plate_image = ImageTk.PhotoImage(photoPIL)
            plateLabel.config(image=plate_image, pady=10)
            plateLabel.image = plate_image

            time.sleep(1 / 5)  # this is refresh rate


    def updater(self):
        # clock
        self.nowTimeVar.set(datetime.now().strftime("Date-%d-%m-%Y Time-%H:%M:%S"))
        self.after(1000, self.updater)

    def open_vid(self):
        # ask save location
        dirname = tkinter.filedialog.askopenfile(mode='r', filetypes=[('Video Files', '*.mp4')])
        if not dirname:
            return

        vidLabel = Label(self, pady=10)
        plateLabel = Label(self, padx=10, pady=10, bg=constants.colors['main']['bg'])

        thread = threading.Thread(target=self.imageRefresh, args=(vidLabel, plateLabel, dirname))
        thread.start()

        vidLabel.grid(row=1, column=0, columnspan=2, sticky=N)
        plateLabel.grid(row=2, column=0, sticky=N + W + S + E, columnspan=2)
