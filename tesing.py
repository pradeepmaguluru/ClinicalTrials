import requests

BASE = "https://clinicaltrials.gov/api/v2/studies"
params = {
    "query.cond": "cancer",
    "pageSize": 5,
    "fields": "NCTId,protocolSection.identificationModule"
}

while True:
    resp = requests.get(BASE, params=params)
    
    if resp.status_code != 200:
        print(f"⚠️ API error {resp.status_code}: {resp.text[:200]}")
        break
    
    try:
        data = resp.json()
    except Exception as e:
        print("⚠️ JSON parse error:", e)
        print("Raw response:", resp.text[:200])
        break
    
    studies = data.get("studies", [])
    if not studies:
        print("✅ No more studies found.")
        break
    
    for s in studies:
        ident = s["protocolSection"]["identificationModule"]
        nct = ident.get("nctId")
        title = ident.get("officialTitle", ident.get("briefTitle"))
        org = ident.get("organization", {}).get("fullName")
        print(f"NCT: {nct} | Title: {title} | Org: {org}")
    
    # Pagination
    token = data.get("nextPageToken")
    if token:
        params["pageToken"] = token
    else:
        break
