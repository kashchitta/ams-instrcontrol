# -*- coding: utf-8 -*-
"""
Created on Fri Jun 2 22:15:04 2017
Scribled Attenuation Measurement System Complete

@author: nchitta
"""
import csv, numpy as np, math as mt
readingz=[]
reading=[]
refdata=[]
#with open('AMS_RefData.csv') as reffile:
#    reader=csv.reader(reffile)
#    for row in reader:
#        refdata.append(row)
#        print(row)
#with open('Statistical_Reading.csv') as statfile:
#    reader=csv.reader(statfile)
#    for row in reader:
#        readingz.append(row)
#        print(row)
#x=list(xrange(len(readingz)))
reading1=[-14.83645,-14.88455,-14.8955,-14.87867,-14.87791,-14.87547,-14.88379,-14.88161,-14.92044,-14.92443]
reading2= [4.04171,
 4.04815,
 4.05905,
 4.04222,
 4.04146,
 4.03902,
 4.04734,
 4.04516,
 4.08399,
 4.08798]
#reading=[]
#x=list(xrange(len(reading2)))
#for i in x:
##    reading.append(float(readingz[i][0]))
#    reading.append(reading2)
#sorted(reading)
reading=reading2
notr=len(reading)
#Calculating The Uncertainty
def split_list(data):
    half = len(data)/2
    return data[:half], data[half:]
data1=[]
data2=[]
data1,data2 = split_list(reading)
x1=np.mean(data1)
x2=np.mean(data2)
s1=np.var(data1)
s2=np.var(data2)
meandiffs1=x1-x2
meandiffs2=x2-x1
sumofsqr=mt.sqrt(mt.pow(s1,2)+mt.pow(s2,2))
t0=2.24*(meandiffs2/sumofsqr)
t1=2.24*(meandiffs1/sumofsqr)
f0=mt.pow(s1,2)/mt.pow(s2,2)
f1=mt.pow(s2,2)/mt.pow(s1,2)
if s1>s2 and f0<6.4 and t0<2.3:
    print('The Mean Value and Variance are Stationary and this is a valid measurement')
    #Make sure you replace the below Ifs using a simple dictionary to capture the actual uncertainty on the go.        
    if notr==10:
        ts=3.2
    elif notr>20:
        ts=2.6
    else:
        ts=9.9
    print('Finaly Attenuation reading with Uncertainty is '+str(np.mean(reading))+' +/- '+str(ts/mt.sqrt(notr))+' dB')
elif f0>6.4:
    print('The Variance is not stationary - Cannot use this measurement for calculation of Random Uncertainty')
elif t0>2.3:
    print('The Mean is not stationary - Cannot Use this Measurement for calculation of Random Uncertainty')
else:
    print('Using variable explorer try to understand the cause of this really crazy edgecase')
raw_input('Press enter to exit after you have reviewed the data')
