# -*- coding: utf-8 -*-
"""
Created on Tue May 16 18:25:31 2017

@author: nchitta
"""
import visa, matplotlib.pyplot as plt,time, csv
#Lets Initialize our resource manager to speak with the devices
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()
#Just checking if we are able to access both the instruments correctly.
fluke6060b=rm.open_resource('GPIB0::2::INSTR')
sr844=rm.open_resource('GPIB0::8::INSTR')
agi8648a=rm.open_resource('GPIB0::19::INSTR')
output_dir = "Data/SR844/"+time.strftime('%Y%m%d-%H%M%S')
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
sr844.timeout = 50000
reading=[]
raw_input("Please make sure Fluke 6060B, Agilent 8648A are in Sync and ensure Fluke RF Out is connected to Ref In and Agilent RF Out at Signal Input  - Press Enter to Continue")
time.sleep(5)
freq1=int(raw_input('Please Input Frequency in MHZ..\n'))
fluke6060b.write("FR %s MZ" % freq1)
sr844.write('FMOD 0')# Setting the SR844 to run on reference input frequency
time.sleep(10)
pow1=-100
pin=[]
pout=[]
refphase=0
rdbmphase=0
fig=plt.figure(figsize=(12,8))
while pow1<=0:
        freq2=float(sr844.query("FRAQ?"))#Query the external frequency setting on the frequency tab in SR844
        print('sr844 is running on external frequency %s' %freq2)
        #agi8648a.write("OUTPUT 719;FREQ:CW %s HZ" % freq2)           # Commenting until we figure out the FRAQ problem     
        agi8648a.write("OUTPUT 719;FREQ:CW %s MHZ" %freq1)                
        agi8648a.write("POW:AMPL %s DBM" % pow1)    
        #fluke6060b.write("AP %s DBM" %pow1)
        agi8648a.write(":OUTP:STAT ON")
        #fluke6060b.write("RO 1")
        #agi4396b.write("INIT:IMM;*WAI")
#        for 4396B we have a little difference we gotta do the below to get the above:- :
#            :INITiate:CONTinuoust{OFF|0}
#            :ABORt
#            :SENSe:SWEep:COUNtt1
#            :INITiate
        time.sleep(5)
        sr844.write('AWRS')#Run auto select widereserve mode.
        sr844.write('AGAN')#Run auto sensitivity mode.
        time.sleep(5)
        sr844.write('APHS')#Run Autophase function
        time.sleep(5)
        refphase=sr844.query('PHAS?')#Adjusted Phase Value.
        time.sleep(1)
        rdbmphase=sr844.query("SNAP?4,5")
        data=[float(i) for i in rdbmphase.strip('{}').split(',')]
        reading.append([refphase,data[0],data[1]])
        pin.append(pow1)
        pout.append(data[0])
        pow1=pow1+1
        agi8648a.write(":OUTP:STAT OFF")
        #fluke6060b.write("RO 0")
else: 
        #if pow1>=10:
        if pow1>=0:
            with open(output_dir+'/SR844_3DeviceTest_Freq'+str(freq2)+time.strftime('%Y%m%d-%H%M%S')+'.csv',"wb") as f:
                writer = csv.writer(f)
                writer.writerows(reading)
            ax = fig.add_subplot(1,1,1)
            ax.plot(pin, pin, 'g')
            ax.plot(pin, pout, 'r')
            ax.set_xlabel('Input Power')
            ax.set_ylabel('Output Power')
        else:
            print('There is some trouble plz recheck results')
plt.savefig(output_dir+'/SR844_3DeviceTest_Freq_'+str(freq2)+time.strftime('%Y%m%d-%H%M%S')+'.png')