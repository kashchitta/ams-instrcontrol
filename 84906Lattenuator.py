import visa, time
#Lets Initialize our resource manager to speak with the devices
rm=visa.ResourceManager()
#We want to do this just to check out spool results for reference later on.
rm.list_resources()
#hp84906l=rm.open_resource('GPIB0::1::INSTR')
#hp84906l.timeout = 20000
#print(hp84906l.query("IDN?"))
#print(hp84906l.write("B12345678")) 
# Above IS all we need for controlling the programmable attenuator. B to Switch OFF and A to Switch ON