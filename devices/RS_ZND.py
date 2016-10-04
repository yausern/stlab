import visa
import numpy as np
import time
from stlab.devices.instrument import instrument

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class RS_ZND_pna(instrument):
    def __init__(self,addr='TCPIP::192.168.1.149::INSTR',reset=True,verb=True):
        super(RS_ZND_pna, self).__init__(addr,reset,verb)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None 
        self.id()
        self.twoportmode = False
        self.oneportmode = False
        if reset:
            self.write('INIT:CONT 0') #Turn off continuous mode
            self.TwoPort()
    def SinglePort(self):
        self.write('CALC:PAR:DEL:ALL') #Delete default trace
        tracenames = ['\'TrS11\'']
        tracevars = ['\'S11\'']
        for name,var in zip(tracenames,tracevars):
            self.write('CALC:PAR:SDEF ' + name + ', ' + var) #Set 2 traces and measurements
            self.write('DISP:WIND1:TRAC:EFE ' + name)
        self.twoportmode = False
        self.oneportmode = True
    def TwoPort(self):
        self.write('CALC:PAR:DEL:ALL') #Delete default trace
        tracenames = ['\'TrS11\'','\'TrS21\'']
        tracevars = ['\'S11\'','\'S21\'']
        windows = ['1','2']
        for name,var,wind in zip(tracenames,tracevars,windows):
            self.write('DISP:WIND'+wind+':STAT ON')
            self.write('CALC:PAR:SDEF ' + name + ', ' + var) #Set 2 traces and measurements
            self.write('DISP:WIND'+wind+':TRAC1:FEED ' + name)
        self.twoportmode = True
        self.oneportmode = False
    def SetRange(self,start,end):
        self.SetStart(start)
        self.SetEnd(end)
    def SetCenterSpan(self,center,span):
        self.SetCenter(center)
        self.SetSpan(span)
    def SetStart(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:STAR '+mystr
        self.write(mystr)
    def SetEnd(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:STOP '+mystr
        self.write(mystr)
    def SetCenter(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:CENT '+mystr
        self.write(mystr)
    def SetSpan(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:SPAN '+mystr
        self.write(mystr)
    def SetIFBW(self,x):
        mystr = numtostr(x)
        mystr = 'BAND '+mystr
        self.write(mystr)
    def SetPower(self,x):
        mystr = numtostr(x)
        mystr = 'SOUR:POW '+mystr
        self.write(mystr)
    def GetPower(self):
        mystr = 'SOUR:POW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp
    def SetPoints(self,x):
        mystr = '%d' % x
        mystr = 'SWE:POIN '+mystr
        self.write(mystr)
    def Measure2ports(self,autoscale = True):
        if not self.twoportmode:
            self.TwoPort()
        print((self.query('INIT;*OPC?'))) #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND1:TRAC1:Y:AUTO ONCE') #Autoscale both traces
            self.write('DISP:WIND2:TRAC1:Y:AUTO ONCE')
        #Read measurement (in unicode strings). READS DATA WITH ACTIVE CALIBRATION APPLIED
        frec = self.query('CALC:DATA:STIM?')
        S11 = self.query('CALC:DATA:TRAC? \'TrS11\', SDAT')
        S21 = self.query('CALC:DATA:TRAC? \'TrS21\', SDAT')
        frec = np.array(list(map(float, frec.split(','))))
        S11 = np.array(list(map(float, S11.split(','))))
        S21 = np.array(list(map(float, S21.split(','))))
        S11re = S11[::2]  #Real part
        S11im = S11[1::2] #Imaginary part
        S21re = S21[::2]  #Real part
        S21im = S21[1::2] #Imaginary part
        CalOn = bool(int(self.query('CORR?')))
        if CalOn:
            S11uc = self.query('CALC:DATA:TRAC? \'TrS11\', NCD')
            S21uc = self.query('CALC:DATA:TRAC? \'TrS21\', NCD')
            S11reuc = S11uc[::2]  #Real part
            S11imuc = S11uc[1::2] #Imaginary part
            S21reuc = S21uc[::2]  #Real part
            S21imuc = S21uc[1::2] #Imaginary part
            return (frec,S11re, S11im, S21re, S21im, S11reuc, S11imuc, S21reuc, S21imuc)
        else:
            return (frec,S11re, S11im, S21re, S21im)
    def Measure1port(self,autoscale = True):
        pass
        if not self.oneportmode:
            self.SinglePort()
        print((self.query('INIT;*OPC?'))) #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND1:TRAC1:Y:AUTO ONCE') #Autoscale trace
        #Read measurement (in unicode strings).  READS DATA WITH ACTIVE CALIBRATION APPLIED
        frec = self.query('CALC:DATA:STIM?')
        S11 = self.query('CALC:DATA:TRAC? \'TrS11\', SDAT')
        #Convert to numpy arrays
        frec = np.array(list(map(float, frec.split(','))))
        S11 = np.array(list(map(float, S11.split(','))))
        S11re = S11[::2]  #Real part
        S11im = S11[1::2] #Imaginary part
        CalOn = bool(int(self.query('CORR?')))
        if CalOn:
            S11uc = self.query('CALC:DATA:TRAC? \'TrS11\', NCD')
            S11uc = np.array(list(map(float, S11uc.split(','))))
            S11reuc = S11uc[::2]  #Real part
            S11imuc = S11uc[1::2] #Imaginary part
            return (frec,S11re,S11im,S11reuc,S11imuc)
        else:
            return (frec,S11re,S11im)
    def LoadCal (self, calfile, channel = 1):
        mystr = "MMEM:LOAD:CORR " + str(channel) + ",'" + calfile + "'"
        self.write(mystr)
    def CalOn (self):
        mystr = "CORR ON"
        self.write(mystr)
    def CalOff (self):
        mystr = "CORR OFF"
        self.write(mystr)

