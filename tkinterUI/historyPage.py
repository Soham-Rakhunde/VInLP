import os
import sqlite3
from tkinter import *
from tkinter import simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
from DetailsPage import DetailsPage
import constants
from datetime import datetime
import tkinter.filedialog
from tkinter import messagebox
import xlwt


class HistoryPage(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, padx=20, bg=constants.colors['main']['bg'])
        self.grid(row=1, column=1)

        self.style = ttk.Style()
        self.style.map('TCombobox', fieldbackground=[('readonly', 'gray90')])
        self.style.map('TCombobox', selectbackground=[('readonly', 'gray90')])
        self.style.map('TCombobox', selectforeground=[('readonly', 'black')])
        self.style.map('Treeview', background=[('selected', 'gray70')])

        self.searchBar()
        self.dbtable()
        self.downloadBar()

        # connect database
        cwd = os.getcwd()
        parDir = cwd.replace('tkinterUI', 'realtest.db')
        self.db = sqlite3.connect(parDir)
        self.cur = self.db.cursor()
        self.cur.execute("SELECT rowid,* FROM realtest")
        self.searchedEntries = self.entries = self.cur.fetchall()
        self.resetTree()

        # resizable
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)

    def __del__(self):
        self.db.commit()
        self.db.close()

    def searchBar(self):
        # First Row (search)
        self.searchby = StringVar(value='Reg. Number')
        self.entryVar = StringVar(value='Enter Query')
        searchComboVals = ('Reg. Number','Date','Time','Vehicle','Address',)

        label = Label(self, text='Search by ', padx=10, pady=10)
        comboBox = ttk.Combobox(self, textvariable=self.searchby, state="readonly", justify='center')
        comboBox['values'] = searchComboVals
        entryBox = ttk.Entry(self, textvariable=self.entryVar, width=40, justify='center')
        searchBut = ttk.Button(self, text='Search', command=self.searchTree)
        resetButton = ttk.Button(self, text='Reset', command=self.resetTree)

        entryBox.bind('<Button-1>', self.OnSingleClickEntry)
        entryBox.bind("<Return>",lambda _:self.searchTree())
        comboBox.bind("<FocusIn>", lambda _: comboBox.selection_range(0, 0))
        comboBox.current(0)

        # grid
        label.grid(row=0, column=0, sticky=N + E + S + W, pady=(15, 2), padx=(0, 2))
        comboBox.grid(row=0, column=1, sticky=N + E + S + W, pady=(15, 2), padx=2)
        entryBox.grid(row=0, column=2, sticky=N + E + S + W, pady=(15, 2), padx=2)
        searchBut.grid(row=0, column=3, sticky=N + E + S + W, pady=(15, 2), padx=2)
        resetButton.grid(row=0, column=4, sticky=N + E + S + W, pady=(15, 2), padx=(2, 0))

    def dbtable(self):
        # treeview
        self.table = ttk.Treeview(self, height=30, selectmode='browse')

        verscrlbar = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(xscrollcommand=verscrlbar.set)

        self.table["columns"] = ("1", "2", "3", "4", "5")
        self.table['show'] = 'headings'

        self.table.column("1", width=30, anchor='c')
        self.table.column("2", width=120, anchor='c')
        self.table.column("3", width=220, anchor='c')
        self.table.column("4", width=230, anchor='c')
        self.table.column("5", width=300, anchor='c')

        # Assigning the heading names to the
        # respective columns
        self.table.heading("1", text="Id")
        self.table.heading("2", text="Number")
        self.table.heading("3", text="TimeStamp")
        self.table.heading("4", text="Vehicle")
        self.table.heading("5", text="Address")

        self.table.bind("<Double-1>", self.OnDoubleClick)
        self.table.grid(row=1, column=0, columnspan=5, sticky=N + E + S + W)
        verscrlbar.grid(row=1, column=5, sticky=N + E + S + W)

    def downloadBar(self):
        # download frame
        downloadFrame = Frame(self, bg=constants.colors['main']['bg'])

        self.downloadType = StringVar(value='Number Plate Image')
        self.downloadWhat = StringVar(value='Selected Row')

        downloadLabel = Label(downloadFrame, text='Download the ', padx=10, pady=10)

        downCombo = ttk.Combobox(downloadFrame, textvariable=self.downloadType, state="readonly", justify='center')
        downCombo['values'] = ('Number Plate Image','Captured Image','Data as Excel')
        downCombo.current(0)

        ofLabel = Label(downloadFrame, text=' of ', padx=10, pady=10)

        whatCombo = ttk.Combobox(downloadFrame, textvariable=self.downloadWhat, state="readonly", justify='center')
        whatCombo['values'] = ('Selected Row','Searched Rows','All Rows',)
        whatCombo.current(0)

        downloadBut = ttk.Button(downloadFrame, text='Download', command=self.download)

        downCombo.bind("<FocusIn>", lambda _: downCombo.selection_range(0, 0))
        whatCombo.bind("<FocusIn>", lambda _: whatCombo.selection_range(0, 0))

        # pack
        downloadLabel.pack(side=LEFT, fill=X, expand=True, pady=(2, 2), padx=(0, 2))
        downCombo.pack(side=LEFT, fill=X, expand=True, pady=(2, 2), padx=2)
        ofLabel.pack(side=LEFT, fill=X, expand=True, pady=(2, 2), padx=2)
        whatCombo.pack(side=LEFT, fill=X, expand=True, pady=(2, 2), padx=2)
        downloadBut.pack(side=LEFT, fill=X, expand=True, pady=(2, 2), padx=(2, 0))

        downloadFrame.grid(row=2, column=0, columnspan=5, sticky=N + E + S + W, pady=(2, 15), padx=(2, 2))

    def OnSingleClickEntry(self, event):
        if self.entryVar.get() == 'Enter Query':
            self.entryVar.set('')

    def OnDoubleClick(self, event):
        id = self.table.selection()[0]
        DetailsPage(self.master, id=id, cur=self.cur)

    def updateTable(self, entries):
        self.table.delete(*self.table.get_children())
        self.table.tag_configure('odd',background='gray90')
        self.table.tag_configure('even', background='snow')
        FirstWhite = 0 if len(entries)%2 == 0 else 1
        for entry in reversed(entries):
            self.table.insert("", 'end', text="", iid=entry[0], values=(
                entry[0], entry[1], entry[2], entry[3],
                entry[4]), tags = ('even',) if entry[0]%2 == FirstWhite else ('odd',))

    # resets tree to full data
    resetTree = lambda self: self.updateTable(entries=self.entries)

    def searchTree(self):
        # searches and updates table
        columnMap = {
            'Vehicle': 'name',
            'Reg. Number': 'numPlate',
            'Date': 'timeStamp',
            'Time': 'timeStamp',
            'Address': 'address',
        }
        column = self.searchby.get()
        query = self.entryVar.get()

        if column == 'Time':
            query = f"SELECT rowid,* FROM realtest WHERE {columnMap[column]} LIKE '{query}% | %'"
        elif column == 'Date':
            query = f"SELECT rowid,* FROM realtest WHERE {columnMap[column]} LIKE '% | {query}%'"
        else:
            query = f"SELECT rowid,* FROM realtest WHERE {columnMap[column]} LIKE '%{query}%'"
        self.cur.execute(query)
        self.searchedEntries = self.cur.fetchall()
        self.updateTable(entries=self.searchedEntries)

    def download(self):
        # ifelse for selecting the number of rows to download
        if self.downloadWhat.get() == 'Selected Row':
            id = self.table.selection()
            if not id :
                tkinter.messagebox.showerror(title='Row Selection Expected', message='No Row Selected')
                return None
            self.cur.execute(f"SELECT rowid,* FROM realtest WHERE rowid = {int(id[0])}")
            dList = [self.cur.fetchone()]
        elif self.downloadWhat.get() == 'All Rows' :
            dList = self.entries
        else:#Searched Row
            dList = self.searchedEntries

        # ask save location
        dirname = tkinter.filedialog.askdirectory(parent=self, initialdir="/",title='Please select location to save file ')
        if not dirname:
            return

        # excel save code
        if self.downloadType.get() == 'Data as Excel':
            # ask for file name to save
            fileName = simpledialog.askstring(title="Excel File Name",
                                              prompt="Enter the name to save the excel file :")
            if not fileName:
                return

            excel = xlwt.Workbook()
            sheet = excel.add_sheet("VInLP export", datetime.now())
            style = xlwt.easyxf('font: bold 1, color blue; borders: left thick, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')

            tl =  xlwt.easyxf('font: bold 1, color blue; border: left thick, top thick, right thin, bottom thick')
            t =  xlwt.easyxf('font: bold 1, color blue; border: left thin, top thick, right thin, bottom thick')
            tr =  xlwt.easyxf('font: bold 1, color blue; border: left thin, top thick, right thick, bottom thick')
            r =  xlwt.easyxf('border: left thin,right thick')
            br =  xlwt.easyxf('border: left thin, right thick, bottom thick')
            b =  xlwt.easyxf('border: left thin,right thin, bottom thick')
            bl =  xlwt.easyxf('border: left thick, right thin, bottom thick')
            l =  xlwt.easyxf('border: left thick,right thin')
            m =  xlwt.easyxf('border: left thin,right thin')

            sheet.write(0, 0, 'Id', tl)
            sheet.write(0, 1, 'Registration Number', t)
            sheet.write(0, 2, 'Date', t)
            sheet.write(0, 3, 'Time', t)
            sheet.write(0, 4, 'Vehicle', t)
            sheet.write(0, 5, 'Address', tr)

            sheet.col(0).width = int(4 * 260)
            sheet.col(1).width = int(17 * 260)
            sheet.col(2).width = int(11 * 260)
            sheet.col(3).width = int(12 * 260)
            sheet.col(4).width = int(30 * 260)
            sheet.col(5).width = int(35 * 260)

            sheet.write(1, 0, '', l)
            sheet.write(1, 1, '', m)
            sheet.write(1, 2, '', m)
            sheet.write(1, 3, '', m)
            sheet.write(1, 4, '', m)
            sheet.write(1, 5, '', r)

            for index, row in enumerate(dList):
                time, date = row[2].split(' | ')
                sheet.write(index+2, 0, row[0], l)
                sheet.write(index+2, 1, row[1], m)
                sheet.write(index+2, 2, date, m)
                sheet.write(index+2, 3, time, m)
                sheet.write(index+2, 4, row[3], m)
                sheet.write(index+2, 5, row[4], r)

            index = len(dList) + 1
            sheet.write(index, 0,style=bl)
            sheet.write(index, 1, style=b)
            sheet.write(index, 2, style=b)
            sheet.write(index, 3, style=b)
            sheet.write(index, 4, style=b)
            sheet.write(index, 5, style=br)
            excel.save(f'{dirname}/{fileName}.xls')

        # saving images
        else:
            for row in dList:
                print(row[0])
                with open(f'{dirname}/{row[1]}.png', 'wb') as file:
                    file.write(row[6] if self.downloadType.get() == 'Captured Image' else row[7])