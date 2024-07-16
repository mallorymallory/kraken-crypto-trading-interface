import tkinter as tk
from tkinter import messagebox
from tkinter import colorchooser
import time
from indicators import INDI
import json


SCALERPAIR = (0,0)
 
def motion(event):
    x,y = event.x, event.y
    # print(x,y)
def motion_(event, typee=None):
    
    x,y = event.x, event.y
    global SCALERPAIR
    xdiff = round(SCALERPAIR[0]-x,2)
    ydiff = round(SCALERPAIR[1]-y,2)
    print(xdiff, ydiff )
    scale_x, scale_y, move_x, move_y = [None, None, xdiff, ydiff] if typee else [round(1+(xdiff/100),2), round(1+ (ydiff/100),2), None, None]
    canvasMovoor(c, scale_x, scale_y, move_x, move_y)
        
    SCALERPAIR = (x,y)
    print(x,y, event) 

def canvasMovoor(canvas, scale_x, scale_y, move_x, move_y):
    global studyHolder
    
    if not move_x and not move_y:
        canvas.scale('all', 0 ,0 , scale_x  ,scale_y)
        for i in studyHolder:
            studyHolder[i].scale('all', 0 ,0 , scale_x  ,1)
    items = canvas.find_all()
    box = canvas.bbox('all')
    print(box)
    if not move_x and not move_y: # double if >:( it needs to be after bbox but bbox needs to be after scaling for jitter 
        move_x = (3550-box[2])
        move_y = 0  

    for item in items:
        canvas.move(item, move_x, move_y)
    for i in studyHolder:
        items = studyHolder[i].find_all()
        box = studyHolder[i].bbox('all')
        for item in items:
            studyHolder[i].move(item, move_x, 0)   

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
    add_menu.add_command(label='stoch',command=lambda: activeIndiUpdatoor('stoch'))
    add_menu.add_command(label='chan',command=lambda: activeIndiUpdatoor('chan'))
    add_menu.add_command(label='rsi',command=lambda: activeIndiUpdatoor('rsi'))
    add_menu.add_command(label='macd',command=lambda: activeIndiUpdatoor('macd'))

    del_menu = tk.Menu(menubar)
    menubar.add_cascade(label="INDI-",menu=del_menu)
    del_menu.add_command(label='sma',command=lambda: CLEAROOR('sma'))
    del_menu.add_command(label='dmi',command=lambda: CLEAROOR('dmi'))
    del_menu.add_command(label='stoch',command=lambda: CLEAROOR('stoch'))
    del_menu.add_command(label='chan',command=lambda: CLEAROOR('chan'))
    del_menu.add_command(label='rsi',command=lambda: CLEAROOR('rsi'))
    del_menu.add_command(label='macd',command=lambda: CLEAROOR('macd'))

    setty_menu = tk.Menu(menubar)
    menubar.add_cascade(label="Settings",menu=setty_menu)
    setty_menu.add_command(label='colours',command=settingChangoor)
    setty_menu.add_command(label='indicators',command=lambda: CLEAROOR('dmi'))

    help_menu = tk.Menu(menubar)
    menubar.add_cascade(label="Help",menu=help_menu)
    help_menu.add_command(label='pairs',command=lambda: messagebox.showinfo('pairs', list(indicators.pairmap.keys())))
    help_menu.add_command(label='intervals',command=lambda: messagebox.showinfo('intervals', pInts))

