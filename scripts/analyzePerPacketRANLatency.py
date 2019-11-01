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


allpdcp = dldict['pdcp']
print(len(allpdcp))
allrlc = dldict['rlc']
print(len(allrlc))
allphy = dldict['phy']
print(len(allphy))


######## filter logical channel (rb_cfg_idx) #############
rlc_1 = []
carry_sn = 0
carry_sfn = 0 # rlc
sn_set = set()
sn_set.add(allrlc[0]['SN'])
rlc_1.append(allrlc[0])
for idx, rlc in enumerate(allrlc[1:]):
    # Check RB CFG IDX for your LTE
    if rlc['rb_cfg_idx'] == '3': #
    #if True:
        # cyclic SN
        rlc['SN'] += carry_sn * 1024
        if  rlc['SN'] - allrlc[idx-1]['SN'] < -1000: #
            print("Cyclic SN")
            print(rlc)
            print(allrlc[idx-1])
            carry_sn += 1
            rlc['SN'] += 1024
            print(rlc)

        # cyclic RLC SFN
        rlc['SFN'] += carry_sfn * 10240
        #print(rlc)
        if  rlc['SFN'] - allrlc[idx-1]['SFN'] < -9000: #
            print("Cyclic SFN")
            print(rlc)
            carry_sfn += 1
            rlc['SFN'] += 10240
            print(rlc)
        # handle dup RLC SN
        if (rlc['SN'] not in sn_set):
            sn_set.add(rlc['SN'])
            rlc_1.append(rlc)
        else:
            print("Duplicate SN %d"%rlc['SN'])

carry_sfn_pdcp = 0
# cyclic PDCP SFN
for idx, pdcp in enumerate(allpdcp[1:]):
    pdcp['SFN'] += carry_sfn_pdcp * 10240
    if  pdcp['SFN'] - allpdcp[idx-1]['SFN'] < -9000:
        carry_sfn_pdcp += 1
        pdcp['SFN'] += 10240
        #print(pdcp)

