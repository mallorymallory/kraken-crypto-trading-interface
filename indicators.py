import os.path
import csv
import sys
import traceback
from websocket import create_connection
import threading
import krakenex
import pprint
import time

class INDI(threading.Thread):

    def __init__(self, DATA, FULL=False, CURRENT=False):
        
        self.k = krakenex.API()
        pairmap = self.k.query_public('AssetPairs')
        self.full = FULL
        self.current = CURRENT

        self.funcMap = INDI.__dict__
        # print(self.funcMap)
        threading.Thread.__init__(self)
        if type(DATA) != list:
            raise Exception ('data must be list of lists [[pair, interval, period],]')
        
        self.data = {}

        self.setup = False

        for opt in DATA:
            self.data.update({opt[0]:{'interval':opt[1],
                                      'period':opt[2],
                                      'rsi':None,
                                      'sma':None,
                                      'ema':None,
                                      'chan':None,
                                      'dmi':None,
                                      'macd':None}})
            for y in list(pairmap['result']):
                parmp = pairmap['result'][y]
                if opt[0] == parmp['altname'] and y[-2:] != '.d':
                    self.data[opt[0]].update({'fullname':y, 'wsname':parmp['wsname']})

    def getNew(self, indicators, data=None):
        for pair in self.data:
##            print(pair)
            if data == None:
                for x in range(2):
                    try:
                        res = self.k.query_public('OHLC', {'pair':pair, 'interval':self.data[pair]['interval']})
                        ohlc = res['result'][self.data[pair]['fullname']]
                        
                    except Exception as f:
                        try:
                            print(f)
                            with open('OHLCErrors.csv', 'a', newline='') as FF:
                                ff = csv.writer(FF)
                                ff.writerow([time.time(), res, f, traceback.format_exc()])
                        except Exception as F:
                            print(F)
                            with open('OHLCErrors.csv', 'a', newline='') as FFF:
                                fff = csv.writer(FFF)
                                fff.writerow([time.time(), '', F, traceback.format_exc()])
                    else:
                        break
            else:
                ohlc = data['result'][pair]

            for i in indicators:
                self.data[pair].update({i:self.funcMap['get'+i.upper()](self, ohlc, indicators[i]['period'])})

            self.data[pair].update({'ohlc':ohlc,'ctime':ohlc[-1][0]})
            self.setup = True


#-------------------------------Chandelier Exits----------------------------------------------------------------------------------    
#-------------------------------Chandelier Exits----------------------------------------------------------------------------------
#-------------------------------Chandelier Exits----------------------------------------------------------------------------------
    def getCHAN(self, ohlc, period):                
        closes = []
        ATR = []
        PC = float(ohlc[0][4])
        for candle in ohlc[1:]:
            CH = float(candle[2])
            CL = float(candle[3])
                        
            atr = max([(CH-CL), abs(CH - PC), abs(CL - PC)])              
            ATR.append(atr)

            PC = float(candle[4])
            closes.append(PC)
            
        SATR = []
        if len(ATR) == len(closes):
            print('YAY')
        else:
            print('NAY')
            
        sumatr = sum(ATR[0:period])
        multi = 2/(period+1)
        for x in ATR[period:]:
            Satr = (x-sumatr) * multi + sumatr
            SATR.append(Satr)
            sumatr = Satr
        
        hl = []  
        for x in range(len(closes[period:])):
            num = x+period
#                print(closes[x:num])
            hl.append((max(closes[x:num]), min(closes[x:num])))
        
        
        exits = []
        if len(SATR) == len(hl):
#                print('not yikes')
            for z in range(len(SATR)):
                exits.append([hl[z][0]-SATR[z], hl[z][1]+SATR[z]])                
        else:
            print('yikes', len(SATR), len(hl))
            
        results = [[float(exits[0][0]),float(exits[0][0]),float(exits[0][0])]]*(period+1)
        for i in range(len(exits)):
            results.append([float(exits[i][0]), float(exits[i][1]), float((exits[i][0]+exits[i][1])/2)]) #, float(((exits[i][0]+exits[i][1])/2)-float(ohlc[i+period+1][4]))])

        return results
    
#-------------------------------MACD----------------------------------------------------------------------------------     
#-------------------------------MACD----------------------------------------------------------------------------------     
#-------------------------------MACD----------------------------------------------------------------------------------     

    def getMACD(self, ohlc, period):
        
        closes = []
        for i in ohlc:
            closes.append(float(i[4]))

        results = []
        self.MACD = []
        self.emaresults = []
        self.signal = []
        
        for i in period:
            initSMA = sum(closes[0:i])/i
            multi = 2/(i+1)
            resi = []
            for iii in range(i):
                resi.append(0)
            for x in closes[i:]:
                initSMA = ((x - initSMA)*multi)+ initSMA
                resi.append(initSMA)

            self.emaresults.append(resi)
        
        if len(self.emaresults[0]) == len(self.emaresults[1]):
            for ii in range(len(self.emaresults[0])):
                self.MACD.append(self.emaresults[0][ii] - self.emaresults[1][ii])
                
            print(len(self.MACD))    
            signalSMA = sum(self.MACD[:period[0]])/period[0]
            signalMulti = 2/(period[0]+1)
            
            for II in range(period[0]):
                results.append([0,0])
            for I in self.MACD[period[0]:]:
                signalSMA = ((I - signalSMA)*signalMulti)+signalSMA
                results.append([I, signalSMA])
                
        else:
            print('fuck')

        return results

