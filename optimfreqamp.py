# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 11:15:04 2017

@author: nchitta
"""
###Change Log 3/13/2017 Changes have been made to get optimal 4411B settings to be###
###able to get better match to the output using some statistical techniques.      ###
#####################################################################################
#   This code is trying to control all the instruments for basic GPIB programming   #
#   to conduct the random error experiment.                                         #
#####################################################################################
# Refer randerr experiment.txt in /home/chitta/Desktop/Python/InstCon/ for backgrnd #
#####################################################################################
# Test code to see how to connect with GPIB and query!!
#import visa 
#rm = visa.ResourceManager()
#rm.list_resources()
#('ASRL1::INSTR','ASRL2::INSTR','GPIB0::19::INSTR')
#inst = rm.open_resource('GPIB0::19:INSTR')
#print(inst.query("*IDN?"))
#Ok Level 1 of testing complete - lets get started with the actual code now :) #
#Lets import all the packages we want to use in this program
#import numpy as np
#import matplotlib as plt
import visa, time, numpy as np
import csv
#Lets Initialize our resource manager to speak with the devices
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()
#Just checking if we are able to access both the instruments correctly.
agi4411b=rm.open_resource('GPIB0::18::INSTR')
agi8648a=rm.open_resource('GPIB0::19::INSTR')
print(agi4411b.query("*IDN?"))
print(agi8648a.query("*IDN?"))
frequency=raw_input('Please Input Frequency in MHZ\n')
power=raw_input('Please Input Power in dBm\n')
nooftrials=raw_input('Please Input Number of Trials for calibrating random error')
#Lets give the signal generator and spectrum analyzer their required basic settings.
agi8648a.write("OUTPUT 719;FREQ:CW %s MHZ" % frequency)
agi8648a.write("POW:AMPL %s DBM" % power)
agi4411b.write("SENS:FREQ:CENT %s MHZ" % frequency)
agi4411b.write("SENS:FREQ:SPAN 1 MHZ")
agi4411b.write("POW:ATT 0 DB")
agi8648a.write(":OUTP:STAT ON")
#Loop for selecting optimum frequency and amplitude: - 
rbw_val = ['1 KHZ','10 KHZ','30 KHZ','100 KHZ','300 KHZ','1 MHZ']
j=0
while j<len(rbw_val):
    agi4411b.write(":SENSe:BWIDTH:RES ", rbw_val[j])# Write GPIB to select first RBW value and get the xval 
    print("rbw set as ", rbw_val[j])
    agi4411b.write("INIT:IMM;*WAI")# to make a complete sweep before actually getting the data. 
    agi4411b.write("CALC:MARK1:MAX")
    freqcstr=agi4411b.query("CALC:MARK1:X?")
    freqc=float(freqcstr)
    freqcchk=freqc/1e6
    freqchk=float(frequency)
    print(freqchk,freqcchk)
    if freqchk>freqcchk:
        j=j+1
        rbw_amp2=rbw_val[j]        
        print("if loop j ",j)
        j= len(rbw_val)+1
        print(rbw_amp2)
        print("exiting calculation loop")
    elif freqchk<=freqcchk:
        j= j+1
        print(rbw_val[j])
        print("elif loop j ",j)
        rbw_amp1=rbw_val[j]
else:
    print("Optimized Spectrum Analyzer values calculated")
    print(rbw_amp1, rbw_amp2)
#Let us loop the loop for storing frequency and Amplitude.
i=0 
notr=int(nooftrials)
result=[[nooftrials,frequency,power]]
while i < notr:
#for trial in nooftrials: using amp1 to calculate frequency for x value
    agi4411b.write(":SENSe:BWIDTH:RES ", rbw_val[0])#write GPIB to select RBW value for xval amp1        
    agi4411b.write("INIT:IMM;*WAI")    
    agi4411b.write("CALC:MARK1:MAX")
    xval=(agi4411b.query("CALC:MARK1:X?"))
    xval_fin=float(xval)/1e6
    agi4411b.write(":SENSe:BWIDTH:RES ", rbw_amp1)#write GPIB to select RBW value for xval amp1    
    agi4411b.write("INIT:IMM;*WAI")    
    agi4411b.write("CALC:MARK1:MAX")
    yval1=float(agi4411b.query("CALC:MARK1:Y?"))
    agi4411b.write(":SENSe:BWIDTH:RES ", rbw_amp2)#write GPIB to select RBW value for xval amp2
    agi4411b.write("INIT:IMM;*WAI")
    agi4411b.write("CALC:MARK1:MAX")    
    yval2=float(agi4411b.query("CALC:MARK1:Y?"))
    print i,xval,yval1,yval2
    yval=np.average([yval1,yval2])
    result.append([i,xval_fin,yval])
    agi8648a.write(":OUTP:STAT OFF")
    time.sleep(1)
    agi8648a.write(":OUTP:STAT ON")
    time.sleep(2)
    i = i + 1
#    print i
#    print trial
else:
    print i, "Are the number of trials conducted successfully"
    print result       
#save file to data for backup: -  with some sort of timestamp
    with open('output'+time.strftime('%Y%m%d-%H%M%S')+'.csv',"wb") as f:
        writer = csv.writer(f)
        writer.writerows(result)
#Close the instruments and plot the data.
agi8648a.write(":OUTP:STAT OFF")
agi4411b.close
agi8648a.close