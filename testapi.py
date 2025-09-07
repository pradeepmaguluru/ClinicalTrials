import requests

BASE = "https://clinicaltrials.gov/api/v2/studies"
params = {
    "query.cond": "cancer",
    "pageSize": 1,
    "fields": "NCTId,protocolSection.identificationModule"
}

r = requests.get(BASE, params=params)
print(r.status_code)
print(r.json())
