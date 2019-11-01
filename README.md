# Custom MobileInsight analyzers for RAN latency

## Installation
Install the following to your machine and MI apk to your rooted android phone
- Python 2.7.12
- MobilieInsight 4.0
## Data Collection
Run MI and your desired Android application then
Collect *.mi2log* from the phone to a folder ./mi and run
## Run Analyzer
`$ python lte-analyzer.py ./mi 2> $YOUR_OUTPUT_FILE`
then run a script on this file. For example,
`$ python analyzeRANLatency.py $YOUR_OUTPUT_FILE`
to get the total RAN latency for your application
