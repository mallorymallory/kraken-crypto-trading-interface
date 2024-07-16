import os.path
import csv
import sys
import traceback
import threading
import krakenex
import pprint
import time

class INDI(threading.Thread):

    def __init__(self, DATA, FULL=False, CURRENT=False):
        
        self.k = krakenex.API()
        self.interval = None
        self.full = FULL
        self.current = CURRENT
        self.funcMap = INDI.__dict__
        threading.Thread.__init__(self)
        if type(DATA) != list:
            raise Exception ('data must be list of pairs [pair,...]')
        self.data = {}
        self.setup = False
        self.pairmap = self.getPairmap()

        for pair in DATA:
            self.data.update({pair:{'ohlc':None,
                                      'rsi':None,
                                      'sma':None,
                                      'ema':None,
                                      'chan':None,
                                      'dmi':None,
                                      'stoch':None,
                                      'macd':None}})


    def pairSetter(self, list, change=True):
        if change:
            self.data = {}
        for pair in list:
            self.data.update({pair:{'ohlc':None,
                                        'rsi':None,
                                        'sma':None,
                                        'ema':None,
                                        'chan':None,
                                        'dmi':None,
                                        'stoch':None,
                                        'macd':None}})

    def getPairmap(self):
        pairmap = {}
        AP = None
        for i in range(2):
            try:
                AP = self.k.query_public('AssetPairs')['result']
                for i in AP:
                    pairmap.update({AP[i]['altname']:i,
                                    AP[i]['wsname']:i,
                                    i:i,
                                    AP[i]['altname'].lower():i,
                                    AP[i]['wsname'].lower():i,
                                    i.lower():i,

                                    })
                pairmap.update({'BTCUSD':'XXBTZUSD',
                                'BTC/USD':'XXBTZUSD',
                                'BTCUSD'.lower():'XXBTZUSD',
                                'BTC/USD'.lower():'XXBTZUSD',
                                    })
                    
            except Exception as F:
                print(F)
                with open('OHLCErrors.csv', 'a', newline='') as FF:
                    ff = csv.writer(FF)
                    ff.writerow([time.time(), AP, F, traceback.format_exc()])
            else:
                break

        return pairmap


    def getNew(self, indicators, interval=None, data=None):
        if interval == None:
            if self.interval == None:
                raise('no interval set')
        else:
            self.interval=interval
        res = None
        for pair in self.data:
##            print(pair)
            if data == None:
                for x in range(2):
                    try:
                        res = self.k.query_public('OHLC', {'pair':pair, 'interval':self.interval})
                        ohlc = res['result'][self.pairmap[pair]]
                        
                    except Exception as f:
                        print(f)
                        with open('OHLCErrors.csv', 'a', newline='') as FF:
                            ff = csv.writer(FF)
                            ff.writerow([time.time(), res, f, traceback.format_exc()])

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

    def getSTOCH(self, ohlc_data, period=14):
        
        def moving_average(values, window):
            if len(values) < window:
                return 0
            return sum(values[-window:]) / window
        
        stochastic_data = []
        for i in range(len(ohlc_data)):
            if i < period - 1:
                # Not enough data to calculate %K
                stochastic_data.append([0, 0])
            else:
                high_14 = max([float(data[2]) for data in ohlc_data[i - period+1 :i]])
                low_14 = min([float(data[3]) for data in ohlc_data[i - period+1:i]])
                close = float(ohlc_data[i][4])
                
                if high_14 == low_14:
                    # Avoid division by zero
                    percent_k = 100
                else:
                    percent_k = ((close - low_14) / (high_14 - low_14)) * 100
                
                stochastic_data.append([percent_k, 0])
        
        percent_k_values = [data[0] for data in stochastic_data]
        
        for i in range(len(stochastic_data)):
            if stochastic_data[i][0] is not 0 and i >= period +3:
                stochastic_data[i][1] = moving_average(percent_k_values[i-3:i], 3)
            else:
                stochastic_data[i][1] = 0
        
        return stochastic_data
