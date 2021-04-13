from tkinter import *

class HoverButton(Button):
    def __init__(self, master, **kw):
        Button.__init__(self, master=master, **kw)
        self.defaultBackground = self["bg"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['bg'] = self['activebackground']
        self['fg'] = self.defaultBackground

    def on_leave(self, e):
        self['bg'] = self.defaultBackground
        self['fg'] = 'black'
