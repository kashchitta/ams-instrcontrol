# -*- coding: utf-8 -*-
"""
Created on Thu Apr 06 08:39:03 2017

@author: NikhilChandKashyap
"""

# In this program we are trying to charecterize IMD for the given setup and identify P1DB and P3DB points
import visa,time,csv,matplotlib.pyplot as plt
#Lets Initialize our resource manager to speak with the devices
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()
#Just checking if we are able to access both the instruments correctly.
#fluke6060b=rm.open_resource('GPIB0::2::INSTR')
u2043x=rm.open_resource('USB0::0x2A8D::0x1D01::MY55190016::INSTR')
agi8648a=rm.open_resource('GPIB0::19::INSTR')
#
u2043x.timeout = 50000
pow1=-65
reading=[]
pin=[]
pout=[]
#u2043x=rm.open_resource('USB0::0x2A8D::0x1D01::MY55190016::INSTR')
freq1=raw_input('Please Input Frequency in MHZ..\n')
#pow1=raw_input('Please Input Power in dBm..\n')
agi8648a.write("OUTPUT 719;FREQ:CW %s MHZ" % freq1)
#u2043x.write("CALibration:ZERO:AUTO;*WAI;*OPC?")
#u2043x.write("CALibration:ALL;*WAI;*OPC?")
#time.sleep(15)
#u2043x.write("*WAI")
#u2043x.write("FORM:DATA ASCII")
#ready=int(u2043x.query("*OPC?"))
#print("Before Loop ready: %s" % ready)
#fluke6060b.write("FR %s MZ" % freq1)
#if ready==1:
while pow1<=10:
    #print("in Loop %s" % pow1)
    
    agi8648a.write("POW:AMPL %s DBM" % pow1)    
    #fluke6060b.write("AP %s DBM" %pow1)
    agi8648a.write(":OUTP:STAT ON")
    time.sleep(1)
#    fluke6060b.write("RO 1")
    #u2043x.read()
    yval=u2043x.query("MEASure:SCALar:POWer:AC:RELative?")
    reading.append([pow1,yval])
    pin.append(pow1)
    pout.append(yval)
    pow1=pow1+1
    u2043x.write("*RST")
    agi8648a.write(":OUTP:STAT OFF")
 #   fluke6060b.write("RO 0")
else: 
    if pow1>=10:
        print('Various Signal Generator Powers Measured')
        with open('PwrSensrOutp'+time.strftime('%Y%m%d-%H%M%S')+'.csv',"wb") as f:
            writer = csv.writer(f)
            writer.writerows(reading)
    else:
        print('There is some trouble plz recheck results')
fig=plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
ax.plot(pin, pout)
ax.set_xlabel('Input Power')
ax.set_ylabel('Output Power')
plt.savefig('PowerSenseCalc.png')
#agi8648a.close
fluke6060b.close
u2043x.close