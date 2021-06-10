from tkinter import *
from tkinter import ttk

from errorCode import errorCodes
from PIL import ImageTk, Image
import io
import constants


class DetailsPage(Toplevel):
    def __init__(self, master, id, cur, isRecursed=False):
        Toplevel.__init__(self, master, bg=constants.colors['main']['bg'])

        global plate, photo, icon
        self.geometry('1500x750+0+0')
        self.title(f'Details of id {id}')
        self.protocol("WM_DELETE_WINDOW", self.closeHandler)

        if not isRecursed:
            master.withdraw()

        #get the row opened
        cur.execute(f"SELECT rowid,* FROM realtest WHERE rowid = {int(id)}")
        self.thisEntry = cur.fetchone()

        # get all the rows with same reg no.
        cur.execute(f"SELECT rowid,* FROM realtest WHERE numPlate = '{self.thisEntry[1]}'")
        self.entries = cur.fetchall()

        # main photo
        self.photoPIL = Image.open(io.BytesIO(self.thisEntry[6]))
        photowidth, photoheight = self.photoPIL.size
        aspectr = photowidth / photoheight
        self.photoPIL = self.photoPIL.resize((945, int(945 / aspectr)), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(self.photoPIL)
        self.photoLabel = Label(self, image=photo, bg=constants.colors['main']['bg'])

        self.textInfoFrame()
        self.treeTable(cur)

        # grid
        self.photoLabel.grid(row=0, column=1, columnspan=2, sticky=N + E)
        self.table.grid(row=1, column=1, columnspan=2, sticky=N + E + S + W)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)


    def textInfoFrame(self):
        infoFrame = Frame(self, bg=constants.colors['main']['bg'], width=15)

        # plate photo
        self.platePIL = Image.open(io.BytesIO(self.thisEntry[7]))
        photowidth, photoheight = self.platePIL.size
        aspectr = photowidth / photoheight
        self.platePIL = self.platePIL.resize((547, int(547 / aspectr)), Image.ANTIALIAS)
        plate = ImageTk.PhotoImage(self.platePIL)
        self.plateLabel = Label(infoFrame, anchor='s')
        self.plateLabel.image = plate
        self.plateLabel.configure(image=plate)

        numberLabel = Label(infoFrame, text=f'{self.thisEntry[1]}', padx=5, pady=5, font=("Helvetica", 25), bg='gray70')
        nameLabel = Label(infoFrame, text=f'Vehicle : {self.thisEntry[3]}', padx=5, pady=5, font=("Helvetica", 15))
        addressLabel = Label(infoFrame, text=f'Address : {self.thisEntry[4]}', padx=5, pady=5, font=("Helvetica", 15))
        totalLabel = Label(infoFrame,
                           text=f'Visit Number : {1 + self.entries.index(self.thisEntry)} | Total Visits : {len(self.entries)}',
                           padx=5, pady=5, font=("Helvetica", 15))
        thisTimeLabel = Label(infoFrame, text=f'TimeStamp of Photo - {self.thisEntry[2]}', padx=5, pady=5,
                              font=("Helvetica", 15))
        timeLabel = Label(infoFrame, text=f'Last Seen on {self.entries[-1][2]}', padx=5, pady=5, font=("Helvetica", 15))
        warningLabel = Label(infoFrame, text=f'{errorCodes.decode(self.thisEntry[5])}', padx=20, font=("Helvetica", 15))

        # grid
        infoFrame.grid(row=0, column=0, rowspan=2, sticky=N + E + S + W)#master
        self.plateLabel.pack(side=BOTTOM, fill=BOTH, expand=True)
        numberLabel.pack(side=TOP, fill=BOTH, ipady=30)
        nameLabel.pack(side=TOP, fill=BOTH, ipady=20)
        addressLabel.pack(side=TOP, fill=BOTH, ipady=20)
        totalLabel.pack(side=TOP, fill=BOTH, ipady=20)
        thisTimeLabel.pack(side=TOP, fill=BOTH, ipady=20)
        timeLabel.pack(side=TOP, fill=BOTH, ipady=20)
        warningLabel.pack(side=BOTTOM, fill=BOTH, ipady=20)

    def treeTable(self,cur):
        # treeview
        style = ttk.Style()
        style.map('Treeview', background=[('selected', 'gray70')])
        self.table = ttk.Treeview(self, selectmode='browse')
        verscrlbar = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        verscrlbar.grid(row=1, column=2, sticky=N + E + S, pady=(0, 2))
        self.table.configure(xscrollcommand=verscrlbar.set)

        self.table["columns"] = ("1", "2", "3", "4")
        self.table['show'] = 'headings'

        self.table.column("1", width=30, anchor='c')
        self.table.column("2", width=100, anchor='c')
        self.table.column("3", width=100, anchor='c')
        self.table.column("4", width=50, anchor='c')

        self.table.heading("1", text="Id")
        self.table.heading("2", text="Time")
        self.table.heading("3", text="Date")
        self.table.heading("4", text="Visit Number")

        self.table.tag_configure('odd', background='gray90')
        self.table.tag_configure('even', background='snow')

        length = len(self.entries)
        FirstWhite = 1 if length % 2 == 0 else 0
        for index, entry in enumerate(reversed(self.entries)):
            time, date = entry[2].split(' | ')
            self.table.insert("", 'end', text="", iid=entry[0], values=(entry[0], time, date, length - index),
                              tags=('even',) if index % 2 == FirstWhite else ('odd',))

        self.table.bind("<Double-1>", lambda e: self.OnDoubleClick(e, cur))

    def OnDoubleClick(self, event, cur):
        id = self.table.selection()[0]
        DetailsPage(self.master, id=id, cur=cur, isRecursed=True)
        self.destroy()

    def closeHandler(self):
        self.destroy()
        self.master.deiconify()

    # def click(self, value):
    #     self.clicked = value
    #
    # def imageResizer(self, event):
    #     if self.clicked:
    #         global plate, photo
    #
    #         new_width = event.width
    #         print(int(new_width), event.height)
    #
    #         wpercent = (new_width * 0.7 / float(self.photoPIL.size[0]))
    #         hsize = int((float(self.photoPIL.size[1]) * float(wpercent)))
    #         self.photoPIL = self.photoPIL.resize((int(new_width * 0.7), hsize), PIL.Image.ANTIALIAS)
    #
    #         photo = ImageTk.PhotoImage(self.photoPIL)
    #         self.photoLabel.destroy()
    #
    #         self.photoLabel = Label(self, image=photo, padx=10, pady=10, bg=constants.colors['main']['bg'])
    #         self.photoLabel.grid(row=0, column=0, sticky=N + W)

