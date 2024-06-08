import tkinter as tk
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

def mainCreatoor():
    mainCanvas = tk.Canvas(canframe, bg='black', height = 500, width=720, scrollregion=(0,0,5760,5760))
    mainCanvas.config(xscrollcommand=xscroll.set)
    mainCanvas.pack()
    return mainCanvas

def underCreatoor():
    subCanvas = tk.Canvas(canframe, bg='black', height= 100, width=720, scrollregion=(0,0,5760,5760))
    subCanvas.config(xscrollcommand=xscroll.set)
    subCanvas.pack()
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
    c.create_rectangle(x-7, ((float(open)*multi)*-1) +ofs, x-1,((float(close)*multi)*-1)+ofs, fill=colour, )
    c.create_line(x-4, ((float(high)*multi)*-1) +ofs, x-4,((float(low)*multi)*-1)+ofs, fill=colour, )

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
    for i in activeIndicators:
        if activeIndicators[i]['active'] and i not in list(studyHolder.keys()):
            if i in STUDIES:
                if i != 'macd':
                    studyHolder.update({i:underCreatoor()})
                else:
                    studyHolder.update({i:studyHolder['rsi']})
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


STUDIES = ['dmi', 'macd', 'rsi']
OVERLAY = ['chan', 'sma', 'ema']

pMap,interval,pair,activeIndicators = startoor()

indicators = INDI([[pair, interval, pMap[str(interval)]]])
indicators.getNew(activeIndicators)

top = tk.Tk()
top.bind('<Motion>', motion)
canframe = tk.Frame(top)
canframe.pack()

xscroll = tk.Scrollbar(canframe, orient='horizontal')
xscroll.pack(side='bottom', fill='x')
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




