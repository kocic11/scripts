import json
import os
import sys
import argparse

from functions import *

parser = argparse.ArgumentParser()
parser.add_argument("env", help="JSON file with environment variables")
parser.add_argument("instance", help="JCS instance name")
# parser.add_argument("--start", help="Start JCS instance", action='store_true')
# parser.add_argument("--stop", help="Stop JCS instance", action='store_true')
# parser.add_argument("--scale", help="Scale JCS instance", action='store_true')
subparsers = parser.add_subparsers(help='sub-command help')
parser_scale = subparsers.add_parser("scale", help="Scale JCS instance")
# parser_scale.add_argument("scale", help="Scale JCS instance", action='store_true')
parser_scale.add_argument("hosts", help="comma separated list of JCS instance hosts")
parser_scale.add_argument("shape", help="JCS instance shape")
parser_start = subparsers.add_parser("start", help="Start JCS instance")
# parser_start.add_argument("start", action='store_true')
parser_stop = subparsers.add_parser("stop", help="Stop JCS instance")
# parser_stop.add_argument("stop", action='store_true')
parser_logs = subparsers.add_parser("logs", help="Show JCS instance activity logs")
# parser_logs.add_argument("logs", action='store_true')
args = parser.parse_args()

with open(args.env) as f:
  config = json.load(f)

if args.scale:
    print("Scale up/down")
    print(scale(config, args.instance, args.hosts, args.shape))

if args.stop or args.start:
  print("Start/Stop")
  print(startstop(config, args.instance, args.command))
if args.logs:
  print("Activity Logs")
  print(activity(config, args.instance))
