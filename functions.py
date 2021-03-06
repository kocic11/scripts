import argparse
import json
import os
import sys
from datetime import date
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import logging
import logging.config
from logging import handlers

from os import path
#Change this
parser = None
logger = None

result = json.loads(
    """
  {
    "details": {
      "message": ""
    }
  }
  """
)


def __getEnv(env):
    with open(env) as f:
        config = json.load(f)
    params = {}
    params["user"] = config.get("user")
    params["password"] = config.get("password")
    params["id_tenant_name"] = config.get("id-tenant-name")
    params["jaas_uri"] = config.get("jaas_uri")
    params["email"] = {
        "email_server": config.get("email_server"),
        "email_server_port": config.get("email_server_port"),
        "email_server_port_ssl": config.get("email_server_port_ssl"),
        "email_user": config.get("email_user"),
        "email_user_password": config.get("email_user_password"),
        "email_from": config.get("email_from"),
        "email_to": config.get("email_to"),
        "email_subject": config.get("email_subject")
    }
    params["auth"] = (params["user"], params["password"])
    params["headers"] = {
        "content-type": "application/json",
        "X-ID-TENANT-NAME": params["id_tenant_name"]
    }

    # Postman Mock Server requirement
    mock_header = config.get("x-mock-match-request-body")
    if mock_header != None:
        params["headers"].update({"x-mock-match-request-body": mock_header})

    return params

def __setLogger(args):
  global logger
  try:
    with open("C:/Users/AKOCIC/Work/Code/scripts/log_conf.json") as f:
      config = json.load(f)
    logging.config.dictConfig(config["logging"])
    logger = logging.getLogger("functions")
  except:
    import traceback
    exc_type, exc_value, exc_tb = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_tb)
    pass

def __send_email(email, message):
    try:
        if email["email_server_port_ssl"] == "true":
            smtp_server = smtplib.SMTP_SSL(
                host=email["email_server"], port=email["email_server_port"])
            logger.debug("Using SSL port")
        else:
            smtp_server = smtplib.SMTP(
                host=email["email_server"], port=email["email_server_port"])
            logger.debug("Using non SSL port")
        smtp_server.login(email["email_user"], email["email_user_password"])
        logger.debug("Logged to email server")
        msg = MIMEMultipart()
        msg["From"] = email["email_from"]
        msg["To"] = email["email_to"]
        msg["Subject"] = email["email_subject"]
        msg.attach(
            MIMEText(str(json.dumps(message, indent=2, sort_keys=True)), "plain"))
        smtp_server.send_message(msg)
        logger.debug("Sent email")
    except:
        logger.error(sys.exc_info()[0])
        pass


def __startstop(args, command):
    """Return the result of the JCS instance start/stop operation."""
    global result
    data = json.loads(
        """
      {
        "allServiceHosts" : "true"
      } 
      """
    )

    params = __getEnv(args.env)
    uri = params["jaas_uri"] + "/instancemgmt/" + params["id_tenant_name"] + \
        "/services/jaas/instances/" + args.instance + "/hosts/" + command
    result, response = __post(uri, params, data)

    if args.email:
        __send_email(params["email"], result)

    return result, response


def __post(uri, params, data):
    global result
    try:
        response = requests.post(
            uri, auth=params["auth"], headers=params["headers"], data=json.dumps(data))
        if response.status_code == requests.codes.ACCEPTED:
            result = response.json()
        else:
            result["details"]["message"] = "Unexpected error: " + \
                str(response.status_code) + ", " +\
                response.text
    except:
        result["details"]["message"] = "Unexpected error: " + \
            str(sys.exc_info()[0])
        pass
    return result, response


def __get(uri, params):
    try:
        response = requests.get(
            uri, auth=params["auth"], headers=params["headers"])
        if response.status_code == requests.codes.OK:
            result = response.json()
        else:
            result["details"]["message"] = "Unexpected error: " + \
                str(response.status_code)
    except:
        result["details"]["message"] = "Unexpected error: " + \
            str(sys.exc_info()[0])
        pass
    return result, response


