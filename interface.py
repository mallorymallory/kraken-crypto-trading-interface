import tkinter as tk
from tkinter import messagebox
import time
from indicators import INDI
import json

def motion(event):
    x,y = event.x, event.y
    # print(x,y)

def menuBarCreatoor():
    menubar = tk.Menu(top)
    top.config(menu=menubar)
    file_menu = tk.Menu(menubar)
    file_menu.add_command(label='Exit',command=top.destroy)
    menubar.add_cascade(label="File",menu=file_menu)

    add_menu = tk.Menu(menubar)
    menubar.add_cascade(label="INDI+",menu=add_menu)
    add_menu.add_command(label='sma',command=lambda: activeIndiUpdatoor('sma'))
    add_menu.add_command(label='dmi',command=lambda: activeIndiUpdatoor('dmi'))
    add_menu.add_command(label='chan',command=lambda: activeIndiUpdatoor('chan'))
    add_menu.add_command(label='rsi',command=lambda: activeIndiUpdatoor('rsi'))
    add_menu.add_command(label='macd',command=lambda: activeIndiUpdatoor('macd'))

    del_menu = tk.Menu(menubar)
    menubar.add_cascade(label="INDI-",menu=del_menu)
    del_menu.add_command(label='sma',command=lambda: CLEAROOR('sma'))
    del_menu.add_command(label='dmi',command=lambda: CLEAROOR('dmi'))
    del_menu.add_command(label='chan',command=lambda: CLEAROOR('chan'))
    del_menu.add_command(label='rsi',command=lambda: CLEAROOR('rsi'))
    del_menu.add_command(label='macd',command=lambda: CLEAROOR('macd'))

    help_menu = tk.Menu(menubar)
    menubar.add_cascade(label="Help",menu=help_menu)
    help_menu.add_command(label='pairs',command=lambda: messagebox.showinfo('pairs', list(indicators.pairmap.keys())))
    help_menu.add_command(label='intervals',command=lambda: messagebox.showinfo('intervals', pInts))


def mainCreatoor():
    mainCanvas = tk.Canvas(canframe, bg='black', height = 500, width=720, scrollregion=(0,0,5760,5760))
    mainCanvas.config(xscrollcommand=xscroll.set)
    mainCanvas.grid(column=0,row=0)
    return mainCanvas

def underCreatoor(y):
    subCanvas = tk.Canvas(canframe, bg='black', height= 100, width=720, scrollregion=(0,0,5760,5760))
    subCanvas.config(xscrollcommand=xscroll.set)
    subCanvas.grid(column=0,row=y)
    return subCanvas

# def stuffDrawoor():
def startoor():
    with open('settings.txt', 'r') as settingsFile:
        settings = settingsFile.readline()
        print(settings)
        settingsObj = json.loads(settings.replace("'",'"'))

        pMap = settingsObj['pMap']
        interval = settingsObj['interval']
        pair = settingsObj['pair']
        activeIndicators = settingsObj['activeIndicators']

    return pMap,interval,pair,activeIndicators

def chartDrawoor(x, open, high, low, close, multi, ofs, colour):
    c.create_rectangle(x-7, ((float(open)*multi)*-1) +ofs, x-1,((float(close)*multi)*-1)+ofs, fill=colour, tags=('chart'))
    c.create_line(x-4, ((float(high)*multi)*-1) +ofs, x-4,((float(low)*multi)*-1)+ofs, fill=colour, tags=('chart'))

def indiDrawoor(indi, x, last, new, multi, ofs, canvas, colour):
    if type(last) != list:
        last,new=[last],[new]
    for i in range(len(last)):
        canvas.create_line(x-8, ((float(last[i])*multi)*-1)+ofs, 
                            x,((float(new[i])*multi)*-1)+ofs, fill=colour[i], tags=(indi))

def multiplusoffsetGettoor(data, sortbyindex, chartsize):
    smallest = float(min(data, key=lambda z: float(z[sortbyindex[1]]))[sortbyindex[1]])
    biggest = float(max(data, key=lambda z: float(z[sortbyindex[0]]))[sortbyindex[0]])
    chartMulti = chartsize/(biggest-smallest)
    chartOffset = biggest*chartMulti
    return chartMulti,chartOffset