def settingChangoor():
    def colourPickoor(x,y,z,a):
        print(x)
        color_code = colorchooser.askcolor(title="Choose a color")[1]
        if color_code:
            a.configure(bg=color_code)
            z[y] = color_code
        
        top2.focus_set()

    top2 = tk.Toplevel(top,)
    tframe = tk.Frame(top2)
    tframe.grid(column=0,row=0)

    chartLabel = tk.Label(tframe, text='chart')
    chartLabel.grid(column=0,row=0)
    chartcolour1 = tk.Label(tframe, text='11111', bg=chartColour[0])
    chartcolour1.grid(column=1,row=0)
    chartcolour2 = tk.Label(tframe, text='11111', bg=chartColour[1])
    chartcolour2.grid(column=2,row=0)
    chartcolour1.bind('<Button-1>', lambda x: colourPickoor(x, 0, chartColour, chartcolour1))
    chartcolour2.bind('<Button-1>', lambda x: colourPickoor(x, 1, chartColour, chartcolour2))
    e = {}
    yy = 1
    for i in [indi for indi in activeIndicators]:
        chartLabel = tk.Label(tframe, text=i)
        chartLabel.grid(column=0,row=yy)
        chartcolourx = tk.Label(tframe, text='11111', bg=activeIndicators[i]['colour'][0])
        chartcolourx.grid(column=1,row=yy)
        chartcoloury = tk.Label(tframe, text='11111', bg=activeIndicators[i]['colour'][1])
        chartcoloury.grid(column=2,row=yy)
        e.update({i:[chartcolourx,chartcoloury]})
        
        yy+=1
    #DONT LOOK
    e['sma'][0].bind('<Button-1>', lambda x: colourPickoor(x, 0, activeIndicators['sma']['colour'], e['sma'][0]))
    e['chan'][0].bind('<Button-1>', lambda x: colourPickoor(x, 0, activeIndicators['chan']['colour'], e['chan'][0]))
    e['dmi'][0].bind('<Button-1>', lambda x: colourPickoor(x, 0, activeIndicators['dmi']['colour'], e['dmi'][0]))
    e['stoch'][0].bind('<Button-1>', lambda x: colourPickoor(x, 0, activeIndicators['stoch']['colour'], e['stoch'][0]))
    e['rsi'][0].bind('<Button-1>', lambda x: colourPickoor(x, 0, activeIndicators['rsi']['colour'], e['rsi'][0]))
    e['macd'][0].bind('<Button-1>', lambda x: colourPickoor(x, 0, activeIndicators['macd']['colour'], e['macd'][0]))
    
    e['sma'][1].bind('<Button-1>', lambda x: colourPickoor(x, 1, activeIndicators['sma']['colour'], e['sma'][1]))
    e['chan'][1].bind('<Button-1>', lambda x: colourPickoor(x, 1, activeIndicators['chan']['colour'], e['chan'][1]))
    e['dmi'][1].bind('<Button-1>', lambda x: colourPickoor(x, 1, activeIndicators['dmi']['colour'], e['dmi'][1]))
    e['stoch'][1].bind('<Button-1>', lambda x: colourPickoor(x, 1, activeIndicators['stoch']['colour'], e['stoch'][1]))
    e['rsi'][1].bind('<Button-1>', lambda x: colourPickoor(x, 1, activeIndicators['rsi']['colour'], e['rsi'][1]))
    e['macd'][1].bind('<Button-1>', lambda x: colourPickoor(x, 1, activeIndicators['macd']['colour'], e['macd'][1]))

    button = tk.Button(top2, text='Apply', command=resetoor)
    button.grid(column=0, row=yy+1)
    

def resetoor():
    CLEAROOR('change')
    DRAWOOR()

def mainCreatoor():
    mainCanvas = tk.Canvas(canframe, bg='black', height = 500, width=720, scrollregion=(0,0,3600,3600))
    mainCanvas.config(xscrollcommand=xscroll.set)
    mainCanvas.grid(column=0,row=0)
    return mainCanvas

def underCreatoor(y):
    subCanvas = tk.Canvas(canframe, bg='black', height= 100, width=720, scrollregion=(0,0,3600,3600))
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
        chartColour = settingsObj['chartcolour']
        interval = settingsObj['interval']
        pair = settingsObj['pair']
        activeIndicators = settingsObj['activeIndicators']

    return pMap,interval,pair,activeIndicators,chartColour