def jobid(args):
    """Return the the JCS instance operation status by job id."""
    __setLogger(args)
    global result
    params = __getEnv(args.env)
    
    # Postman Mock Server requirement
    params["headers"].pop("x-mock-match-request-body", None)
    
    uri = params["jaas_uri"] + "/activitylog/" + \
        params["id_tenant_name"] + "/job/" + args.jobid

    return __get(uri, params)


def scale(args):
    """Return the result of the JCS instance scale up/down operation."""
    __setLogger(args)
    global result
    data = json.loads(
        """
    {
      "components": {
          "WLS": {
            "hosts": [],
            "shape": "",
            "ignoreManagedServerHeapError": "true"
          }
      }
    }
    """
    )

    params = __getEnv(args.env)

    uri = params["jaas_uri"] + "/instancemgmt/" + params["id_tenant_name"] + \
        "/services/jaas/instances/" + args.instance + "/hosts/scale"
    data["components"]["WLS"]["hosts"] = args.hosts.split(",")
    data["components"]["WLS"]["shape"] = args.shape

    result, response = __post(uri, params, data)

    if args.email:
        __send_email(params["email"], result)

    return result, response


def start(args):
    """Return the result of the JCS instance start operation."""
    __setLogger(args)
    return __startstop(args, "start")


def stop(args):
    """Return the result of the JCS instance stop operation."""
    __setLogger(args)
    return __startstop(args, "stop")


def activity(args):
    """Return the the JCS instance operations activity logs."""
    __setLogger(args)
    global result
    params = __getEnv(args.env)
    uri = params["jaas_uri"] + "/activitylog/" + params["id_tenant_name"] + "/filter?serviceName=" + \
        args.instance + "&fromStartDate=" + args.fromStartDate

    return __get(uri, params)


def print_usage(args):
    global parser
    parser.print_usage()
    exit()


def main():
    
    global parser
    parser = argparse.ArgumentParser()
    parser.add_argument("env", help="JSON file with environment variables")
    parser.add_argument("instance", help="JCS instance name")
    parser.add_argument("-e", "--email", help="Send email",
                        action='store_true')
    parser.add_argument("-v", "--verbose", help="Print verbose information",
                        action='store_true')
    parser.set_defaults(func=print_usage)
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_scale = subparsers.add_parser("scale", help="Scale JCS instance")
    parser_scale.add_argument(
        "scale", help="Scale JCS instance", action='store_true')
    parser_scale.add_argument(
        "hosts", help="comma separated list of JCS instance hosts")
    parser_scale.add_argument("shape", help="JCS instance shape")
    parser_scale.set_defaults(func=scale)
    parser_start = subparsers.add_parser("start", help="Start JCS instance")
    parser_start.add_argument("start", action='store_true')
    parser_start.set_defaults(func=start)
    parser_stop = subparsers.add_parser("stop", help="Stop JCS instance")
    parser_stop.add_argument("stop", action='store_true')
    parser_stop.set_defaults(func=stop)
    parser_logs = subparsers.add_parser(
        "logs", help="Show JCS instance activity logs")
    parser_logs.add_argument("logs", action='store_true')
    parser_logs.add_argument(
        "-d", "--fromStartDate", help="Filter activities based on start date (YYYY-MM-DD)", default=date.today().strftime("%Y-%m-%d"))
    parser_logs.set_defaults(func=activity)
    parser_jobid = subparsers.add_parser(
        "jobid", help="Show JCS instance activity logs for given job id")
    parser_jobid.add_argument("jobid", help="JCS instance job id")
    parser_jobid.set_defaults(func=jobid)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    result, response = main()
    logger.info(result)
    logger.info(response.status_code)
    logger.info(response.text)
