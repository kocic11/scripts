from functions import start, stop, scale, activity, jobid
import argparse
import requests

#TESTS
def test_stop():
    args = argparse.Namespace()
    args.env = "mockenv.json"
    args.instance = "testjcs"
    args.stop = "stop"
    args.email = False
    result, response = stop(args)
    assert requests.codes.ACCEPTED == response.status_code

def test_start():
    args = argparse.Namespace()
    args.env = "mockenv.json"
    args.instance = "testjcs"
    args.start = "start"
    args.email = False
    result, response = start(args)
    assert requests.codes.ACCEPTED == response.status_code

def test_scale_accepted():
    args = argparse.Namespace()
    args.env = "mockenv.json"
    args.instance = "testjcs"
    args.scale = "scale"
    args.hosts = "testjcs-wls-1"
    args.shape = "VM.Standard2.1"
    args.email = False
    result, response = scale(args)
    assert requests.codes.ACCEPTED == response.status_code

def test_scale_bad():
    args = argparse.Namespace()
    args.env = "mockenv.json"
    args.instance = "testjcs"
    args.scale = "scale"
    args.hosts = "testjcs-wls-1,testjcs-wls-2"
    args.shape = "VM.Standard2.1"
    args.email = False
    result, response = scale(args)
    assert requests.codes.BAD == response.status_code

def test_jobid():
    args = argparse.Namespace()
    args.env = "mockenv.json"
    args.instance = "testjcs"
    args.jobid = "190047607"
    args.email = "false"
    result, response = jobid(args)
    assert requests.codes.OK == response.status_code