import tkinter as tk
import time
from indicators import INDI

def motion(event):
    x,y = event.x, event.y
    print(x,y)

pMap = {'15':[16,48],
        '10080':[16,48],
        '60':[4,24],
        '240':[6,42],
        '5':[12,48]}

interval = 15
pair = 'XBTUSD'

indicators = INDI([[pair, interval, pMap[str(interval)]]])
indicators.getNew()

profThresh= 15

def xview(*args):
    c.xview(*args)
    B.xview(*args)
    rsican.xview(*args)

top = tk.Tk()
top.bind('<Motion>', motion)

canframe = tk.Frame(top)
canframe.pack()
xscroll = tk.Scrollbar(canframe, orient='horizontal')


c = tk.Canvas(canframe, bg='black', height = 500, width=720, scrollregion=(0,0,5760,5760))
B = tk.Canvas(canframe, bg='black', height= 100, width=720, scrollregion=(0,0,5760,5760))
rsican = tk.Canvas(canframe, bg='black', height= 100, width=720,  scrollregion=(0,0,5760,5760))

xscroll.pack(side='bottom', fill='x')
xscroll.config(command = xview)

c.config(xscrollcommand=xscroll.set)
c.pack()
B.config(xscrollcommand=xscroll.set)
B.pack()
rsican.config(xscrollcommand=xscroll.set)
rsican.pack()
while True:
    if indicators.setup:
        print(len(indicators.data[pair]['dmi']), len(indicators.data[pair]['chan']), len(indicators.data[pair]['macd']))#, len(indicators.data[pair]['sma']))
        if len(indicators.data[pair]['dmi']) == len(indicators.data[pair]['chan']):# == len(indicators.data[pair]['macd']):
            x = 0
            lendiff = len(indicators.data[pair]['macd']) - len(indicators.data[pair]['dmi']) 
            smallest = float(min(indicators.data[pair]['chan'], key=lambda z: float(z[0]))[0])
            biggest = float(max(indicators.data[pair]['chan'], key=lambda z: float(z[1]))[1])
            pdiff = biggest-smallest
            multi = 300/pdiff
            ummm = (biggest * multi) + 50
            
            mcdBIG = max(indicators.data[pair]['macd'][16:])[0]#, key=lambda bbb: float(bbb[0]))
            mcdSMOL = min(indicators.data[pair]['macd'][16:])[0]#, key=lambda bbb: float(bbb[0]))
            mcdDIFF = mcdBIG - mcdSMOL
            mcdMULTI = 5000/mcdDIFF
            mcdPLUS = 50

    ##            if (biggest*multi*-1) + multi < 0:
    ##                raise Exception('hmmmm')

            Trades = []
            lastLong = False
            lastShort = False
            longPrice = None
            bestLongFill = None
            shortPrice = None
            bestShortFill = None
            for row in range(len(indicators.data[pair]['chan'])):
                if x == 0:
                    pass
                else:
                    
                    
