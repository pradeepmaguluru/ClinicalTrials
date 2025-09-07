import requests, csv

BASE = "https://clinicaltrials.gov/api/v2/studies/"
params = {
    "query.cond": "cancer",
    "pageSize": 500,
    "fields": "NCTId,protocolSection.identificationModule,conditionsModule.conditions,armsInterventionsModule.interventions,designModule.phases,statusModule.overallStatus,sponsorsModule"
}

studies = []
conditions_edges = []
interventions_edges = []
sponsors_edges = []
collaborators_edges = []
phases_edges = []
status_edges = []

while True:
    resp = requests.get(BASE, params=params)
    data = resp.json()
    
    for s in data.get("studies", []):
        nct = s["protocolSection"]["identificationModule"].get("nctId")
        title = s["protocolSection"]["identificationModule"].get("officialTitle","")

        # Study node
        studies.append((nct, title))

        # Conditions
        conds = s.get("conditionsModule", {}).get("conditions", [])
        for c in conds:
            conditions_edges.append((nct, c))

        # Interventions
        ints = s.get("armsInterventionsModule", {}).get("interventions", [])
        for i in ints:
            interventions_edges.append((nct, i.get("name", "")))

        # Sponsor
        sponsor = s.get("sponsorsModule", {}).get("leadSponsor", {}).get("name")
        if sponsor:
            sponsors_edges.append((nct, sponsor))

        # Collaborators
        collabs = s.get("sponsorsModule", {}).get("collaborators", [])
        for col in collabs:
            collaborators_edges.append((nct, col.get("name", "")))

        # Phase
        phases = s.get("designModule", {}).get("phases", [])
        for ph in phases:
            phases_edges.append((nct, ph))

        # Status
        status = s.get("statusModule", {}).get("overallStatus")
        if status:
            status_edges.append((nct, status))

    # Pagination
    token = data.get("nextPageToken")
    if token:
        params["pageToken"] = token
    else:
        break

# Write CSVs
def write_csv(filename, header, rows):
    with open(filename,"w",newline="") as f:
        writer = csv.writer(f); writer.writerow(header); writer.writerows(rows)

write_csv("studies.csv", ["id","title"], studies)
write_csv("study_conditions.csv", ["study","condition"], conditions_edges)
write_csv("study_interventions.csv", ["study","intervention"], interventions_edges)
write_csv("study_sponsors.csv", ["study","sponsor"], sponsors_edges)
write_csv("study_collaborators.csv", ["study","collaborator"], collaborators_edges)
write_csv("study_phases.csv", ["study","phase"], phases_edges)
write_csv("study_status.csv", ["study","status"], status_edges)

print("Export complete with derivations: conditions, interventions, sponsors, collaborators, phases, status")
