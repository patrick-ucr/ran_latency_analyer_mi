import sys
import pprint 
import datetime
pp = pprint.PrettyPrinter(indent=4)
import matplotlib.pyplot as plt
import os
import statistics as stats
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
print(len(allpdcp))
allrlc = dldict['rlc']
print(len(allrlc))
allphy = dldict['phy']
print(len(allphy))
#allpdcp = sorted(allpdcp, key=lambda k: (k['timestamp'], k['SN']))
#allrlc = sorted(allrlc, key=lambda k: (k['timestamp'], k['SN']))
#allphy = sorted(allphy, key=lambda k: (k['timestamp'], k['SFN']))

#for rlc in allrlc:
#    pprint.pprint(rlc)
######## filter logical channel (rb_cfg_idx) #############
rlc_1 = []
carry_sn = 0
carry_sfn = 0 # rlc
sn_set = set()
sn_set.add(allrlc[0]['SN'])
rlc_1.append(allrlc[0])
for idx, rlc in enumerate(allrlc[1:]):
    # RB CFG IDX = 1 (ASOCS)
    if rlc['rb_cfg_idx'] == '4': # 1 for private ASOCS and 3 for public AT&T
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

#for rlc in rlc_1:
#    print(rlc)

#for item in zip(allpdcp,rlc_1):
#    print(item[0]['SN'],item[0]['SFN'],item[1]['SN'],item[1]['SFN'])

#sys.exit()

rlc_bytes = []
for rlc in rlc_1:
    rlc_bytes.append(int(rlc['bytes']))
