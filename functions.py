import argparse
import json
import os
import sys
from datetime import date
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    user = config.get("user")
    password = config.get("password")
    id_tenant_name = config.get("id-tenant-name")
    jaas_uri = config.get("jaas_uri")
    email_server = config.get("email_server")
    email_server_port = config.get("email_server_port")
    email_server_port_ssl = config.get("email_server_port_ssl")
    email_user = config.get("email_user")
    email_user_password = config.get("email_user_password")
    email_from = config.get("email_from")
    email_to = config.get("email_to")
    email_subject = config.get("email_subject")
    email = {"email_server": email_server, "email_server_port": email_server_port, "email_server_port_ssl": email_server_port_ssl,
             "email_user": email_user, "email_user_password": email_user_password, "email_from": email_from, "email_to": email_to,
             "email_subject": email_subject}
    auth = (user, password)
    headers = {
        "content-type": "application/json",
        "X-ID-TENANT-NAME": id_tenant_name
    }
    return user, password, id_tenant_name, jaas_uri, auth, headers, email


def __send_email(email, message):
    try:
        if email["email_server_port_ssl"] == "true":
            smtp_server = smtplib.SMTP_SSL(
                host=email["email_server"], port=email["email_server_port"])
            print("Using SSL port")
        else:
            smtp_server = smtplib.SMTP(
                host=email["email_server"], port=email["email_server_port"])
            print("Using non SSL port")
        smtp_server.login(email["email_user"], email["email_user_password"])
        print("Logged to email server")
        msg = MIMEMultipart()
        msg["From"] = email["email_from"]
        msg["To"] = email["email_to"]
        msg["Subject"] = email["email_subject"]
        msg.attach(
            MIMEText(str(json.dumps(message, indent=2, sort_keys=True)), "plain"))
        smtp_server.send_message(msg)
        print("Sent email")
    except:
        print(sys.exc_info()[0])
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

    user, password, id_tenant_name, jaas_uri, auth, headers, email = __getEnv(
        args.env)

    try:
        uri = jaas_uri + "/instancemgmt/" + id_tenant_name + \
            "/services/jaas/instances/" + args.instance + "/hosts/" + command
        response = requests.post(
            uri, auth=auth, headers=headers, data=json.dumps(data))
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

    __send_email(email, result)
    return result


def scale(args):
    """Return the result of the JCS instance scale up/down operation."""
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

    user, password, id_tenant_name, jaas_uri, auth, headers, email = __getEnv(
        args.env)

    try:
        uri = jaas_uri + "/instancemgmt/" + id_tenant_name + \
            "/services/jaas/instances/" + args.instance + "/hosts/scale"
        data["components"]["WLS"]["hosts"] = args.hosts.split(",")
        data["components"]["WLS"]["shape"] = args.shape
        response = requests.post(
            uri, auth=auth, headers=headers, data=json.dumps(data))
        if response.status_code == requests.codes.ACCEPTED:
            result = response.json()
        else:
            result["details"]["message"] = "Unexpected error: " + \
                str(response.status_code) + ", " + \
                response.text
    except:
        result["details"]["message"] = "Unexpected error: " + \
            str(sys.exc_info()[0])
        pass

    __send_email(email, result)
    return result


def start(args):
    """Return the result of the JCS instance start operation."""
    return __startstop(args, "start")


def stop(args):
    """Return the result of the JCS instance stop operation."""
    return __startstop(args, "stop")


def activity(args):
    """Return the the JCS instance operations activity logs."""
    global result
    user, password, id_tenant_name, jaas_uri, auth, headers, email = __getEnv(
        args.env)

    try:
        uri = jaas_uri + "/activitylog/" + id_tenant_name + "/filter?serviceName=" + \
            args.instance + "&fromStartDate=" + args.fromStartDate
        response = requests.get(uri, auth=auth, headers=headers)
        if response.status_code == requests.codes.OK:
            result = response.json()
        else:
            result["details"]["message"] = "Unexpected error: " + \
                str(response.status_code)
    except:
        result["details"]["message"] = "Unexpected error: " + \
            str(sys.exc_info()[0])
        pass

    return result


def print_usage(args):
    global parser
    parser.print_help()
    exit()


def main():
    global parser
    parser.add_argument("env", help="JSON file with environment variables")
    parser.add_argument("instance", help="JCS instance name")
    parser.set_defaults(func=print_usage)
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_scale = subparsers.add_parser("scale", help="Scale JCS instance")
    parser_scale.add_argument(
        "scale", help="Scale JCS instance", action='store_true')
    parser_scale.add_argument(
        "hosts", help="comma separated list of JCS instance hosts")
    parser_scale.add_argument("shape", help="JCS instance shape")
    parser_scale.add_argument(
        "--email", help="JCS instance shape", action="store_true")
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
    args = parser.parse_args()
    return args.func(args)


parser = argparse.ArgumentParser()
print(main())
