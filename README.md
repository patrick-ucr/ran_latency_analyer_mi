# "Custom MobileInsight Analyzer and Python Scripts for RAN-Level Deep Analysis" Kittipat Apicharttrisorn (UC Riverside), Rajarajan Sivaraj (AT&T Labs Research, San Ramon, CA), and Rittwik Jana (AT&T Labs Research, Bedmister, NJ)
- Custom MobileInsight analyzer to collect relevant information at PDCP, RLC, MAC and PHY layers of LTE
- Python scripts to extract insights into RAN latency, PHY network conditions, and RLC segmentation
- Open data collected and used to plot results in a paper under a peer review

## Installation
Install the following to your machine and MI apk to your rooted android phone
- Python 2.7.12
- MobilieInsight 4.0
Replace PCDP, RLC, MAC, PHY analyzers in folder `/mobile_insight/analyzer` with the downloaded, custom analyzers of the same filenames. 

## Data Collection
Run MI and your desired Android application then
Collect *.mi2log* from the phone to a folder ./mi and run the scripts

## Run Analyzer
`$ python lte-analyzer.py ./mi 2> $YOUR_OUTPUT_FILE`
then run a script on this file. For example,
`$ python analyzeAggregateRANLatency.py $YOUR_OUTPUT_FILE`
to get the aggregate RAN latency for your application

## Publication
“Characterization of Multi-User Augmented Reality over Cellular Networks” K. Apicharttrisorn, Bharath Balasubramanian, Jiasi Chen, Rajarajan Sivaraj, Yu Zhou, Rittwik Jana, Srikanth Krishnamurthy, Tuyen Tran, and Yi-Zhen Tsai. IEEE SECON 2020 (to appear)
