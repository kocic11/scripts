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

print(scale(config))
print(startstop(config))
print(activity(config))