def DRAWOOR():
    pair = pairvar.get()
    coords = canframe.grid_size()
    print(coords)
    for i in activeIndicators:
        if activeIndicators[i]['active'] and i not in list(studyHolder.keys()):
            if i in STUDIES:
              studyHolder.update({i:underCreatoor(coords[1]+1)})

    x = 0
    lasts = {}
    # print(indicators.data[pair]['rsi'])
    chartMulti,chartOffset = multiplusoffsetGettoor(indicators.data[pair]['ohlc'], [2,3], 500)
    mcdMULTI,mcdPLUS = multiplusoffsetGettoor(indicators.data[pair]['macd'][pMap[str(interval)][1]:], [0,0], 100)

    for row in range(len(indicators.data[pair]['ohlc'])):
        if x == 0:
            pass
        else:

            chartDrawoor(x, indicators.data[pair]['ohlc'][row][1], indicators.data[pair]['ohlc'][row][2], 
                        indicators.data[pair]['ohlc'][row][3],indicators.data[pair]['ohlc'][row][4], chartMulti, chartOffset,
                        'green' if float(indicators.data[pair]['ohlc'][row][4])>float(indicators.data[pair]['ohlc'][row][1]) else 
                        'red')

            for i in activeIndicators:
                if activeIndicators[i]['active']:
                    if i in OVERLAY:
                        indiDrawoor(i, x, lasts[i], indicators.data[pair][i][row],chartMulti, chartOffset, c, activeIndicators[i]['colour'])
                    elif i in STUDIES and i != 'macd':
                        indiDrawoor(i, x, lasts[i], indicators.data[pair][i][row],1, 100, studyHolder[i], activeIndicators[i]['colour'])
                    else:
                        indiDrawoor(i, x, lasts[i], indicators.data[pair][i][row],mcdMULTI, mcdPLUS, studyHolder[i], activeIndicators[i]['colour'])

        x+=8
        for i in activeIndicators:
            lasts.update({i:indicators.data[pair][i][row]})
    if activeIndicators['rsi']['active']:
        h = studyHolder['rsi'].create_line(0, 20, 5760, 20, fill='red', tag=('rsi'))
        l = studyHolder['rsi'].create_line(0, 80, 5760, 80, fill = 'green', tag=('rsi'))

    ##FORCE TO LEFT on UPDATE
    c.xview_moveto(0.875)
    for canvy in studyHolder:
        studyHolder[canvy].xview_moveto(0.875)


def CLEAROOR(indi):
    if indi == 'change':
        for i in activeIndicators:
            if activeIndicators[i]['active']:
                if i in OVERLAY:
                    c.delete(i)
                else:
                    studyHolder[i].delete(i)
        c.delete('chart')
    else:
        if indi in OVERLAY:
            c.delete(indi)
        else:
            studyHolder[indi].delete(indi)
            if studyHolder[indi].find_all() == ():
                studyHolder[indi].destroy()
                studyHolder.pop(indi)
        activeIndicators[indi]['active'] = 0

def activeIndiUpdatoor(indi):
    activeIndicators[indi]['active'] = 1
    DRAWOOR()

def xview(*args):
    # print(args)
    c.xview(*args)
    for i in studyHolder:
        studyHolder[i].xview(*args)

def labelEnteroor(args, Label):
    Label.configure(fg='black', bg='white')
def labelLeavoor(args, Label):
    Label.configure(fg='white', bg='black')

def labelClickoor(args, setting, ):
    print(setting)
    changer = tk.Entry(fakercanframe)
    changer.grid(column=0, row=1)
    changer.focus_set()
    changerbutton = tk.Button(fakercanframe)
    changerbutton.grid(column=1,row=1)
    changer.bind('<Return>', lambda x: updateSettoor(changer.get(), [changer,changerbutton], setting))
    changerbutton.configure(command= lambda: updateSettoor(changer.get(), [changer,changerbutton], setting))


def updateSettoor(new,toDestroy, setting):
    print(setting)

    if new in list(indicators.pairmap.keys()) or str(new) in pInts:
        if setting == 'pair':
            pairvar.set(indicators.pairmap[new])
            indicators.pairSetter([indicators.pairmap[new]])
        else:
            intvar.set(new)
        indicators.getNew(activeIndicators, interval= None if setting == 'pair' else new)
        toDestroy[0].destroy()
        toDestroy[1].destroy()
        CLEAROOR('change')
        DRAWOOR()
    else:
        messagebox.showerror('Warning', 'not a valid '+setting+' try again')


STUDIES = ['dmi', 'macd', 'rsi']
OVERLAY = ['chan', 'sma', 'ema']

pMap,interval,pair,activeIndicators = startoor()

indicators = INDI([pair])
indicators.getNew(activeIndicators, interval)
pInts = ['1', '5', '10', '15', '30', '60', '240', '1440', '10080', '21600']

top = tk.Tk()
top.bind('<Motion>', motion)
canframe = tk.Frame(top)
canframe.grid(column=0,row=0)
fakercanframe = tk.Frame(top, bg='black')
fakercanframe.grid(column=0,row=0, sticky='nw',padx=2,pady=2,)


pairvar=tk.StringVar()
pairvar.set(pair)
pairLabel = tk.Label(fakercanframe, textvariable=pairvar, bg='black',fg='white',)
pairLabel.grid(column=0,row=0, sticky='w')
pairLabel.bind('<Enter>', lambda x: labelEnteroor(x, pairLabel))
pairLabel.bind('<Leave>', lambda x: labelLeavoor(x, pairLabel))
pairLabel.bind('<Button-1>', lambda x: labelClickoor(x,'pair'))

intvar=tk.StringVar()
intvar.set(interval)
intLabel = tk.Label(fakercanframe, textvariable=intvar, bg='black',fg='white',)
intLabel.grid(column=1,row=0, sticky='w')
intLabel.bind('<Enter>', lambda x: labelEnteroor(x, intLabel))
intLabel.bind('<Leave>', lambda x: labelLeavoor(x, intLabel))
intLabel.bind('<Button-1>', lambda x: labelClickoor(x,'interval'))

xscroll = tk.Scrollbar(top, orient='horizontal')
xscroll.grid(column=0,row=100,sticky='ew')
xscroll.config(command = xview)

while True:
    if indicators.setup:
        break
    time.sleep(0.1)

studyHolder = {}
menuBarCreatoor()
c = mainCreatoor()

DRAWOOR()

top.mainloop()




