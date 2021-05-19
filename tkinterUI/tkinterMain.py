from tkinter import *
from ttkthemes import themed_tk as tkt
from historyPage import HistoryPage
from modifiedClass import HoverButton
from HomePage import HomePage
import constants



class App(tkt.ThemedTk):
    def __init__(self):
        tkt.ThemedTk.__init__(self)

        self.set_theme('adapta')
        self.geometry('+0+0')
        self.title('Vehicle Identification & License Plate Detection System (VInLP DecSys)')
        self.configure(bg=constants.colors['main']['bg'])
        self.side_bar()
        self._frame = None
        self.switch_frame(frame_class=HomePage)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # eventloops
        self.mainloop()

    def side_bar(self):
        optionFrame = Frame(self, bg=constants.colors['sidebar']['bg'], width=15)

        text1 = Label(optionFrame, text='VInLP', bg=constants.colors['sidebar']['activebg'],
                      fg=constants.colors['sidebar']['font'], width=15, height=0)
        text2 = Label(optionFrame, text='DecSys', bg=constants.colors['sidebar']['activebg'],
                      fg=constants.colors['sidebar']['font'], width=15, height=0)
        homeButton = HoverButton(optionFrame, text='Home', relief=FLAT, width=15, bg=constants.colors['sidebar']['bg'],
                                 activebackground=constants.colors['sidebar']['activebg'],
                                 command=lambda: self.switch_frame(HomePage))
        dbButton = HoverButton(optionFrame, text='History', relief=FLAT, width=15, bg=constants.colors['sidebar']['bg'],
                               activebackground=constants.colors['sidebar']['activebg'],
                               command=lambda: self.switch_frame(HistoryPage))
        searchButton = HoverButton(optionFrame, text='Search', relief=FLAT, width=15,
                                   bg=constants.colors['sidebar']['bg'],
                                   activebackground=constants.colors['sidebar']['activebg'])

        exitButton = HoverButton(self, text='Exit', relief=FLAT, width=15, height=2,
                                 bg=constants.colors['sidebar']['bg'],
                                 activebackground=constants.colors['sidebar']['activebg'], command=self.destroy)

        # grid
        optionFrame.grid(row=0, column=0, sticky=N + E + S + W)  # master
        text1.grid(row=0, column=0)
        text2.grid(row=1, column=0)
        homeButton.grid(row=2, column=0, sticky=N + E + W)
        dbButton.grid(row=3, column=0, sticky=N + E + W)
        searchButton.grid(row=4, column=0, sticky=N + E + W)
        exitButton.grid(row=1, column=0, sticky=S)  # master

    def switch_frame(self, frame_class):
        if self._frame != frame_class:
            if self._frame is not None:
                self._frame.destroy()
            self._frame = frame_class(self)
            self._frame.grid(row=0, column=1, rowspan=2, sticky=N + E + S + W)


if __name__ == "__main__":
    root = App()
