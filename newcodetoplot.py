import requests
import pandas as pd

def fetch_study(nct_id: str):
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def flatten_study(study):
    proto = study.get("protocolSection", {})
    tables = {}

    # 1. Identification
    id_mod = proto.get("identificationModule", {})
    tables["identification"] = pd.DataFrame([{
        "nctId": id_mod.get("nctId"),
        "orgStudyId": id_mod.get("orgStudyId"),
        "officialTitle": id_mod.get("officialTitle"),
        "briefTitle": id_mod.get("briefTitle")
    }])

    # 2. Status
    status_mod = proto.get("statusModule", {})
    tables["status"] = pd.DataFrame([{
        "overallStatus": status_mod.get("overallStatus"),
        "startDate": status_mod.get("startDateStruct", {}).get("date"),
        "completionDate": status_mod.get("completionDateStruct", {}).get("date"),
        "primaryCompletionDate": status_mod.get("primaryCompletionDateStruct", {}).get("date")
    }])

    # 3. Sponsors
    sponsor_mod = proto.get("sponsorCollaboratorsModule", {})
    lead = sponsor_mod.get("leadSponsor", {})
    collaborators = sponsor_mod.get("collaborators", [])
    rows = [{"role": "lead", "name": lead.get("name")}]
    rows += [{"role": "collaborator", "name": c.get("name")} for c in collaborators]
    tables["sponsors"] = pd.DataFrame(rows)

    # 4. Conditions
    cond_mod = proto.get("conditionsModule", {})
    tables["conditions"] = pd.DataFrame(cond_mod.get("conditions", []), columns=["condition"])

    # 5. Arms + Interventions
    arms_mod = proto.get("armsInterventionsModule", {})
    arms = arms_mod.get("armGroupList", {}).get("armGroup", [])
    interventions = arms_mod.get("interventionList", {}).get("intervention", [])
    tables["arms"] = pd.DataFrame(arms) if arms else pd.DataFrame()
    tables["interventions"] = pd.DataFrame(interventions) if interventions else pd.DataFrame()

    # 6. Outcomes
    outcomes_mod = proto.get("outcomesModule", {})
    primary = outcomes_mod.get("primaryOutcomes", [])
    secondary = outcomes_mod.get("secondaryOutcomes", [])
    tables["primary_outcomes"] = pd.DataFrame(primary) if primary else pd.DataFrame()
    tables["secondary_outcomes"] = pd.DataFrame(secondary) if secondary else pd.DataFrame()

    # 7. Eligibility
    elig_mod = proto.get("eligibilityModule", {})
    tables["eligibility"] = pd.DataFrame([elig_mod]) if elig_mod else pd.DataFrame()

    return tables


# 🔹 Example run
nct_id = "NCT00292552"  # replace with your NCT ID
study = fetch_study(nct_id)
tables = flatten_study(study)

# Show each table
for name, df in tables.items():
    print(f"\n=== {name.upper()} ===")
    print(df.head())
