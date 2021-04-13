import os
from tkinter import *
from PIL import Image, ImageTk
import constants
from datetime import datetime

class HomePage(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, padx=20, bg=constants.colors['main']['bg'])
        self.grid(row=1, column=1)

        global vid, plate
        cwd = os.getcwd()
        parDir = cwd.replace('tkinterUI', 'Resources\\')
        self.nowTimeVar = StringVar(self, value=datetime.now().strftime("Date-%d-%m-%Y Time-%H:%M:%S"))

        # grid
        timeLabel = Label(self, textvariable=self.nowTimeVar, bg=constants.colors['main']['bg'],padx=10)
        vid = ImageTk.PhotoImage(Image.open(f"{parDir}img.png"))
        vidLabel = Label(self, image=vid, pady=10)
        plate = ImageTk.PhotoImage(Image.open(f"{parDir}img_1.png"))
        plateLabel = Label(self, image=plate, padx=10, pady=10, bg=constants.colors['main']['bg'])
        # numberLabel = Label(self, text='DL4CAF4943', bg='ivory', padx=10, pady=10)
        # numberLabel.grid(row=1, column=1)

        timeLabel.grid(row=0, column=0, columnspan=2, sticky=N + S + E)
        vidLabel.grid(row=1, column=0, columnspan=2, sticky=N)
        plateLabel.grid(row=2, column=0, columnspan=2, sticky=W + S + E)
        self.updater()

    def updater(self):
        # clock
        self.nowTimeVar.set(datetime.now().strftime("Date-%d-%m-%Y Time-%H:%M:%S"))
        self.after(1000, self.updater)