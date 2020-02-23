import json
import requests
import sys
from datetime import date

result = json.loads(
  """
  {
    "details": {
      "message": ""
    }
  }
  """
)

def __getEnv(config):
  user = config.get("user")
  password = config.get("password")
  id_tenant_name = config.get("id-tenant-name")
  jaas_uri = config.get("jaas_uri")
  auth = (user, password)
  headers = {
    "content-type": "application/json",
    "X-ID-TENANT-NAME": id_tenant_name
  }
  return user, password, id_tenant_name, jaas_uri, auth, headers

def scale(config, jcsinstance, hosts, shape):
  """Return the result of the JCS instance scale up/down operation."""
  global result
  data = json.loads(
    """
    {
      "components": {
          "WLS": {
            "hosts": [],
            "shape": "",
            "ignoreManagedServerHeapError": true
          }
      }
    }
    """
  )
  
  user, password, id_tenant_name, jaas_uri, auth, headers = __getEnv(config)
  
  try:
    uri = jaas_uri + "/instancemgmt/" + id_tenant_name + "/services/jaas/instances/" + jcsinstance + "/hosts/scale"
    data["components"]["WLS"]["hosts"] = hosts.split(",")
    data["components"]["WLS"]["shape"] = shape
    
    result = requests.post(uri, auth=auth, headers=headers, data=json.dumps(data)).json()
  except:
    result["details"]["message"] = "Unexpected error: " + str(sys.exc_info()[0])
    pass
  return result

def startstop(config, jcsinstance, command):
  """Return the result of the JCS instance start/stop operation."""
  global result
  data = json.loads(
    """
    {
    "allServiceHosts" : true
    } 
    """
  )

  user, password, id_tenant_name, jaas_uri, auth, headers = __getEnv(config) 

  try:
    uri = jaas_uri + "/instancemgmt/" + id_tenant_name + "/services/jaas/instances/" + jcsinstance + "/hosts/" + command
    result = requests.post(uri, auth=auth, headers=headers, data=json.dumps(data)).json()
  except:
    result["details"]["message"] = "Unexpected error: " + str(sys.exc_info()[0])
    pass
  return result

def activity(config, jcsinstance, fromStartDate = None):
  """Return the the JCS instance operations activity logs."""
  global result
  user, password, id_tenant_name, jaas_uri, auth, headers = __getEnv(config)

  try:
    if fromStartDate == None or fromStartDate == '':
      fromStartDate = date.today().strftime("%Y-%m-%d")
    uri = jaas_uri + "/activitylog/" + id_tenant_name + "/filter?serviceName=" + jcsinstance + "&fromStartDate=" + fromStartDate
    result = requests.get(uri, auth=auth, headers=headers).json()
  except:
    result["details"]["message"] = "Unexpected error: " + str(sys.exc_info()[0])
    pass
  return result
