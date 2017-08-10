# -*- coding: utf-8 -*-
"""
Created on Fri Jun 2 22:15:04 2017
Scribled Attenuation Measurement System Complete

@author: nchitta
"""
import visa,matplotlib.pyplot as plt,time, csv, scipy.stats as st, pandas as pd, numpy as np, warnings,matplotlib,math as mt
#Lets Initialize our resource manager to speak with the devices
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()
#Just checking if we are able to access both the instruments correctly.
output_dir = "Data/AMS/"+time.strftime('%Y%m%d-%H%M%S')
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
hp84906l=rm.open_resource('GPIB0::1::INSTR')
hp84906l.timeout = 20000
freq1=float(raw_input('Please Input Frequency to test in MHZ..'))
IFFreq=int(raw_input('Please make your choice of IF - Enter 0 for 100 KHz and Enter 1 for 30 MHz: '))
notr=float(raw_input('Please input the number of trials '))
thre=float(raw_input('Please input the threshold values'))
freqIF=['0.0001 MHZ','30 MHZ']
freq2=freq1+float(freqIF[IFFreq].split(' ')[0])
freq_hz=float(freqIF[IFFreq].split(' ')[0])*pow(10,6)
agi4396b.write("SENS:FREQ:CENT %s" % freq_hz)
span_val=100000# Setting Span Default to be 1 KHz
agi4396b.write("SENS:FREQ:SPAN %s" % span_val)
agi4396b.write("REFV -40")# Setting the reference value to -40 dBm such that we can see values during the lower end as well.
fluke6060b.write("FR %s MZ" % freq1)
pow1=0
pow2=10
it=0
refdata=[]
agi8648a.write("OUTPUT 719;FREQ:CW %s MHZ" % freq2)
agi8648a.write("POW:AMPL %s DBM" % pow2)    
print("Attenuation Comparison list generation in Progress...")
Att1=['B1234','B234A1','B134A2','B124A3','B24A13', 'B14A23','B4A123','B2A134','B1A234','A1234']
Att2=["0 dB","10 dB", "20 dB", "30 dB", "40 dB", "50 dB", "60 dB", "70 dB", "80 dB", "90 dB"]
pin=[]
pout=[]
while it<len(Att1):
        fluke6060b.write("AP %s DBM" %pow1)
        fluke6060b.write("RO 1")
        time.sleep(5)
        hp84906l.write(Att1[it])
        time.sleep(5)
        agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
        agi4396b.write("MKR ON")
        agi4396b.write("SEAM PEAK") #for peak search function
        xval1=(agi4396b.query("MKRPRM?"))
        yval1=float(agi4396b.query("MKRVAL?"))
        refdata.append([xval1,pow1,yval1])
        pin.append(pow1)
        pout.append(yval1)
        it=it+1        
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
        if it>=len(Att1):
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
while True:
    pow2=raw_input('Setting in DATUM Setting to be lowest for measuremnet- to change for highest setting you have to end - press done to end')
    hp84906l.write(Att1[0])# Change 0 to 9 if you want highest setting
    time.sleep(5)
    if pow2=='done': break
    raw_input("Please recheck to make sure Fluke 6060B output, 84906L and 4396B Input are connected and once done - press enter to continue")
    pchk=[]
    reading=[]
    #GPIB commands to power up SG and Measure SA.
    fluke6060b.write("AP %s DBM" %pow1)
    fluke6060b.write("RO 1")
    time.sleep(5)
    agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
    agi4396b.write("MKR ON")
    agi4396b.write("SEAM PEAK") #for peak search function
    xval2=(agi4396b.query("MKRPRM?"))
    yval2=float(agi4396b.query("MKRVAL?"))
    pchk.append(yval2)
    time.sleep(5)
    agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
    trace_val=agi4396b.query("OUTPDTRC?")
    trace_val_data=[float(j) for j in trace_val.strip('{}').split(',')]
    pts=list(xrange(len(trace_val_data)))
    fig1=plt.figure(figsize=(12,8))
    ax=fig1.add_subplot(1,1,1)
    ax.plot(pts,trace_val_data, 'b', label='power %s dBm' %yval2)
    ax.plot(pts,trace_val_data, 'b', label='CenterFreq %s MHZ' %xval2)
    legend = ax.legend(loc='upper right', shadow=True)
    plt.savefig(output_dir+'/AMSSAOut_PchkNoAttn'+'image'+time.strftime('%Y%m%d-%H%M%S')+'.png')
    fluke6060b.write("RO 0")
    raw_input("Please connect the attenuator and once done - press enter to continue")
    #GPIB commands to power up SG and Measure SA.
    fluke6060b.write("AP %s DBM" %pow1)
    fluke6060b.write("RO 1")
    time.sleep(5)
    hp84906l.write(Att1[0])
    time.sleep(5)
    agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
    agi4396b.write("MKR ON")
    agi4396b.write("SEAM PEAK") #for peak search function
    xval=(agi4396b.query("MKRPRM?"))
    yval=float(agi4396b.query("MKRVAL?"))
    pchk.append(yval)
    time.sleep(5)
    agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
    trace_val=agi4396b.query("OUTPDTRC?")
    trace_val_data=[float(j) for j in trace_val.strip('{}').split(',')]
    pts=list(xrange(len(trace_val_data)))
    fig1=plt.figure(figsize=(12,8))
    ax=fig1.add_subplot(1,1,1)
    ax.plot(pts,trace_val_data, 'b', label='power %s dBm' %yval)
    ax.plot(pts,trace_val_data, 'b', label='CenterFreq %s MHZ' %xval)
    legend = ax.legend(loc='upper right', shadow=True)
    plt.savefig(output_dir+'/AMSSAOut_PchkAttn'+'image'+time.strftime('%Y%m%d-%H%M%S')+'.png')
    fluke6060b.write("RO 0")
    #Starting matching: - 
    print("Matching in Progress...")
    #Linear Search
    i=0
    j=0
    n=0
    diff=[]
    #Linear Search for DUT Setting
    while i < len(refdata):
        diff.append(float(refdata[i][2])-pchk[1])
        #print(i)
        i=i+1
    else:
        print("program successfully terminated. for DUT Setting")
        absdiff=[]
        for x in diff:
            absdiff.append(abs(x))
        n=absdiff.index(min(absdiff))
        print("matched index is ",n)
        print("error margin is for DATUM Setting match :", min(absdiff))
        print("Match Complete. Closest match to DUT setting from Power Sweeped against"+str(pchk[1])+" is"+str(refdata[n][2]))
    #Linear Search for DATUM Setting
    j=0
    diffd=[]
    while j < len(refdata):
        diffd.append(float(refdata[j][2])-pchk[0])
        #print(j)
        j=j+1
    else:
        print("program successfully terminated. for DUT Setting")
        absdiffd=[]
        for x in diffd:
            absdiffd.append(abs(x))
        m=absdiffd.index(min(absdiffd))
        print("error margin is for DUT Setting match :", min(absdiffd))
        print("Match Complete. Closest match to DUT setting from Power Sweeped against"+str(pchk[0])+" is"+str(refdata[m][2]))
    #print("RF Subs based Attenuation value is: ", float(pchk[0])-float(pchk[1])) # for the sake of bm <  am / writing in string values 
    print("Quasi RF-IF Subs based Attenuation value is: ", pchk[0]-pchk[1])
    print("Algorithm Based Attenuator setting value", Att2[n])
    #Lets get some statistics for the Uncertainty Calculation.X
    trial=0
    raw_input('Attenuator setting found - Please remove the DUT from place to calculate statistical data - press enter to continue')
    while trial <notr:
        hp84906l.write(Att1[n])
        fluke6060b.write("AP %s DBM" %pow1)
        fluke6060b.write("RO 1")
        time.sleep(1)
        agi4396b.write(":INIT:CONT 0;:ABOR;:SENS:SWE:COUN 1;:INIT:CONT 1")
        agi4396b.write("MKR ON")
        agi4396b.write("SEAM PEAK") #for peak search function
        xval2=(agi4396b.query("MKRPRM?"))
        yval2=float(agi4396b.query("MKRVAL?"))
        reading.append(yval2)
        time.sleep(1)
        trial=trial+1
    else:
        print(reading)
        pts1=list(xrange(len(reading)))
        with open(output_dir+'/AMSStatData_Outp'+time.strftime('%Y%m%d-%H%M%S')+'.csv',"wb") as f:
                writer = csv.writer(f)
                for eachval in reading:
                    writer.writerow([eachval])
                    
