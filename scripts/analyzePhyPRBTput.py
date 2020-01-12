import sys
import pprint 
import datetime
from  matplotlib import pyplot as plt
import numpy as np
import os
pp = pprint.PrettyPrinter(indent=4)
filelocation = sys.argv[1]
dir_name = os.path.dirname(filelocation)+'/'


############### Data Import #################################
datalist = [] #PHY
rlcdatalist = []
pdcpPduStarted = False
with open(filelocation, 'r') as f:
    lines = f.readlines()
    dldict = {'pdcp': [], 'rlc': [], 'phy': []}
    for line in lines:
        if '[PUSCH Tx Info]' in line:
            phydict = {}
            words = line.split(' ')
            #print(words)
            dateAndTime = words[5] + ' ' + words[6]
            timestamp = datetime.datetime.strptime(dateAndTime,"%Y-%m-%d %H:%M:%S.%f")

            SFNSF = int(words[10])
            txPower = int(words[12])
            tbSize = int(words[18])
            numRB = int(words[15])
            mod = words[20]
            coderate = words[23].rstrip('\n')
            phydict = {'timestamp': timestamp,'SFNSF': SFNSF, 'txPower': txPower, 'numRB': numRB, 'tbSize':tbSize, 'mod':mod, 'coderate':coderate }
            datalist.append(phydict)
            #print(line)
            #print(dldict['phy'])
            #sys.exit()
        #print(len(datalog))
        elif '[RLC UL PDU Info]' in line:
            #print(line)
            words = line.split(' ')
            dateAndTime = words[5].lstrip('Info]\t') + ' ' + words[6]
            timestamp = datetime.datetime.strptime(dateAndTime,"%Y-%m-%d %H:%M:%S.%f")
            SN = int(words[8])
            FI = str(words[10])
            E = str(words[12])
            SysFN = int(words[14])
            subFN = int(words[16])
            SFN = SysFN * 10 + subFN                                           
            pduBytes = int(words[18])
            rb_cfg_idx = words[20].rstrip('\n')
            rlcdict = {'timestamp': timestamp, 'SN': SN, 'FI': FI, 'E': E , 'SFN': SFN, 'bytes':pduBytes, 'rb_cfg_idx': rb_cfg_idx}
            #print(rlcdict)
            rlcdatalist.append(rlcdict)

datalist = sorted(datalist, key=lambda k: k['timestamp'])  
rlcdatalist = sorted(rlcdatalist, key=lambda k: k['timestamp'])
print(len(datalist))
print(len(rlcdatalist))
rlc_pdu_bytes = []
for rlc in rlcdatalist:
    rlc_pdu_bytes.append(rlc['bytes'])

phy_tb_thres = 0
phy_tb_sizes = []
for phy in datalist:
    if phy['tbSize'] > phy_tb_thres:
        phy_tb_sizes.append(phy['tbSize'])

phy_rb_thres = 0
phy_rb_pdu = []
for phy in datalist:
    if phy['numRB'] > phy_rb_thres:
        phy_rb_pdu.append(phy['numRB'])

#pp.pprint(datalist)
#sys.exit()
numRBListFiltered = []
rbFilterThres = 0.0
numRBList = []
prevSFN = 0
prevTS = 0
tputListFiltered = []
tputFilterThres = 0.0
tputList = []
timeList = []
sfnPrefix = 0

numRBTemp = 0
tbTemp  = 0
timeTemp  = 0
PERIOD = 10 # average every 10ms
prevPhy = {}
first = True
def deltaMs(this, prev):
    return ( (this - prev).seconds * 1000) + ((this - prev).microseconds / 1000)

