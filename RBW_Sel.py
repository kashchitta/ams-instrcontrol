# -*- coding: utf-8 -*-
"""
Created on Thu Apr 06 16:33:17 2017

@author: nchitta
"""

import visa
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()
#Just checking if we are able to access both the instruments correctly.
agi4411b=rm.open_resource('GPIB0::18::INSTR')
frequency=raw_input('Please Input Frequency in MHZ..')
power=raw_input('Please Input Lowest Power of your choice in dBm..')
rbw_val = ['1 KHZ','10 KHZ','30 KHZ','100 KHZ','300 KHZ','1 MHZ','3 MHZ']
j=0
while j<len(rbw_val):
    agi4411b.write(":SENSe:BWIDTH:RES ", rbw_val[j])# Write GPIB to select first RBW value and get the xval 
    #print("rbw set as ", rbw_val[j])
    agi4411b.write("INIT:IMM;*WAI")# to make a complete sweep before actually getting the data. 
    agi4411b.write("CALC:MARK1:MAX")
    freqcstr=agi4411b.query("CALC:MARK1:X?")
    freqc=float(freqcstr)
    freqcchk=freqc/1e6
    freqchk=float(frequency)
    #print(freqchk,freqcchk)
    if freqchk>freqcchk:
        j=j+1
        rbw_amp2=rbw_val[j]        
        #print("if loop j ",j)
        j= len(rbw_val)+1
        #print(rbw_amp2)
        #print("exiting calculation loop")
    elif freqchk<=freqcchk:
        j= j+1
        #print(rbw_val[j])
        #print("elif loop j ",j)
        rbw_amp1=rbw_val[j]
else:
    print("Optimized Spectrum Analyzer values calculated for Frequency & Power")
    print("Optimized SA RBW for Frequency is %s " %rbw_amp2)
    print("Optimized SA RBW for Power is %s " %rbw_amp1)