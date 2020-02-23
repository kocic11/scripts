import json
import os
import sys
from functions import *

lenArgs = len(sys.argv)
if (lenArgs < 2) :
    print("Usage: python", sys.argv[0], "env.json")
    exit()

with open(sys.argv[1]) as f:
  config = json.load(f)

print("Scale up/down")
print(scale(config, "testjcs", "testjcs-wls-1", "VM.Standard2.1"))
print("Start/Stop")
print(startstop(config, "testjcs", "start"))
print("Activity Logs")
print(activity(config, "testjcs"))