#-------------------------------RSI----------------------------------------------------------------------------------     
#-------------------------------RSI----------------------------------------------------------------------------------     
#-------------------------------RSI----------------------------------------------------------------------------------     

    def getRSI(self, ohlc, period):
                
        closes = []
        for i in ohlc:
            closes.append(float(i[4]))

        ups = []
        downs = []
        last = closes[0]
        for x in closes[1:]:
            chng = x-last
            if chng <= 0:
                    ups.append(0)
                    downs.append(abs(chng))
            elif chng >= 0:
                    ups.append(abs(chng))
                    downs.append(0)
            last = x
        smaups = sum(ups[0:period])/period
        smadowns = sum(downs[0:period])/period
        lU = ups[0]
        lD = downs[0]
        for x in ups[1:period]:
            smaups = (lU*(period-1)+x)/period
            lU = smaups
        for x in downs[1:period]:
            smadowns = (lD*(period-1)+x)/period
            lD = smadowns
            
        results=[0]*(period+1)
        if len(ups) != len(downs):
            raise Exception ('Error, something went wrong')
        else:
            lup = smaups
            ldown = smadowns
            for x in range(len(ups[period:])):
                lup = (lup*(period-1)+ups[period+x])/period
                ldown = (ldown*(period-1)+downs[period+x])/period
                results.append(self.calc(lup, ldown))

        return results
   

    def calc(self, avgU, avgD):
        if avgU == 0:
            avgU = 0.0000000001
        if avgD == 0:
            avgD = 0.0000000001
        Rs = avgU / avgD
        rsi = 100 - (100/(1+Rs))
        return rsi



#-------------------------------DMI---------------------------------------------------------------------------------    
#-------------------------------DMI---------------------------------------------------------------------------------    
#-------------------------------DMI---------------------------------------------------------------------------------    


    def getDMI(self, ohlc, period):
                
        DMPLUS = []
        DMMINUS = []
        ATR = []
        PH = float(ohlc[0][2])
        PL = float(ohlc[0][3])
        PC = float(ohlc[0][4])
        for candle in ohlc[1:]:
            CH = float(candle[2])
            CL = float(candle[3])
            
            um = CH - PH
            dm = PL - CL
            
            if um > dm and um > 0:
                dmPLUS = um
            else:
                dmPLUS = 0
                
            if dm > um and dm > 0:
                dmMINUS = dm
            else:
                dmMINUS = 0
                
            atr = max([(CH-CL), abs(CH - PC), abs(CL - PC)])
            
            DMPLUS.append(dmPLUS)
            DMMINUS.append(dmMINUS)
            ATR.append(atr)
            
            PH = CH
            PL = CL
            PC = float(candle[4])
            
        SATR = []
        SDMP = []
        SDMM = []
        
        sumatr = sum(ATR[0:period])
        multi = 2/(period+1)
        for x in ATR[period:]:
            Satr = (x-sumatr) * multi + sumatr
            SATR.append(Satr)
            
            sumatr = Satr
        
        sumdmp = sum(DMPLUS[0:period])
        for xx in DMPLUS[period:]:
            Sdmp = (xx - sumdmp) * multi + sumdmp
            SDMP.append(Sdmp)
            sumdmp = Sdmp
            
        
        sumdmm = sum(DMMINUS[0:period])
        for xxx in DMMINUS[period:]:
            Sdmm = (xxx - sumdmm) * multi + sumdmm
            SDMM.append(Sdmm)
            sumdmm = Sdmm    
        
        DIP = []
        DIM = []
        
        if len(SATR) == len(SDMP) and len(SDMP) == len(SDMM):
            for x in range(len(SATR)):
                dip = (SDMP[x] / SATR[x]) * 100
                dim = (SDMM[x] / SATR[x]) * 100
                
                DIP.append(dip)
                DIM.append(dim)
                
        results = [[0,0]]*(period+1)    
        for i in range(len(DIP)):
            results.append([DIP[i], DIM[i]]) #(DIP[i]-DIM[i])
                
        return results 



#-------------------------------SMA---------------------------------------------------------------------------------    
#-------------------------------SMA---------------------------------------------------------------------------------    
#-------------------------------SMA---------------------------------------------------------------------------------    

    def getSMA(self, ohlc, period):
        
        closes = []
        for i in ohlc:
                closes.append(float(i[4]))

        results = []
        for x in range(len(closes)):
            rs= []
            for y in period:
                if x < y-1:
                    rs.append(0)
                else:
                    rs.append(sum(closes[x-(y):x])/y)
                    
                
            results.append(rs)
        return results


# a = INDI([['XBTUSD', 15, [4, 16]], ['LTCUSD', 240, [6,42]]])
# print(a.data)
# a.getNew()
# while a.setup != True:
#     print(a.setup)
#     time.sleep(0.5)
# for j in a.data:
#     for i in a.data[j]:
#         if i in ['rsi', 'dmi', 'chan', 'macd', 'sma']:
#             print(j, i, a.data[j][i][-1])
#     print(j, 'ctime', a.data[j]['ctime'])