print("Average RLC PDU Bytes: %d"%(sum(rlc_bytes)/len(rlc_bytes)))
"""
########## Check sorted SN ###########################

prevTS = rlc_1_sorted[0]['timestamp']
prevSN = rlc_1_sorted[0]['SN']
for k,rlc in enumerate(rlc_1_sorted[1:]):
    if rlc['timestamp'] == prevTS:
        if rlc['SN'] == prevSN + 1:
            prevSN = rlc['SN']
            
        else:
            print("error")
            print(rlc_1_sorted[k-1])
            print(rlc)
    else:
        prevTS = rlc['timestamp']
        prevSN = rlc['SN']
"""
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
        if abs(curr_pdcp_pdu[j]['SFN'] - curr_rlc_pdu[i]['SFN']) <= 3:
            print('\n\n')
            print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
            print(resid_pdcp_bytes, resid_rlc_bytes)
            print(curr_pdcp_pdu[j])
            print(curr_rlc_pdu[i])
            resid_pdcp_bytes = curr_pdcp_pdu[j]['bytes'] - curr_rlc_pdu[i]['bytes']
            #tot_rlcpdu_size = curr_rlc_pdu[i]['bytes']
            curr_pdcp_pdu[j]['FIRST_RLC_PDU'] = curr_rlc_pdu[i]
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
            print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))
            if i+1 < len(curr_rlc_pdu):
                i+=1 #rlc advances
                if 'NUM_RLC_PDU' in curr_pdcp_pdu[j]:
                    curr_pdcp_pdu[j]['NUM_RLC_PDU'] += 1
                else:
                    curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1            
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
                    continue
    ################ CASE 2 ##########################
    elif curr_rlc_pdu[i]['FI'] == '01' and curr_rlc_pdu[i]['E'] == '1':
        if abs(curr_pdcp_pdu[j]['SFN'] - curr_rlc_pdu[i]['SFN']) <= 3:
            print('\n\n')
            print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
            print(resid_pdcp_bytes, resid_rlc_bytes)
            print(curr_pdcp_pdu[j])
            print(curr_rlc_pdu[i])
            curr_pdcp_pdu[j]['RLC_LATENCY'] = 1
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
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
                curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
                print(curr_pdcp_pdu[j])
                print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))

                if (j+1 < len(curr_pdcp_pdu)):
                    j+=1
                else: 
                    break            
            curr_pdcp_pdu[j]['FIRST_RLC_PDU'] = curr_rlc_pdu[i]
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
            print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))
            resid_pdcp_bytes = curr_pdcp_pdu[j]['bytes'] - resid_rlc_bytes
            resid_rlc_bytes = 0
            if i+1 < len(curr_rlc_pdu):
                i+=1 #rlc advances
                if 'NUM_RLC_PDU' in curr_pdcp_pdu[j]:
                    curr_pdcp_pdu[j]['NUM_RLC_PDU'] += 1
                else:
                    curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
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
                    continue    
    ################ CASE 3 ##########################
    elif curr_rlc_pdu[i]['FI'] == '10' and curr_rlc_pdu[i]['E'] == '0':
        print('\n\n')
        print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
        print(resid_pdcp_bytes, resid_rlc_bytes)
        print(curr_rlc_pdu[i])
        print(curr_pdcp_pdu[j])
        curr_pdcp_pdu[j]['LAST_RLC_PDU'] = curr_rlc_pdu[i]
        if 'NUM_RLC_PDU' in curr_pdcp_pdu[j]:
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] += 1
        else:
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
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
        if 'NUM_RLC_PDU' in curr_pdcp_pdu[j]:
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] += 1
        else:
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1

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
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
            print(curr_pdcp_pdu[j])
            if (j+1 < len(curr_pdcp_pdu)):
                j+=1
            else:
                break
        resid_pdcp_bytes = curr_pdcp_pdu[j]['bytes'] - resid_rlc_bytes \
            if curr_pdcp_pdu[j]['bytes'] > resid_rlc_bytes else 0
        resid_rlc_bytes = 0
        curr_pdcp_pdu[j]['FIRST_RLC_PDU'] = curr_rlc_pdu[i]
        curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
        print("Initial Scheduling Delay: %d"%(curr_rlc_pdu[i]['SFN']-curr_pdcp_pdu[j]['SFN']))

        if( i+1 < len(curr_rlc_pdu)):
            i+=1
            if 'NUM_RLC_PDU' in curr_pdcp_pdu[j]:
                curr_pdcp_pdu[j]['NUM_RLC_PDU'] += 1
            else:
                curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
        else:
            break
        
        """
        got_error_break = False  
        tot_rlcpdu_size += curr_rlc_pdu[i]['bytes']
        while tot_rlcpdu_size >= curr_pdcp_pdu[j]['bytes']:
            if curr_pdcp_pdu[j]['timestamp'] > curr_rlc_pdu[i]['timestamp']:
                log_time_delta = curr_pdcp_pdu[j]['timestamp']-curr_rlc_pdu[i]['timestamp']
                print(log_time_delta)
                log_time_diff_ms = (log_time_delta.seconds * 1000000 + log_time_delta.microseconds) / 1000
                print(log_time_diff_ms)
            else:
                log_time_delta = curr_rlc_pdu[i]['timestamp']-curr_pdcp_pdu[j]['timestamp']
                print(log_time_delta)
                log_time_diff_ms = (log_time_delta.seconds * 1000000 + log_time_delta.microseconds) / 1000
                print(log_time_diff_ms)

            #if (abs(curr_pdcp_pdu[j]['SFN'] - curr_rlc_pdu[i]['SFN']) > 200):
            if (log_time_diff_ms > 200):
                print("bytes matching error")
                # go back to lastest pdcp pdu with FIRST_RLC_PDU
                k=j
                while 'FIRST_RLC_PDU' not in curr_pdcp_pdu[k]:
                    k-=1
                
                print(curr_rlc_pdu[i])
                curr_pdcp_pdu[k]['LAST_RLC_PDU'] = curr_rlc_pdu[i]
                curr_pdcp_pdu[k]['RLC_LATENCY'] = curr_pdcp_pdu[k]['LAST_RLC_PDU']['SFN'] - curr_pdcp_pdu[k]['FIRST_RLC_PDU']['SFN']
                print (curr_pdcp_pdu[k])
                print(curr_pdcp_pdu[j])
                #### advance to match SFN ###
                while curr_rlc_pdu[i]['timestamp'] < curr_pdcp_pdu[j]['timestamp']:
                    print(curr_rlc_pdu[i])
                    i+=1
                print(curr_rlc_pdu[i])
                #i+=1 #advance to FI 01 
                got_error_break = True
                break
            tot_rlcpdu_size -= curr_pdcp_pdu[j]['bytes'] #residual rlc bytes
            j+=1 #pdcp advances
            print(tot_rlcpdu_size)
            print(curr_pdcp_pdu[j])
            print(curr_rlc_pdu[i])
            #print(curr_pdcp_pdu[j]['timestamp']-curr_rlc_pdu[i]['timestamp'])
        if (not got_error_break):
            i+=1 #rlc advances
        """
    ################ CASE 5 ##########################
    elif curr_rlc_pdu[i]['FI'] == '00' and curr_rlc_pdu[i]['E'] == '1':
        print('\n\n')
        print(curr_rlc_pdu[i]['FI'],curr_rlc_pdu[i]['E'])
        print(resid_pdcp_bytes, resid_rlc_bytes)
        print(curr_pdcp_pdu[j])
        print(curr_rlc_pdu[i])
        resid_rlc_bytes = curr_rlc_pdu[i]['bytes'] - curr_pdcp_pdu[j]['bytes']
        curr_pdcp_pdu[j]['RLC_LATENCY'] = 1
        curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
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
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
            print(curr_pdcp_pdu[j])
            if ( j+1 < len(curr_pdcp_pdu)):
                j+=1
            else:
                break        
        resid_pdcp_bytes = 0
        resid_rlc_bytes = 0
        if (i+1 < len(curr_rlc_pdu)):
            i+=1
            if 'NUM_RLC_PDU' in curr_pdcp_pdu[j]:
                curr_pdcp_pdu[j]['NUM_RLC_PDU'] += 1
            else:
                curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
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
            if 'NUM_RLC_PDU' in curr_pdcp_pdu[j]:
                curr_pdcp_pdu[j]['NUM_RLC_PDU'] += 1
            else:
                curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
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
        curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
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
        if 'NUM_RLC_PDU' in curr_pdcp_pdu[j]:
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] += 1
        else:
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
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
            curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
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
            if 'NUM_RLC_PDU' in curr_pdcp_pdu[j]:
                curr_pdcp_pdu[j]['NUM_RLC_PDU'] += 1
            else:
                curr_pdcp_pdu[j]['NUM_RLC_PDU'] = 1
 
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
num_rlc_pdu_list = []
total_bytes = 0
total_latency = 0
with open(foldername+'/'+filename+'_RLC_Latency.log','w') as f:
    for pdcp in curr_pdcp_pdu: 
        if 'RLC_LATENCY' in pdcp:
            f.write(str(pdcp['SFN'])+','+str(pdcp['RLC_LATENCY'])+'\n')
            laten = pdcp['RLC_LATENCY']
            total_latency += laten
            total_bytes += pdcp['bytes']
            if laten == 0:
                zero_laten_list.append(0)
            elif laten == 1:
                one_laten_list.append(1)
            elif laten == 2:
                two_laten_list.append(2)
            elif laten > 2:
                gt_two_laten_list.append(laten)
            else: 
                print("Error laten: %d"%laten)
        if 'NUM_RLC_PDU' in pdcp:
            num_rlc_pdu_list.append(int(pdcp['NUM_RLC_PDU']))