for phy in datalist:    
    if first:
        first = False
        prevPhy = phy 
        numRBList.append(0.0)
        tputList.append(0.0)
        timeList.append(0)
    else:
        thisTS = phy['timestamp']
        sfnDelta = phy['SFNSF'] - prevPhy['SFNSF']
        #tsDelta = deltaMs(thisTS, prevTS)
        #print(sfnDelta,numRBTemp,tbTemp,timeTemp)
        if sfnDelta < 0:
            #print (prevPhy,phy)
            prevPhy = phy
            continue 
        if timeTemp < PERIOD:
            numRBTemp += phy['numRB']
            tbTemp += phy['tbSize']
            timeTemp += sfnDelta
            prevPhy = phy
        else:
            numRBTemp += phy['numRB']
            tbTemp += phy['tbSize']
            timeTemp += sfnDelta
            avgNumRB = numRBTemp/float(timeTemp)
            if avgNumRB > rbFilterThres:
                numRBListFiltered.append(avgNumRB)
            numRBList.append(avgNumRB)
            avgTput = tbTemp * 8 * 1000 / float(timeTemp)
            if avgTput > tputFilterThres:
                tputListFiltered.append(avgTput)
            tputList.append(avgTput)
            recentTime = timeList[-1]
            timeList.append(recentTime + timeTemp)
            numRBTemp = 0
            tbTemp  = 0
            timeTemp  = 0
            prevPhy = phy 

print(len(numRBList), len(tputList))
################ Data Export #######################
output = open(dir_name+"numRB_average_period_filtered.log",'w')
for n in numRBListFiltered:
    output.write(str(n)+'\n')
output.close()

output = open(dir_name+"tputFiltered.log",'w')
for n in tputListFiltered:
    output.write(str(n)+'\n')
output.close()

output = open(dir_name+"numRB_average_period.log",'w')
for n in numRBList:
    output.write(str(n)+'\n')
output.close()

output = open(dir_name+"tput.log",'w')
for n in tputList:
    output.write(str(n)+'\n')
output.close()

output = open(dir_name+"modulation.log",'w')
for p in datalist:
    output.write(p['mod']+'\n')
output.close()

output = open(dir_name+"coderate.log",'w')
for p in datalist:
    output.write(p['coderate']+'\n')
output.close()

output = open(dir_name+"rlc_pdu_bytes.log",'w')
for bytes_ in rlc_pdu_bytes:
    output.write(str(bytes_)+'\n')
output.close()

output = open(dir_name+"phy_tb_sizes_filtered.log",'w')
for sizes_ in phy_tb_sizes:
    output.write(str(sizes_)+'\n')
output.close()

output = open(dir_name+"phy_numRB_per_pdu_filtered.log",'w')
for rb_ in phy_rb_pdu:
    output.write(str(rb_)+'\n')
output.close()
################## Plot ############################
def ecdf(data):
    x = np.sort(data)
    n = x.size
    y = np.arange(1, n+1) / n
    return(x,y)
    
#timeList[:] = [x - 50000 for x in timeList]

title=str(sys.argv[2])

plt.hist(numRBList,50,label='Num RBs',normed=True,cumulative=True\
        ,histtype='step',alpha=0.55,color='blue',linewidth=3 )
plt.xlabel("Number of RBs")
plt.title(title)
plt.tight_layout()
plt.savefig(dir_name+"CDF_numRB.png")
plt.show()


plt.subplot(2,1,1)
color = 'tab:red'
plt.step(timeList, numRBList,color=color)
plt.xlabel('time (ms)')
plt.ylabel('Number of RBs', color=color)        
plt.title(title)
plt.xlim(0)
#plt.xlim(20500,22500)

#plt.tick_params(axis='y', labelcolor=color)
plt.grid(True)

plt.subplot(2,1,2)
color = 'tab:blue'
plt.step(timeList, tputList, color=color)
plt.xlabel('time (ms)')
plt.ylabel('Throughput (Mbps)',color=color)
plt.title('Throughput (Mbps)')
#plt.xlim(20500,22500)
plt.xlim(0)
#plt.tick_params(axis='y', labelcolor=color)
plt.grid(True)
plt.tight_layout()
plt.savefig(dir_name+"Time_numRB_tput.png")
plt.show()    

