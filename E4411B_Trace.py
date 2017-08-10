import visa, matplotlib.pyplot as plt,time, csv
#Lets Initialize our resource manager to speak with the devices
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()
#Just checking if we are able to access both the instruments correctly.
output_dir = "Data/Trace/"+time.strftime('%Y%m%d-%H%M%S')
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
reading=[]
agi4411b=rm.open_resource('GPIB0::18::INSTR')
agi4411b.timeout = 50000
#agi4411b.write("SENS:FREQ:CENT 30 MHZ")
#agi4411b.write("SENS:FREQ:SPAN 50 MHZ")
agi4411b.write("INIT:IMM;*WAI")
time.sleep(5)
agi4411b.write("CALC:MARK1:MAX")
xval=(agi4411b.query("CALC:MARK1:X?"))
yval=float(agi4411b.query("CALC:MARK1:Y?"))
reading.append([xval,yval])
trace_val=agi4411b.query("TRAC:DATA? TRACE1 ")
trace_val_data=[float(i) for i in trace_val.strip('{}').split(',')]
pts=list(xrange(len(trace_val_data)))
fig1=plt.figure(figsize=(12,8))
ax=fig1.add_subplot(1,1,1)
ax.plot(pts,trace_val_data, 'b', label='power %s dBm' %yval)
ax.plot(pts,trace_val_data, 'b', label='ctrfreq %s MHz' %xval)
ax.set_xlabel('401 Pts on Trace')
ax.set_ylabel('Output Power in dBm')
legend = ax.legend(loc='upper right', shadow=True)
plt.savefig(output_dir+'/E4411B_Trace'+'FromSecondIF_RF_3.3_LO_3.90_4352B_Reading_600.00'+'image'+time.strftime('%Y%m%d-%H%M%S')+'.png')