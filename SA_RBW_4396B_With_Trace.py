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
#agi8648a=rm.open_resource('GPIB0::19::INSTR')
output_dir = "Data/SA_RBW_Trace/"+time.strftime('%Y%m%d-%H%M%S')
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
agi4396b.timeout = 50000
#rbw_val = ['1 KHZ','10 KHZ','30 KHZ','100 KHZ','300 KHZ','1 MHZ','3 MHZ']
#rbw_val = ['300 HZ','1000 HZ','3000 HZ','10000 HZ','30000 HZ','100000 HZ','300000 HZ','1000000 HZ','3000000 HZ']
#rbw_val = ['100 KHZ','1 MHZ','3 MHZ']
rbw_val = ['100000 HZ','300000 HZ','1000000 HZ','3000000 HZ']
#rbw_val = ['10 KHZ']
reading=[]
#u2043x=rm.open_resource('USB0::0x2A8D::0x1D01::MY55190016::INSTR')
freq1=int(raw_input('Please Input Frequency in MHZ..\n'))
freq_hz=freq1*pow(10,6)
#pow1=raw_input('Please Input Power in dBm..\n')
fluke6060b.write("FR %s MZ" % freq1)
#agi8648a.write("OUTPUT 719;FREQ:CW %s MHZ" % freq1)
agi4396b.write("SENS:FREQ:CENT %s" % freq_hz)
j=0
fig=plt.figure(figsize=(12,8))
while j<=len(rbw_val)-1:
    agi4396b.write("BW ", rbw_val[j])# Write GPIB to select first RBW value and get the xval 
    #print("rbw set as ", rbw_val[j])
#    agi4396b.write("INIT:IMM;*WAI")# to make a complete sweep before actually getting the data. 
    rbw_split=rbw_val[j].split(' ')
    span_val=float(rbw_split[0])*100
    agi4396b.write("SENS:FREQ:SPAN %s" % span_val)
    agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
    agi4396b.write("MKR ON")    
    agi4396b.write("MKRPRM %s" % freq_hz) 
    pow1=-100
    pin=[]
    pout=[]
    #while pow1<=10:
    while pow1<=-0:
        #agi8648a.write("POW:AMPL %s DBM" % pow1)    
        fluke6060b.write("AP %s DBM" %pow1)
        #agi8648a.write(":OUTP:STAT ON")
        fluke6060b.write("RO 1")
        #agi4396b.write("INIT:IMM;*WAI")
#        for 4396B we have a little difference we gotta do the below to get the above:- :
#            :INITiate:CONTinuoust{OFF|0}
#            :ABORt
#            :SENSe:SWEep:COUNtt1
#            :INITiate
        time.sleep(5)
        agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
        trace_val=agi4396b.query("OUTPDTRC?")
        trace_val_data=[float(i) for i in trace_val.strip('{}').split(',')]
        pts=list(xrange(len(trace_val_data)))
        fig1=plt.figure(figsize=(12,8))
        ax=fig1.add_subplot(1,1,1)
        ax.plot(pts,trace_val_data, 'b', label='power %s dBm' %pow1)
        legend = ax.legend(loc='upper right', shadow=True)
        plt.savefig(output_dir+'/4396B_SA_RBWOut'+'image'+time.strftime('%Y%m%d-%H%M%S')+'.png')
        #agi4396b.write("SING")
        agi4396b.write("MKR ON")
        agi4396b.write("SEAM PEAK") #for peak search function
        #agi4396b.write("MKRPRM %s" % freq_hz) 
        xval=(agi4396b.query("MKRPRM?"))
        yval=float(agi4396b.query("MKRVAL?"))
        reading.append([xval,pow1,yval])
        pin.append(pow1)
        pout.append(yval)
        pow1=pow1+1
        #agi8648a.write(":OUTP:STAT OFF")
        fluke6060b.write("RO 0")
    else: 
        #if pow1>=10:
        if pow1>=-0:
            print('Power In and Power out calculated for j: %s' % j)
            with open(output_dir+'/4396B_SA_RBWOut_CSV'+'RBWvalIndex'+str(j)+time.strftime('%Y%m%d-%H%M%S')+'.csv'.format(output_dir),"wb") as f:
                writer = csv.writer(f)
                writer.writerows(reading)
            ax = fig.add_subplot(3,3,j+1)
            ax.plot(pin, pin, 'g')
            ax.plot(pin, pout, 'r')
            ax.set_xlabel('Input Power')
            ax.set_ylabel('Output Power')
            j=j+1
        else:
            print('There is some trouble plz recheck results')
else:
    print("Various Readings for RBW values Measured")
    plt.savefig(output_dir+'/4396B_SA_RBWOut_Figure'+time.strftime('%Y%m%d-%H%M%S')+'.png'.format(output_dir))
#    
agi4396b.close
#agi8648a.close
fluke6060b.close