def chartDrawoor(x, open, high, low, close, multi, ofs, colour):
    c.create_rectangle(x-5, ((float(open)*multi)*-1) +ofs, x-1,((float(close)*multi)*-1)+ofs, fill=colour, tags=('chart'))
    c.create_line(x-2, ((float(high)*multi)*-1) +ofs, x-2,((float(low)*multi)*-1)+ofs, fill=colour, tags=('chart'))

def indiDrawoor(indi, x, last, new, multi, ofs, canvas, colour):
    if type(last) != list:
        last,new=[last],[new]
    for i in range(len(last)):
        canvas.create_line(x-5, ((float(last[i])*multi)*-1)+ofs, 
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
    CLEAROOR('change')
    for row in range(len(indicators.data[pair]['ohlc'])):
        if x == 0:
            pass
        else:

            chartDrawoor(x, indicators.data[pair]['ohlc'][row][1], indicators.data[pair]['ohlc'][row][2], 
                        indicators.data[pair]['ohlc'][row][3],indicators.data[pair]['ohlc'][row][4], chartMulti, chartOffset,
                        chartColour[0] if float(indicators.data[pair]['ohlc'][row][4])>float(indicators.data[pair]['ohlc'][row][1]) else 
                        chartColour[1])

            for i in activeIndicators:
                if activeIndicators[i]['active']:
                    if i in OVERLAY:
                        indiDrawoor(i, x, lasts[i], indicators.data[pair][i][row],chartMulti, chartOffset, c, activeIndicators[i]['colour'])
                    elif i in STUDIES and i != 'macd':
                        indiDrawoor(i, x, lasts[i], indicators.data[pair][i][row],1, 100, studyHolder[i], activeIndicators[i]['colour'])
                    else:
                        indiDrawoor(i, x, lasts[i], indicators.data[pair][i][row],mcdMULTI, mcdPLUS, studyHolder[i], activeIndicators[i]['colour'])

        x+=5
        for i in activeIndicators:
            lasts.update({i:indicators.data[pair][i][row]})
    if activeIndicators['rsi']['active']:
        h = studyHolder['rsi'].create_line(0, 20, 5760, 20, fill='red', tag=('rsi'))
        l = studyHolder['rsi'].create_line(0, 80, 5760, 80, fill = 'green', tag=('rsi'))
    if activeIndicators['stoch']['active']:
        h = studyHolder['stoch'].create_line(0, 20, 5760, 20, fill='red', tag=('stoch'))
        l = studyHolder['stoch'].create_line(0, 80, 5760, 80, fill = 'green', tag=('stoch'))
    

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
        c.focus_set()
    else:
        messagebox.showerror('Warning', 'not a valid '+setting+' try again')


def keyup(e):
    if e.keysym[0] == 's':
        if c.find_withtag('pixel1') != ():
            c.delete('pixel1')
            c.unbind('<Motion>')
            print('up', e)
    if "Shift" in e.keysym:
        if c.find_withtag('pixel') != ():
            c.delete('pixel')
            c.unbind('<Motion>')
            print('up', e)

def keydown(e):
    # print('down', e)
    global SCALERPAIR
    if e.keysym[0] == 's':
        if c.find_withtag('pixel1') == ():
            c.create_line(0,0,1,1,tags=('pixel1'))
            print('down', e)
            SCALERPAIR = (e.x, e.y)
            c.bind('<Motion>', motion_)
    if 'Shift' in e.keysym:
        if c.find_withtag('pixel') == ():
            c.create_line(0,0,1,1,tags=('pixel'))
            print('down', e)
            SCALERPAIR = (e.x, e.y)
            c.bind('<Motion>', lambda x: motion_(x, 'mover'))


STUDIES = ['dmi', 'stoch', 'macd', 'rsi']
OVERLAY = ['chan', 'sma', 'ema']

pMap,interval,pair,activeIndicators,chartColour = startoor()

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
c.bind("<KeyPress>", keydown)
c.bind("<KeyRelease>", keyup,)
c.focus_set()
DRAWOOR()

top.mainloop()




