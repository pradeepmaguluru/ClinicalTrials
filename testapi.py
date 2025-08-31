import requests

nct_id = "NCT04320615"
url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"

resp = requests.get(url)
if resp.status_code != 200:
    raise Exception(f"API request failed with status code {resp.status_code}")

data = resp.json()
print(data)
