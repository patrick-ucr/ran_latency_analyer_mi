import sys
import pprint
import datetime
pp = pprint.PrettyPrinter(indent=4)
import matplotlib.pyplot as plt
import os
filelocation = sys.argv[1]
############### Data Import #################################

dldict = {'pdcp': [], 'rlc': [], 'phy': []}
with open(filelocation, 'r') as f:
    lines = f.readlines()
    for line in lines:
        #print(line)
        if '[PDCP UL PDU Info]' in line:
            #print(line)
            words = line.split(' ')
            dateAndTime = words[6] + ' ' + words[7]
            timestamp = datetime.datetime.strptime(dateAndTime,"%Y-%m-%d %H:%M:%S.%f")
            SN = int(words[9]) # sequence number
            SysFN = int(words[15])
            subFN = int(words[18].rstrip('\n'))
            SFN = SysFN * 10 + subFN # frame-subframe
            pduBytes = int(words[12])
            pdcpdict = {'timestamp': timestamp,'SN': SN, 'SFN': SFN, 'bytes':pduBytes }
            #print(pdcpdict)
            dldict['pdcp'].append(pdcpdict)

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
            dldict['rlc'].append(rlcdict)
            #print(line)
            #print(dldict['rlc'])
            #sys.exit()
        elif '[PUSCH Tx Info]' in line:
            words = line.split(' ')
            dateAndTime = words[5].lstrip('Info]\t') + ' ' + words[6]
            timestamp = datetime.datetime.strptime(dateAndTime,"%Y-%m-%d %H:%M:%S.%f")
            SFNSF = int(words[10])
            txPower = int(words[12])
            tbSize = int(words[18])
            numRB = int(words[15])
            phydict = {'timestamp': timestamp,'SFN': SFNSF, 'txPower': txPower, 'numRB': numRB, 'tbSize':tbSize }
            #print(phydict)
            dldict['phy'].append(phydict)
            #print(line)
            #print(dldict['phy'])
            #sys.exit()
    #print(len(datalog))

allpdcp = dldict['pdcp']
#print(len(allpdcp))
allrlc = dldict['rlc']
#print(len(allrlc))
allphy = dldict['phy']
#print(len(allphy))
rlc_1 = []
for rlc in allrlc:
    if rlc['rb_cfg_idx'] == '1':
        rlc_1.append(rlc)
rlc_1_sorted = sorted(rlc_1, key=lambda k: k['timestamp'])
final_bytes = 0
final_laten = 0
prevSFN = 0
totalBytes = 0
prevRLC = None
for rlc in rlc_1_sorted:
    if rlc['FI'] == '00':
        continue
    elif rlc['FI'] == '01':
        prevSFN = rlc['SFN']
        totalBytes = rlc['bytes']
        prevRLC = rlc
        continue
    elif rlc['FI'] == '11':
        totalBytes += rlc['bytes']
    elif rlc['FI'] == '10':
        laten = rlc['SFN'] - prevSFN
        totalBytes += rlc['bytes']
        if laten < -5000: # handle SFN overflow
            thisSFN = 10240 + rlc['SFN']
            laten = thisSFN - prevSFN
        else:
            thisSFN = rlc['SFN']
        print(prevSFN, thisSFN, laten, totalBytes)
        final_bytes += totalBytes
        final_laten += laten
        print(final_bytes)
        print(final_laten)
        print('\n')
        prevSFN = 0
        totalBytes = 0

print("Final Results")
print(final_laten)
print(final_bytes/1000000.0)
