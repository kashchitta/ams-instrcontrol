import visa,matplotlib.pyplot as plt,time, csv, scipy.stats as st, pandas as pd, numpy as np, warnings,matplotlib,math as mt
#Lets Initialize our resource manager to speak with the devices
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()