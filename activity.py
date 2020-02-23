import json
import requests
import sys
from datetime import date

def activity(config):
  result = json.loads(
    """
    {
        "details": {
        "message": ""
      }
    }
    """
  )

  user = config.get("user")
  password = config.get("password")
  id_tenant_name = config.get("id-tenant-name")
  command = config.get("command")
  jcsinstance = config.get("jcsinstance")
  fromStartDate = config.get("fromStartDate")
  auth = (user, password)
  headers = {
    "content-type": "application/json",
    "X-ID-TENANT-NAME": id_tenant_name
  }

  try:
    # Get job status
    if fromStartDate == None:
      fromStartDate = date.today().strftime("%Y-%m-%d")
    uri = "https://jaas.oraclecloud.com//paas/api/v1.1/activitylog/" + id_tenant_name + "/filter?serviceName=" + jcsinstance + "&fromStartDate=" + fromStartDate
    result = requests.get(uri, auth=auth, headers=headers).json()
  except:
    result["details"]["message"] = "Unexpected error: " + str(sys.exc_info()[0])
    pass
  return result

lenArgs = len(sys.argv)
if (lenArgs < 2) :
    print("Usage: python", sys.argv[0], "env.json")
    exit()

with open(sys.argv[1]) as f:
  config = json.load(f)

print(activity(config))