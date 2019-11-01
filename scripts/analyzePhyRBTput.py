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

phy_tb_thres = 100
phy_tb_sizes = []
for phy in datalist:
    if phy['tbSize'] > phy_tb_thres:
        phy_tb_sizes.append(phy['tbSize'])

phy_rb_thres = 3
phy_rb_pdu = []
for phy in datalist:
    if phy['numRB'] > phy_rb_thres:
        phy_rb_pdu.append(phy['numRB'])


numRBListFiltered = []
rbFilterThres = 3.0
numRBList = []
prevSFN = 0
prevTS = 0
tputListFiltered = []
tputFilterThres = 200000.0
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