###                    sma200 = c.create_line(x-8, ((float(lastsma200)*multi)*-1)+ummm, x,((float(indicators.data[pair]['sma'][row+lendiff][2])*multi)*-1)+ummm, fill='magenta4', )
                    
                    if indicators.data[pair]['chan'][row][4] < lastPrice:
                        canfill = 'red'
                    elif indicators.data[pair]['chan'][row][4] > lastPrice:
                        canfill = 'green'
                    else:
                        canfill = 'white'
                    Price = c.create_rectangle(x-7, ((float(lastPrice)*multi)*-1) +ummm, x-1,((float(indicators.data[pair]['chan'][row][4])*multi)*-1)+ummm, fill=canfill, )
                    wicks = c.create_line(x-4, ((float(indicators.data[pair]['chan'][row][3])*multi)*-1) +ummm, x-4,((float(indicators.data[pair]['chan'][row][2])*multi)*-1)+ummm, fill=canfill, )
                    midChan = c.create_line(x-8, ((float(indicators.data[pair]['chan'][row][5])*multi)*-1)+ummm, x,((float(indicators.data[pair]['chan'][row][5])*multi)*-1)+ummm, fill='blue', )
                    lowChan = c.create_line(x-8, ((float(indicators.data[pair]['chan'][row][0])*multi)*-1)+ummm, x,((float(indicators.data[pair]['chan'][row][0])*multi)*-1)+ummm, fill='turquoise1', )
                    highChan = c.create_line(x-8, ((float(indicators.data[pair]['chan'][row][1])*multi)*-1)+ummm, x,((float(indicators.data[pair]['chan'][row][1])*multi)*-1)+ummm, fill='magenta2', )
                    # sma50 = c.create_line(x-8, ((float(lastsma50)*multi)*-1)+ummm, x,((float(indicators.data[pair]['sma'][row+lendiff][0])*multi)*-1)+ummm, fill='magenta4', )
                    # sma100 = c.create_line(x-8, ((float(lastsma100)*multi)*-1)+ummm, x,((float(indicators.data[pair]['sma'][row+lendiff][1])*multi)*-1)+ummm, fill='magenta3', )
                    longDMI = B.create_line(x-8, (float(lastlongDMI)*-1)+75, x,(float(indicators.data[pair]['dmi'][row][0])*-1)+75, fill='green', )
                    shortDMI = B.create_line(x-8, (float(lastshortDMI)*-1)+75, x,(float(indicators.data[pair]['dmi'][row][1])*-1)+75, fill='red', )
#                    emaS = c.create_line(x-8, ((float(lastemaS)*multi)*-1)+ummm, x,((float(ema.results[0][row+lendiff])*multi)*-1)+ummm, fill='magenta4', )
#                    emaL = c.create_line(x-8, ((float(lastemaL)*multi)*-1)+ummm, x,((float(ema.results[1][row+lendiff])*multi)*-1)+ummm, fill='magenta3', )

                    macdT = rsican.create_line(x-8, ((float(lastmcdTrig)*mcdMULTI)*-1)+mcdPLUS, x,((float(indicators.data[pair]['macd'][row+lendiff][0])*mcdMULTI)*-1)+mcdPLUS, fill='blue', )
                    macdS = rsican.create_line(x-8, ((float(lastmcdSig)*mcdMULTI)*-1)+mcdPLUS, x,((float(indicators.data[pair]['macd'][row+lendiff][1])*mcdMULTI)*-1)+mcdPLUS, fill='white', )
                    rrrsi = rsican.create_line(x-8, (float(lastrsi)*-1)+100, x,(float(indicators.data[pair]['rsi'][row])*-1)+100, fill='magenta', )                  
#                    print(indicators.data[pair]['chan'][row][4], float(indicators.data[pair]['sma'][row+lendiff][0]), indicators.data[pair]['chan'][row][4] - float(indicators.data[pair]['sma'][row+lendiff][0]))
     
                x+=8
                lastmcdTrig = indicators.data[pair]['macd'][row+lendiff][0]
                lastmcdSig = indicators.data[pair]['macd'][row+lendiff][1]
                
                lastsma50 = indicators.data[pair]['sma'][row+lendiff][0]
                lastsma100 = indicators.data[pair]['sma'][row+lendiff][1]
#                lastemaS = ema.results[0][row+lendiff]
#                lastemaL = ema.results[1][row+lendiff]
##                lastsma200 = indicators.data[pair]['sma'][row+lendiff][2]
                lastrsi = indicators.data[pair]['rsi'][row]
                lastlongDMI = indicators.data[pair]['dmi'][row][0]
                lastshortDMI = indicators.data[pair]['dmi'][row][1]

                lastPrice = indicators.data[pair]['chan'][row][4]
                lastmidChan = indicators.data[pair]['chan'][row][5]
                lastlowChan = indicators.data[pair]['chan'][row][0]
                lasthighChan = indicators.data[pair]['chan'][row][1]


            h = rsican.create_line(0, 20, 5760, 20, fill='red')
            l = rsican.create_line(0, 80, 5760, 80, fill = 'green')
            break           
        else:
            raise Exception('hwat')
    else:
        time.sleep(1)
        


top.mainloop()