######### Main processing ##################
i=0 #index for curr_rlc_pdu
j=0 #index for curr_pdcp_pdu
curr_rlc_pdu = rlc_1[i:]
curr_pdcp_pdu = allpdcp[j:]
resid_pdcp_bytes = 0 #residual pdcp bytes
resid_rlc_bytes = 0
while j < len(curr_pdcp_pdu) and i < len(curr_rlc_pdu):
    print(curr_pdcp_pdu[j])
    print(curr_rlc_pdu[i])
    ################ CASE 1 ##########################
    if curr_rlc_pdu[i]['FI'] == '01' and curr_rlc_pdu[i]['E'] == '0':
        if abs(curr_pdcp_pdu[j]['SFN'] - curr_rlc_pdu[i]['SFN']) < 3:
            print('\n\n')
            print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
            print(resid_pdcp_bytes, resid_rlc_bytes)
            print(curr_pdcp_pdu[j])
            print(curr_rlc_pdu[i])
            resid_pdcp_bytes = curr_pdcp_pdu[j]['bytes'] - curr_rlc_pdu[i]['bytes']
            #tot_rlcpdu_size = curr_rlc_pdu[i]['bytes']
            curr_pdcp_pdu[j]['FIRST_RLC_PDU'] = curr_rlc_pdu[i]
            print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))
            if i+1 < len(curr_rlc_pdu):
                i+=1 #rlc advances
            else:
                break
            resid_rlc_bytes = 0
            print(curr_pdcp_pdu[j])
            print(curr_rlc_pdu[i])
        else:
            print("exception case 1")
            print(curr_rlc_pdu[i])
            print(curr_pdcp_pdu[j])
            # perhaps this pdcp is sent by another RLC logical channel (differet RB config index)
            if (curr_rlc_pdu[i]['timestamp'] > curr_pdcp_pdu[j]['timestamp']):
                while (curr_rlc_pdu[i]['timestamp'] > curr_pdcp_pdu[j]['timestamp']):
                    j+=1
            elif (curr_rlc_pdu[i]['timestamp'] < curr_pdcp_pdu[j]['timestamp']):
                while (curr_rlc_pdu[i]['timestamp'] < curr_pdcp_pdu[j]['timestamp']):
                    i+=1
            else:
                print("Found timestamp matched PDCP RLC")
                print(curr_rlc_pdu[i])
                print(curr_pdcp_pdu[j])
                if (curr_rlc_pdu[i]['SFN'] - curr_pdcp_pdu[j]['SFN'] > 3):
                    while (curr_rlc_pdu[i]['SFN'] - curr_pdcp_pdu[j]['SFN'] > 3):
                        j+=1
                elif (curr_pdcp_pdu[j]['SFN'] - curr_rlc_pdu[i]['SFN'] > 3):
                    while (curr_pdcp_pdu[j]['SFN'] - curr_rlc_pdu[i]['SFN'] > 3):
                        i+=1
                else:
                    print("Found TS and SFN matched PDCP RLC")
    ################ CASE 2 ##########################
    elif curr_rlc_pdu[i]['FI'] == '01' and curr_rlc_pdu[i]['E'] == '1':
        if abs(curr_pdcp_pdu[j]['SFN'] - curr_rlc_pdu[i]['SFN']) < 3:
            print('\n\n')
            print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
            print(resid_pdcp_bytes, resid_rlc_bytes)
            print(curr_pdcp_pdu[j])
            print(curr_rlc_pdu[i])
            curr_pdcp_pdu[j]['RLC_LATENCY'] = 1
            print(curr_pdcp_pdu[j])
            print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))
            resid_rlc_bytes = curr_rlc_pdu[i]['bytes'] - curr_pdcp_pdu[j]['bytes']
            if (j+1 < len(curr_pdcp_pdu)):
                j+=1
            else:
                break
            while resid_rlc_bytes >  curr_pdcp_pdu[j]['bytes']:
                resid_rlc_bytes -= curr_pdcp_pdu[j]['bytes']
                curr_pdcp_pdu[j]['RLC_LATENCY'] = 1
                print(curr_pdcp_pdu[j])
                print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))

                if (j+1 < len(curr_pdcp_pdu)):
                    j+=1
                else:
                    break
            curr_pdcp_pdu[j]['FIRST_RLC_PDU'] = curr_rlc_pdu[i]
            print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))
            resid_pdcp_bytes = curr_pdcp_pdu[j]['bytes'] - resid_rlc_bytes
            resid_rlc_bytes = 0
            if i+1 < len(curr_rlc_pdu):
                i+=1 #rlc advances
            else:
                break
        else:
            print("exception case 2")
            print(curr_rlc_pdu[i])
            print(curr_pdcp_pdu[j])
            # perhaps this pdcp is sent by another RLC logical channel (differet RB config index)
            if (curr_rlc_pdu[i]['timestamp'] > curr_pdcp_pdu[j]['timestamp']):
                while (curr_rlc_pdu[i]['timestamp'] > curr_pdcp_pdu[j]['timestamp']):
                    j+=1
            elif (curr_rlc_pdu[i]['timestamp'] < curr_pdcp_pdu[j]['timestamp']):
                while (curr_rlc_pdu[i]['timestamp'] < curr_pdcp_pdu[j]['timestamp']):
                    i+=1
            else:
                print("Found timestamp matched PDCP RLC")
                print(curr_rlc_pdu[i])
                print(curr_pdcp_pdu[j])
                if (curr_rlc_pdu[i]['SFN'] - curr_pdcp_pdu[j]['SFN'] > 3):
                    while (curr_rlc_pdu[i]['SFN'] - curr_pdcp_pdu[j]['SFN'] > 3):
                        j+=1
                elif (curr_pdcp_pdu[j]['SFN'] - curr_rlc_pdu[i]['SFN'] > 3):
                    while (curr_pdcp_pdu[j]['SFN'] - curr_rlc_pdu[i]['SFN'] > 3):
                        i+=1
                else:
                    print("Found TS and SFN matched PDCP RLC")
    ################ CASE 3 ##########################
    elif curr_rlc_pdu[i]['FI'] == '10' and curr_rlc_pdu[i]['E'] == '0':
        print('\n\n')
        print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
        print(resid_pdcp_bytes, resid_rlc_bytes)
        print(curr_rlc_pdu[i])
        print(curr_pdcp_pdu[j])
        curr_pdcp_pdu[j]['LAST_RLC_PDU'] = curr_rlc_pdu[i]
        if 'FIRST_RLC_PDU' in curr_pdcp_pdu[j]:
            curr_pdcp_pdu[j]['RLC_LATENCY'] = 1 + curr_pdcp_pdu[j]['LAST_RLC_PDU']['SFN'] - curr_pdcp_pdu[j]['FIRST_RLC_PDU']['SFN']
            print(curr_pdcp_pdu[j])
        else:
            print("Error: no FIRST RLC PDU")
            print(curr_pdcp_pdu[j])
        resid_pdcp_bytes = 0
        resid_rlc_bytes = 0
        if i+1 < len(curr_rlc_pdu) and j+1 < len(curr_pdcp_pdu):
            i+=1 #rlc advances
            j+=1 #pdcp advances
        else:
            break
    ################ CASE 4 ##########################
    elif curr_rlc_pdu[i]['FI'] == '11' and curr_rlc_pdu[i]['E'] == '1':
        print('\n\n')
        print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
        print(resid_pdcp_bytes, resid_rlc_bytes)
        print(curr_pdcp_pdu[j])
        print(curr_rlc_pdu[i])
        resid_rlc_bytes = curr_rlc_pdu[i]['bytes'] - resid_pdcp_bytes
        curr_pdcp_pdu[j]['LAST_RLC_PDU'] = curr_rlc_pdu[i]
        if 'FIRST_RLC_PDU' in curr_pdcp_pdu[j]:
            curr_pdcp_pdu[j]['RLC_LATENCY'] = 1 + curr_pdcp_pdu[j]['LAST_RLC_PDU']['SFN'] - curr_pdcp_pdu[j]['FIRST_RLC_PDU']['SFN']
            print(curr_pdcp_pdu[j])
        else:
            print("Error: no FIRST RLC PDU")
            print(curr_pdcp_pdu[j])

        if (j+1 < len(curr_pdcp_pdu)):
            j+=1
        else:
            break
        while resid_rlc_bytes >  curr_pdcp_pdu[j]['bytes']:
            resid_rlc_bytes -= curr_pdcp_pdu[j]['bytes']
            curr_pdcp_pdu[j]['RLC_LATENCY'] = 1
            print(curr_pdcp_pdu[j])
            if (j+1 < len(curr_pdcp_pdu)):
                j+=1
            else:
                break
        resid_pdcp_bytes = curr_pdcp_pdu[j]['bytes'] - resid_rlc_bytes \
            if curr_pdcp_pdu[j]['bytes'] > resid_rlc_bytes else 0
        resid_rlc_bytes = 0
        curr_pdcp_pdu[j]['FIRST_RLC_PDU'] = curr_rlc_pdu[i]
        print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))

        if( i+1 < len(curr_rlc_pdu)):
            i+=1
        else:
            break

    ################ CASE 5 ##########################
    elif curr_rlc_pdu[i]['FI'] == '00' and curr_rlc_pdu[i]['E'] == '1':
        print('\n\n')
        print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
        print(resid_pdcp_bytes, resid_rlc_bytes)
        print(curr_pdcp_pdu[j])
        print(curr_rlc_pdu[i])
        resid_rlc_bytes = curr_rlc_pdu[i]['bytes'] - curr_pdcp_pdu[j]['bytes']
        curr_pdcp_pdu[j]['RLC_LATENCY'] = 1
        print(curr_pdcp_pdu[j])
        print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))
        if ( j+1 < len(curr_pdcp_pdu)):
            j+=1
        else:
            break
        while resid_rlc_bytes >  curr_pdcp_pdu[j]['bytes']:
            print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))
            resid_rlc_bytes -= curr_pdcp_pdu[j]['bytes']
            curr_pdcp_pdu[j]['RLC_LATENCY'] = 1
            print(curr_pdcp_pdu[j])
            if ( j+1 < len(curr_pdcp_pdu)):
                j+=1
            else:
                break
        resid_pdcp_bytes = 0
        resid_rlc_bytes = 0
        if (i+1 < len(curr_rlc_pdu)):
            i+=1
        else:
            break
    ################ CASE 6 ##########################
    elif curr_rlc_pdu[i]['FI'] == '11' and curr_rlc_pdu[i]['E'] == '0':
        print('\n\n')
        print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
        print(resid_pdcp_bytes, resid_rlc_bytes)
        print(curr_pdcp_pdu[j])
        print(curr_rlc_pdu[i])
        resid_pdcp_bytes = resid_pdcp_bytes - curr_rlc_pdu[i]['bytes'] \
            if resid_pdcp_bytes > curr_rlc_pdu[i]['bytes'] else 0
        resid_rlc_bytes = 0
        if (i+1 < len(curr_rlc_pdu)):
            i+=1 #rlc advances
        else:
            break
    ################ CASE 7 ##########################
    elif curr_rlc_pdu[i]['FI'] == '00' and curr_rlc_pdu[i]['E'] == '0':
        print('\n\n')
        print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
        print(resid_pdcp_bytes, resid_rlc_bytes)
        print(curr_pdcp_pdu[j])
        print(curr_rlc_pdu[i])
        #curr_pdcp_pdu[j]['FIRST_RLC_PDU'] = curr_rlc_pdu[i]
        #curr_pdcp_pdu[j]['LAST_RLC_PDU'] = curr_rlc_pdu[i]
        curr_pdcp_pdu[j]['RLC_LATENCY'] = 1
        print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))
        print(curr_pdcp_pdu[j])
        resid_rlc_bytes = 0
        resid_pdcp_bytes = 0
        if (i+1 < len(curr_rlc_pdu) and j+1 < len(curr_pdcp_pdu)):
            i+=1 #rlc advances
            j+=1 #pdcp advances
        else:
            break
    ################ CASE 8 ##########################
    elif curr_rlc_pdu[i]['FI'] == '10' and curr_rlc_pdu[i]['E'] == '1':
        print('\n\n')
        print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
        print(resid_pdcp_bytes, resid_rlc_bytes)
        print(curr_pdcp_pdu[j])
        print(curr_rlc_pdu[i])
        curr_pdcp_pdu[j]['LAST_RLC_PDU'] = curr_rlc_pdu[i]
        if 'FIRST_RLC_PDU' in curr_pdcp_pdu[j]:
            curr_pdcp_pdu[j]['RLC_LATENCY'] = 1 + curr_pdcp_pdu[j]['LAST_RLC_PDU']['SFN'] - curr_pdcp_pdu[j]['FIRST_RLC_PDU']['SFN']
            print(curr_pdcp_pdu[j])
        else:
            print("Error: no FIRST RLC PDU")
            print(curr_pdcp_pdu[j])
        if (j+1 < len(curr_pdcp_pdu)):
            j+=1
        else:
            break
        resid_rlc_bytes = curr_rlc_pdu[i]['bytes'] - resid_pdcp_bytes
        print(resid_pdcp_bytes, resid_rlc_bytes)
        while resid_rlc_bytes >  curr_pdcp_pdu[j]['bytes']:
            resid_rlc_bytes -= curr_pdcp_pdu[j]['bytes']
            curr_pdcp_pdu[j]['RLC_LATENCY'] = 1
            print(curr_pdcp_pdu[j])
            print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))

            if (j+1 < len(curr_pdcp_pdu)):
                j+=1
            else:
                break
        """
        if (curr_pdcp_pdu[j]['timestamp'] <= curr_rlc_pdu[i]['timestamp']):
            resid_rlc_bytes = curr_rlc_pdu[i]['bytes'] - resid_pdcp_bytes
            j+=1
            while resid_rlc_bytes >  curr_pdcp_pdu[j]['bytes']\
                and curr_pdcp_pdu[j]['timestamp'] <= curr_rlc_pdu[i]['timestamp']:
                resid_rlc_bytes -= curr_pdcp_pdu[j]['bytes']
                j+=1
        """
        resid_pdcp_bytes = 0
        resid_rlc_bytes = 0
        if (i+1 < len(curr_rlc_pdu)):
            i+=1
        else:
            break
    else:
        print("exception case")
        print(curr_rlc_pdu[i])
        print(curr_pdcp_pdu[j])
        # perhaps this pdcp is sent by another RLC logical channel (differet RB config index)
        if (curr_rlc_pdu[i]['timestamp'] > curr_pdcp_pdu[j]['timestamp']):
            while (curr_rlc_pdu[i]['timestamp'] > curr_pdcp_pdu[j]['timestamp']):
                j+=1
        elif (curr_rlc_pdu[i]['timestamp'] < curr_pdcp_pdu[j]['timestamp']):
            while (curr_rlc_pdu[i]['timestamp'] < curr_pdcp_pdu[j]['timestamp']):
                i+=1
        else:
            print("Found matched PDCP RLC")
            print(curr_rlc_pdu[i])
            print(curr_pdcp_pdu[j])
foldername = os.path.dirname(filelocation)
filename = os.path.basename(filelocation).split('.')[0]
print(foldername)
print(filename)
zero_laten_list = []
one_laten_list = []
two_laten_list = []
gt_two_laten_list = []
total_latency = 0
with open(foldername+'/'+filename+'_RLC_Latency.log','w') as f:
    for pdcp in curr_pdcp_pdu:
        if 'RLC_LATENCY' in pdcp:
            f.write(str(pdcp['SFN'])+','+str(pdcp['RLC_LATENCY'])+'\n')
            laten = pdcp['RLC_LATENCY']
            total_latency += laten

print("\n\nTotal RLC Latency: %d\n"%total_latency)
