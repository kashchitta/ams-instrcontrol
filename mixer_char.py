# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 16:20:23 2017
@author: nchitta
"""
# In this program we are trying to plot all the Power readings of Spectrum Analyzer based on the 
import visa, matplotlib.pyplot as plt,time, csv,numpy as np
#Lets Initialize our resource manager to speak with the devices
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()
#Just checking if we are able to access both the instruments correctly.
fluke6060b=rm.open_resource('GPIB0::2::INSTR')
agi4396b=rm.open_resource('GPIB0::17::INSTR')
agi8648a=rm.open_resource('GPIB0::19::INSTR')
#agi8648a=rm.open_resource('GPIB0::19::INSTR')
output_dir = "Data/Mixer_Char/"+time.strftime('%Y%m%d-%H%M%S')
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
log.write("Initializing devices and Datastorage Memory Successful \n")
log.write("Data Location is : "+output_dir+"\n")
agi4396b.timeout = 50000
#Using the Instruments starts here.
freqstart=float(raw_input('Please Enter Start Frequency in the Frequency range..'))
freqstop=float(raw_input('Please Enter Stop Frequency in the Frequency range..'))
IFFreq=int(raw_input('Please make your choice of IF - Enter 0 for 100 KHz and Enter 1 for 30 MHz: '))
freqIF=['0.0001 MHZ','30 MHZ']
log.write("Frequency range entered is : "+str(freqstart)+"MHz to "+str(freqstop)+" Mhz \n")
log.write("Selected IF Frequency Choice is : "+freqIF[IFFreq]+"\n")
freq2=freqstart+float(freqIF[IFFreq].split(' ')[0])
freq_hz=float(freqIF[IFFreq].split(' ')[0])*pow(10,6)
#agi4396b.write("REFV -40")# Setting the reference value to -40 dBm such that we can see values during the lower end as well.
fluke6060b.write("FR %s MZ" % freqstart)
pow1=0
reading=[]
pow2=10
#Measurement to look at the 30 MHz Peak
agi4396b.write("SENS:FREQ:CENT %s" % freq_hz)
span_val=1000# Setting Span Default to be 1 KHz
agi4396b.write("SENS:FREQ:SPAN %s" % span_val)
agi8648a.write("OUTPUT 719;FREQ:CW %s MHZ" % freq2)
agi8648a.write("POW:AMPL %s DBM" % pow2)    
fluke6060b.write("AP %s DBM" %pow1)
fluke6060b.write("RO 1")
time.sleep(5)
agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
agi4396b.write("MKR ON")
agi4396b.write("SEAM PEAK") #for peak search function
xval1=(agi4396b.query("MKRPRM?"))
yval1=float(agi4396b.query("MKRVAL?"))
reading.append([xval1,pow1,yval1])
time.sleep(5)
agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
trace_val=agi4396b.query("OUTPDTRC?")
trace_val_data=[float(j) for j in trace_val.strip('{}').split(',')]
pts1=np.linspace((float(xval1)-span_val)/1000000,(float(xval1)+span_val)/1000000,len(trace_val_data),endpoint=False)
pts=pts1.tolist()
fig1=plt.figure(figsize=(12,8))
ax=fig1.add_subplot(2,1,1)
ax.plot(pts,trace_val_data, 'b', label='power %s dBm' %yval1)
ctrfreq=float(xval1)/1000000
ax.plot(pts,trace_val_data, 'b', label='CenterFreq %s MHZ' %ctrfreq)
ax.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Power (dBm)')
legend = ax.legend(loc='upper right', shadow=True)
plt.savefig(output_dir+'/Mixer_Char_IFZoomed'+'image'+time.strftime('%Y%m%d-%H%M%S')+'.png')
fluke6060b.write("RO 0")
#Measurement to look at the peakest Peak
agi4396b.write("SENS:FREQ:START 0")
#span_val=1000# Setting Span Default to be 1 KHz
stpfreq=(freqstop+100)*1000000
agi4396b.write("SENS:FREQ:STOP %s" % stpfreq)
agi8648a.write("OUTPUT 719;FREQ:CW %s MHZ" % freq2)
agi8648a.write("POW:AMPL %s DBM" % pow2)    
fluke6060b.write("AP %s DBM" %pow1)
fluke6060b.write("RO 1")
time.sleep(5)
agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
agi4396b.write("MKR ON")
agi4396b.write("SEAM PEAK") #for peak search function
xval1=(agi4396b.query("MKRPRM?"))
yval1=float(agi4396b.query("MKRVAL?"))
reading.append([xval1,pow1,yval1])
time.sleep(5)
agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
trace_val=agi4396b.query("OUTPDTRC?")
trace_val_data=[float(j) for j in trace_val.strip('{}').split(',')]
pts1=np.linspace((float(xval1)-span_val)/1000000,(float(xval1)+span_val)/1000000,len(trace_val_data),endpoint=False)
pts=pts1.tolist()
fig1=plt.figure(figsize=(12,8))
ax=fig1.add_subplot(2,1,2)
ax.plot(pts,trace_val_data, 'b', label='power %s dBm' %yval1)
ctrfreq=float(xval1)/1000000
ax.plot(pts,trace_val_data, 'b', label='CenterFreq %s MHZ' %ctrfreq)
ax.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Power (dBm)')
legend = ax.legend(loc='upper right', shadow=True)
plt.savefig(output_dir+'/Mixer_Char_Range'+'image'+time.strftime('%Y%m%d-%H%M%S')+'.png')
fluke6060b.write("RO 0")

with open(output_dir+'/AMSAttnSweepData_Outp'+time.strftime('%Y%m%d-%H%M%S')+'.csv',"wb") as f:
                writer = csv.writer(f)
                writer.writerows(reading)
log.write("Frequency Settings for RF Signal Generator are \n")
log.write("Frequency Settings for LO Signal Generator are")
log.close()
fluke6060b.close
agi4396b.close
agi8648a.close