#Data for trying to fit probability distribution of the data we have at place. 
                    
    matplotlib.rcParams['figure.figsize'] = (16.0, 12.0)
    matplotlib.style.use('ggplot')
    
    # Create models from data
    def best_fit_distribution(data, bins=200, ax=None):
        """Model data by finding best fit distribution to data"""
        # Get histogram of original data
        y, x = np.histogram(data, bins=bins, normed=True)
        x = (x + np.roll(x, -1))[:-1] / 2.0
    
        # Distributions to check
        DISTRIBUTIONS = [        
            st.alpha,st.anglit,st.arcsine,st.beta,st.betaprime,st.bradford,st.burr,st.cauchy,st.chi,st.chi2,st.cosine,
            st.dgamma,st.dweibull,st.erlang,st.expon,st.exponweib,st.exponpow,st.f,st.fatiguelife,st.fisk,
            st.foldcauchy,st.foldnorm,st.frechet_r,st.frechet_l,st.genlogistic,st.genpareto,st.genexpon,
            st.genextreme,st.gausshyper,st.gamma,st.gengamma,st.genhalflogistic,st.gilbrat,st.gompertz,st.gumbel_r,
            st.gumbel_l,st.halfcauchy,st.halflogistic,st.halfnorm,st.hypsecant,st.invgamma,st.invgauss,
            st.invweibull,st.johnsonsb,st.johnsonsu,st.ksone,st.kstwobign,st.laplace,st.levy,st.levy_l,st.levy_stable,
            st.logistic,st.loggamma,st.loglaplace,st.lognorm,st.lomax,st.maxwell,st.mielke,st.nakagami,st.ncx2,st.ncf,
            st.nct,st.norm,st.pareto,st.pearson3,st.powerlaw,st.powerlognorm,st.powernorm,st.rdist,st.reciprocal,
            st.rayleigh,st.rice,st.recipinvgauss,st.semicircular,st.t,st.triang,st.truncexpon,st.truncnorm,st.tukeylambda,
            st.uniform,st.vonmises,st.vonmises_line,st.wald,st.weibull_min,st.weibull_max,st.wrapcauchy
        ]
        DISTRIBUTIONS = [
            st.expon,st.halfnorm,st.invgauss,st.lognorm,st.norm,
            st.pareto,st.powernorm,st.rayleigh,st.uniform
        ]
    
    
        # Best holders
        best_distribution = st.norm
        best_params = (0.0, 1.0)
        best_sse = np.inf
    
        # Estimate distribution parameters from data
        for distribution in DISTRIBUTIONS:
    
            # Try to fit the distribution
            try:
                # Ignore warnings from data that can't be fit
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
    
                    # fit dist to data
                    params = distribution.fit(data)
    
                    # Separate parts of parameters
                    arg = params[:-2]
                    loc = params[-2]
                    scale = params[-1]
    
                    # Calculate fitted PDF and error with fit in distribution
                    pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
                    sse = np.sum(np.power(y - pdf, 2.0))
    
                    # if axis pass in add to plot
                    try:
                        if ax:
                            pd.Series(pdf, x).plot(ax=ax)
                    except Exception:
                        pass
    
                    # identify if this distribution is better
                    if best_sse > sse > 0:
                        best_distribution = distribution
                        best_params = params
                        best_sse = sse
    
            except Exception:
                pass
    
        return (best_distribution.name, best_params)
    
    def make_pdf(dist, params, size=10000):
        """Generate distributions's Probability Distribution Function """
    
        # Separate parts of parameters
        arg = params[:-2]
        loc = params[-2]
        scale = params[-1]
    
        # Get sane start and end points of distribution
        start = dist.ppf(0.01, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.01, loc=loc, scale=scale)
        end = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)
    
        # Build PDF and turn into pandas Series
        x = np.linspace(start, end, size)
        y = dist.pdf(x, loc=loc, scale=scale, *arg)
        pdf = pd.Series(y, x)
    
        return pdf
    
    # Load data from reading
    data=pd.Series(reading)
    # Plot for comparison
    plt.figure(figsize=(12,8))
    ax = data.plot(kind='hist', bins=50, normed=True, alpha=0.5, color=plt.rcParams['axes.color_cycle'][1])
    # Save plot limits
    dataYLim = ax.get_ylim()
    
    # Find best fit distribution
    best_fit_name, best_fit_paramms = best_fit_distribution(data, 200, ax)
    best_dist = getattr(st, best_fit_name)
    
    # Update plots
    ax.set_ylim(dataYLim)
    ax.set_title(u'All Fitted Distributions')
    ax.set_xlabel(u'Attenuation Value')
    ax.set_ylabel('Frequency')
    plt.savefig(output_dir+'/AMSSAOut_AllFittedDistributions'+'image'+time.strftime('%Y%m%d-%H%M%S')+'.png')
    # Make PDF
    print('Best Distribution fit is', best_dist)
    pdf = make_pdf(best_dist, best_fit_paramms)
    
    # Display
    plt.figure(figsize=(12,8))
    ax = pdf.plot(lw=2, label='PDF', legend=True)
    data.plot(kind='hist', bins=50, normed=True, alpha=0.5, label='Data', legend=True, ax=ax)
    
    param_names = (best_dist.shapes + ', loc, scale').split(', ') if best_dist.shapes else ['loc', 'scale']
    param_str = ', '.join(['{}={:0.2f}'.format(k,v) for k,v in zip(param_names, best_fit_paramms)])
    dist_str = '{}({})'.format(best_fit_name, param_str)
    
    ax.set_title(u'with best fit distribution \n' + dist_str)
    ax.set_xlabel(u'Attenuation value')
    ax.set_ylabel('Frequency')
    plt.savefig(output_dir+'/AMSSAOut_BestFitDistribution'+'image'+time.strftime('%Y%m%d-%H%M%S')+'.png')
    print("Algorithm Based Mean Value is : ", np.mean(reading))
    print("Algorithm Based Attenuation Error is", np.std(reading))
    print("Algorithm Based Attenuation is", -(np.mean(reading)-float(refdata[0][2])))
    #Calculating The Uncertainty
    reading.sort()
    def split_list(data):
        half = len(data)/2
        return data[:half], data[half:]
    data1,data2 = split_list(reading)
    x1=np.mean(data1)
    x2=np.mean(data2)
    s1=np.var(data1)
    s2=np.var(data2)
    meandiff=x1-x2
    sumofsqr=mt.sqrt(mt.pow(s1,2)+mt.pow(s2,2))
    t0=2.24*(meandiff/sumofsqr)
    f0=mt.pow(s1,2)/mt.pow(s2,2)
    if s1>s2 and f0<6.4 and t0<2.3:
        print('The Mean Value and Variance are Stationary and this is a valid measurement')
        #Make sure you replace the below Ifs using a simple dictionary to capture the actual uncertainty on the go.        
        if notr==10:
            ts=3.2
        elif notr>20:
            ts=2.6
        else:
            ts=9.9
        print('Finaly Attenuation reading with Uncertainty is '+str(-(np.mean(reading)-float(refdata[0][2])))+' +/- '+str(ts/mt.sqrt(notr))+' dB')
    elif f0>6.4:
        print('The Variance is not stationary - Cannot use this measurement for calculation of Random Uncertainty')
    elif t0>2.3:
        print('The Mean is not stationary - Cannot Use this Measurement for calculation of Random Uncertainty')
    else:
        print('Using variable explorer try to understand the cause of this really crazy edgecase')
fluke6060b.close
agi4396b.close
hp84906l.close
agi8648a.close