print("\n\nTotal RLC Latency: %d\nTotal Bytes: %.2f"%(total_latency,total_bytes/1000000.0)) 
print("Average Number of RLC PDUs per IP Packet: %.2f %.2f"%(stats.mean(num_rlc_pdu_list),stats.stdev(num_rlc_pdu_list)))
rlc_bytes = []
for rlc in rlc_1:
    rlc_bytes.append(int(rlc['bytes']))
print("RLC PDU Bytes: mean %.2f stdev %.2f"%(stats.mean(rlc_bytes),stats.stdev(rlc_bytes)))
total_len = len(zero_laten_list)+len(one_laten_list)+len(two_laten_list)+len(gt_two_laten_list)
print("RLC Concatenation: %.2f"%((len(zero_laten_list)+len(one_laten_list))/float(total_len)))
print("RLC Segmentation: %.2f"%((len(two_laten_list)+len(gt_two_laten_list))/float(total_len)))
print("Total RLC Segmentation Latency (No Propagation) %d ms"%(len(two_laten_list)+sum(gt_two_laten_list)-len(gt_two_laten_list))) 


print("Number of 0 RLC latency components: %d"%len(zero_laten_list))
print("Number of 1 RLC latency components: %d"%len(one_laten_list))
print("Number of 2 RLC latency components: %d"%len(two_laten_list))
print("Number of >2 RLC latency components: %d"%len(gt_two_laten_list))
print("Sum of >2 RLC latency components: %d"%sum(gt_two_laten_list)) 
