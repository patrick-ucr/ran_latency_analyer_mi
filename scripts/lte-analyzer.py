#!/usr/bin/python
# Filename: offline-analysis-example.py
import os
import sys
import logging
"""
Offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRrcAnalyzer, WcdmaRrcAnalyzer, LteNasAnalyzer, UmtsNasAnalyzer, LtePhyAnalyzer, LteMacAnalyzer, LtePdcpAnalyzer, LteRlcAnalyzer, LteCustomAnalyzer

log_file_location = str(sys.argv[1])
log_folder = os.path.dirname(log_file_location)
LOGMSG = False
logmsg_filename = str(os.path.basename(log_file_location).split(".")[0]) + "_log.xml"
MSGLOGGER = False

if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path(log_file_location)
    #src.enable_log_all()
      
    if (MSGLOGGER):
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as(log_folder+"/"+logmsg_filename)
        logger.set_source(src)

    # Analyzers
    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
    wcdma_rrc_analyzer.set_source(src)  # bind with the monitor

    lte_nas_analyzer = LteNasAnalyzer()
    lte_nas_analyzer.set_source(src)

    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(src)
    # PDCP
    lte_pdcp_analyzer = LtePdcpAnalyzer()
    lte_pdcp_analyzer.set_source(src)
    # RLC
    lte_rlc_analyzer = LteRlcAnalyzer()
    #lte_rlc_analyzer.set_log("analyzers.log",logging.DEBUG)
    lte_rlc_analyzer.set_source(src)
    # MAC
    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)
    # PHY
    lte_phy_analyzer = LtePhyAnalyzer()
    lte_phy_analyzer.set_source(src)
    # Custom
    #lte_custom_analyzer = LteCustomAnalyzer()
    #lte_custom_analyzer.set_source(src)
    # Start the monitoring
    src.run()
