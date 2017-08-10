# -*- coding: utf-8 -*-
"""
Created on Fri Jun 2 22:15:04 2017
Scribled Attenuation Measurement System Complete

@author: nchitta
"""
import visa,matplotlib.pyplot as plt,time, csv, scipy.stats as st, pandas as pd, numpy as np, warnings,matplotlib,math as mt,win32com.client
#Lets Initialize our resource manager to speak with the devices
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()
#Just checking if we are able to access both the instruments correctly.
output_dir = "Data/Calibration/"+time.strftime('%Y%m%d-%H%M%S')
def mkdir_p(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    from errno import EEXIST
    from os import makedirs,path
    try:
        makedirs(mypath)
    except OSError as exc: # Python >2.5
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else: raise
#
mkdir_p(output_dir)
log = open(output_dir+'/Log.txt', "w")
#Intialize resources
#sr844=rm.open_resource('GPIB0::8::INSTR') #Needed when we are using Lock in instead of 4396B Spectrum Analyzer
fluke6060b=rm.open_resource('GPIB0::2::INSTR')
agi8648a=rm.open_resource('GPIB0::19::INSTR')
agi4396b=rm.open_resource('GPIB0::17::INSTR')
rudat6k = win32com.client.Dispatch("mcl_RUDAT.USB_DAT")
rudat6k.connect()# COnnecting with the RUDAT6K using DLL Libraries. Use rudat6k.Read_Att(attdef) to read the current attenuation setting if required
attdef=0.0# For initializing the registers in the USB control devices.
freq1=float(raw_input('Please Input Frequency to test in MHZ..'))
IFFreq=int(raw_input('Please make your choice of IF - Enter 0 for 100 KHz and Enter 1 for 30 MHz: '))
notr=float(raw_input('Please input the number of trials '))
freqIF=['0.0001 MHZ','30 MHZ']
freq2=freq1+float(freqIF[IFFreq].split(' ')[0])
freq_hz=float(freqIF[IFFreq].split(' ')[0])*pow(10,6)
agi4396b.write("SENS:FREQ:CENT %s" % freq_hz)
span_val=100000# Setting Span Default to be 1 KHz
agi4396b.write("SENS:FREQ:SPAN %s" % span_val)
#agi4396b.write("REFV -40")# Setting the reference value to -40 dBm such that we can see values during the lower end as well.
agi4396b.write("REFV 0")# Setting the reference value to 0 dBm If you are constantly seeing the Overload Error on Input S in the Spectrum Analyzer.
fluke6060b.write("FR %s MZ" % freq1)
pow1=0
pow2=10
it=0
refdata=[]
agi8648a.write("OUTPUT 719;FREQ:CW %s MHZ" % freq2)
agi8648a.write("POW:AMPL %s DBM" % pow2)    
print("Attenuation Comparison list generation in Progress...")
Att_list=[x*0.25 for x in range(0,241)]#241 to get the final value around 60 dB 
pin=[]
pout=[]
while it<len(Att_list):
        fluke6060b.write("AP %s DBM" %pow1)
        fluke6060b.write("RO 1")
        time.sleep(5)
        rudat6k.SetAttenuation(Att_list[it])
        xval=[]
        yval=[]
        trial=0
        while trial<notr:
            time.sleep(2)
            agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
            agi4396b.write("MKR ON")
            agi4396b.write("SEAM PEAK") #for peak search function
            xval.append(float(agi4396b.query("MKRPRM?")))
            yval.append(float(agi4396b.query("MKRVAL?")))
            trial+=1
        xval1=np.mean(xval)
        yval1=np.mean(yval)
        refdata.append([xval1,pow1,yval1])
        pin.append(pow1)
        pout.append(yval1)
        it+=1        
        time.sleep(5)
        agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
        trace_val=agi4396b.query("OUTPDTRC?")
        trace_val_data=[float(j) for j in trace_val.strip('{}').split(',')]
        pts=list(xrange(len(trace_val_data)))
        fig1=plt.figure(figsize=(12,8))
        ax=fig1.add_subplot(1,1,1)
        ax.plot(pts,trace_val_data, 'b', label='power %s dBm' %yval1)
        ax.plot(pts,trace_val_data, 'b', label='CenterFreq %s MHZ' %xval1)
        legend = ax.legend(loc='upper right', shadow=True)
        plt.savefig(output_dir+'/AMSSAOut_AttenCal'+'image'+time.strftime('%Y%m%d-%H%M%S')+'.png')
        fluke6060b.write("RO 0")
else: 
        if it>=len(Att_list):
            print('Power In and Power out calculated for ')
            with open(output_dir+'/AMSRefata_Outp'+time.strftime('%Y%m%d-%H%M%S')+'.csv',"wb") as f:
                writer = csv.writer(f)
                writer.writerows(refdata)
            fig=plt.figure(figsize=(12,8))
            ax = fig.add_subplot(1,1,1)
            ax.plot(pin, pin, 'g')
            ax.plot(pin, pout, 'r')
            ax.set_xlabel('Input Power')
            ax.set_ylabel('Output Power')
print("Attenuation Comparison list generation Complete...")
#Now we are actually trying to just measure the power values when attenuator is connected and not connected to make RF Subs value and also the Alogorithm Checked Value.
fluke6060b.close
agi4396b.close
agi8648a.close
rudat6k.Disconnect