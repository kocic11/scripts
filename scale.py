import json
import requests
import sys

def scale(config):
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

lenArgs = len(sys.argv)
if (lenArgs < 2) :
    print("Usage: python", sys.argv[0], "env.json")
    exit()

with open(sys.argv[1]) as f:
  config = json.load(f)

print(scale(config))