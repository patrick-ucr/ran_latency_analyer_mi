# Custom MobileInsight Analyzer and Python Scripts for RAN-Level Analysis
- Custom MobileInsight analyzer to collect relevant information at PDCP, RLC, MAC and PHY layers of LTE
- Python scripts to extract insights into RAN latency, PHY network conditions, and RLC segmentation
- Open data collected and used to plot results in a paper under a peer review
## Installation
Install the following to your machine and MI apk to your rooted android phone
- Python 2.7.12
- MobilieInsight 4.0
## Data Collection
Run MI and your desired Android application then
Collect *.mi2log* from the phone to a folder ./mi and run the scripts
or download open data from [here](https://osf.io/mpnrw/?view_only=d4c253756a264f6face477cebb074eae)
## Run Analyzer
`$ python lte-analyzer.py ./mi 2> $YOUR_OUTPUT_FILE`
then run a script on this file. For example,
`$ python analyzeRANLatency.py $YOUR_OUTPUT_FILE`
to get the total RAN latency for your application
