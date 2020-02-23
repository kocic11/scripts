import json
import requests
import sys

result = json.loads(
  """
  {
    "details": {
      "message": ""
    }
  }
  """
)

def scale(config):
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

  
  user = config.get("user")
  password = config.get("password")
  id_tenant_name = config.get("id-tenant-name")
  hosts = config.get("hosts")
  shape = config.get("shape")
  jcsinstance = config.get("jcsinstance")
  
  auth = (user, password)
  headers = {
    "content-type": "application/json",
    "X-ID-TENANT-NAME": id_tenant_name
  }

  try:
    # Scale up/down
    uri = "https://jaas.oraclecloud.com/paas/api/v1.1/instancemgmt/" + id_tenant_name + "/services/jaas/instances/" + jcsinstance + "/hosts/scale"
    
    
    data["components"]["WLS"]["hosts"] = hosts.split(",")
    data["components"]["WLS"]["shape"] = shape
    
    result = requests.post(uri, auth=auth, headers=headers, data=json.dumps(data)).json()
  except:
    result["details"]["message"] = "Unexpected error: " + str(sys.exc_info()[0])
    pass
  return result

def startstop(config):
  """Return the result of the JCS instance start/stop operation."""
  global result
  data = json.loads(
    """
    {
    "allServiceHosts" : true
    } 
    """
  )

  user = config.get("user")
  password = config.get("password")
  id_tenant_name = config.get("id-tenant-name")
  command = config.get("command")
  jcsinstance = config.get("jcsinstance")
  
  auth = (user, password)
  headers = {
    "content-type": "application/json",
    "X-ID-TENANT-NAME": id_tenant_name
  }

  try:
    # Scale up/down
    uri = "https://jaas.oraclecloud.com/paas/api/v1.1/instancemgmt/" + id_tenant_name + "/services/jaas/instances/" + jcsinstance + "/hosts/" + command
    result = requests.post(uri, auth=auth, headers=headers, data=json.dumps(data)).json()
  except:
    result["details"]["message"] = "Unexpected error: " + str(sys.exc_info()[0])
    pass
  return result
