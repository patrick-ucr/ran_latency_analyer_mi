#!/usr/bin/python
# Filename: lte_pdcp_analyzer.py
"""
A 4G PDCP analyzer to get link layer information

Author: Haotian Deng
"""


from mobile_insight.analyzer.analyzer import *
from xml.dom import minidom

__all__ = ["LtePdcpAnalyzer"]


class LtePdcpAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        
        self.add_source_callback(self.__msg_callback)
        
        self.pdcpPduULCipherDict = {}
        self.pdcpPacketULCount = 0
        self.pdcpULPduCount = 0
    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Phy-layer logs
        #source.enable_log("LTE_PDCP_DL_Config")
        #source.enable_log("LTE_PDCP_UL_Config")
        #source.enable_log("LTE_PDCP_UL_Data_PDU")
        #source.enable_log("LTE_PDCP_DL_Ctrl_PDU")
        #source.enable_log("LTE_PDCP_UL_Ctrl_PDU")
        #source.enable_log("LTE_PDCP_DL_Stats")
        #source.enable_log("LTE_PDCP_UL_Stats")
        #source.enable_log("LTE_PDCP_DL_SRB_Integrity_Data_PDU")
        #source.enable_log("LTE_PDCP_UL_SRB_Integrity_Data_PDU")
        source.enable_log("LTE_PDCP_UL_Cipher_Data_PDU")
    def __msg_callback(self, msg):
        #s = msg.data.decode_xml().replace("\n", "")
        #print minidom.parseString(s).toprettyxml(" ")
        if msg.type_id == "LTE_PDCP_UL_Cipher_Data_PDU":
            
            self.pdcpPacketULCount += 1
            self.log_info("[PDCP UL Packet Count]\t " + str(self.pdcpPacketULCount))
            log_item = msg.data.decode()
            # print log_item
            timestamp = str(log_item['timestamp'])
            subPkt = log_item['Subpackets'][0]
            subPktSize = str(subPkt['Subpacket Size'])
            listPDU = subPkt['PDCPUL CIPH DATA']
            self.pdcpPduULCipherDict = {}
            totalPduSize = 0
            self.log_info("[PDCP UL PDU Start]")
            for pdu in listPDU:
                self.pdcpULPduCount += 1
                self.pdcpPduULCipherDict['PDU Size'] = str(pdu['PDU Size'])    
                totalPduSize += int(pdu['PDU Size']) 
                self.pdcpPduULCipherDict['Sub FN'] = str(pdu['Sub FN'])
                self.pdcpPduULCipherDict['Sys FN'] = str(pdu['Sys FN'])
                self.pdcpPduULCipherDict['SN'] = str(pdu['SN'])
                self.log_info("[PDCP UL PDU Info]\t"+"Timestamp: "+timestamp+\
                    " SN: "+self.pdcpPduULCipherDict['SN']+\
                    " PDU Size: "+self.pdcpPduULCipherDict['PDU Size']+\
                    " Sys FN: "+self.pdcpPduULCipherDict['Sys FN']+\
                    " Sub FN: "+self.pdcpPduULCipherDict['Sub FN']
                    )
            self.log_info("[PDCP UL PDU End]")
            self.log_info("[PDCP UL Total Data Size]: "+timestamp+" Subpacket Size: "+subPktSize+" Total PDU Size: "+str(totalPduSize))
            self.log_info("[PDCP UL Total PDU Count]: " +str(self.pdcpULPduCount))


