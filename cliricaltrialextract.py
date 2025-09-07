
# ClinicalTrials.gov Visualization Notebook
# Works with any NCT ID

from urllib import response
import requests
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# ----------------------------
# 1. Fetch trial data
# ----------------------------
def get_trial_data(nct_id):
   url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
   
   response = requests.get(url)
   #print(response.json())
   data = response.json()
   #print(data)
   #study = data["protocolSection"]['identificationModule']['briefTitle']
   #print(study)
   title = data["protocolSection"]["identificationModule"]["briefTitle"]
   conditions = data["protocolSection"]["conditionsModule"]["conditions"]
   interventions = []
   if "armsInterventionsModule" in data["protocolSection"]:
       interventions = [
           i["interventionName"] 
           for i in data["protocolSection"]["armsInterventionsModule"]["interventionList"]["intervention"]
       ]

   print(title)
   print(conditions)
   print(interventions)

   return data

# ----------------------------
# 2. Extract details
# ----------------------------
def extract_info(study):
    title = study["ProtocolSection"]["identificationModule"]["briefTitle"]
    conditions = study["ProtocolSection"]["ConditionsModule"]["ConditionList"]["Condition"]

    interventions = []
    if "ArmsInterventionsModule" in study["ProtocolSection"]:
        interventions = [i["InterventionName"] for i in study["ProtocolSection"]["ArmsInterventionsModule"]["InterventionList"]["Intervention"]]

    enrollment = study["ProtocolSection"]["DesignModule"].get("EnrollmentInfo", {}).get("EnrollmentCount", "NA")

    start_date = study["ProtocolSection"]["StatusModule"].get("StartDateStruct", {}).get("StartDate", "NA")
    completion_date = study["ProtocolSection"]["StatusModule"].get("CompletionDateStruct", {}).get("CompletionDate", "NA")

    locations = []
    if "ContactsLocationsModule" in study["ProtocolSection"]:
        locs = study["ProtocolSection"]["ContactsLocationsModule"].get("LocationList", {}).get("Location", [])
        for l in locs:
            if "LocationCountry" in l:
                locations.append(l["LocationCountry"])

    return {
        "title": title,
        "conditions": conditions,
        "interventions": interventions,
        "enrollment": enrollment,
        "start_date": start_date,
        "completion_date": completion_date,
        "locations": locations
    }
def plot_condition_intervention_graph(conditions, interventions, nct_id):
    G = nx.Graph()
    for c in conditions:
        for i in interventions:
            G.add_edge(c, i)

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=2500, 
            font_size=10, edge_color="gray")
    plt.title(f"Condition-Intervention Graph for {nct_id}", fontsize=14)
    plt.show()
def plot_locations(locations, nct_id):
    if not locations:
        print("No location data available")
        return
    
    loc_df = pd.Series(locations).value_counts()

    plt.figure(figsize=(8, 4))
    loc_df.plot(kind="bar")
    plt.title(f"Location Distribution for {nct_id}", fontsize=14)
    plt.ylabel("Number of Sites")
    plt.xlabel("Country")
    plt.show()
def plot_timeline(start_date, completion_date, enrollment, nct_id):
    plt.figure(figsize=(8, 2))
    plt.plot([start_date, completion_date], [int(enrollment), int(enrollment)], marker="o")
    plt.title(f"Timeline for {nct_id}\nEnrollment: {enrollment}", fontsize=14)
    plt.xlabel("Dates")
    plt.yticks([])
    plt.show()


data = get_trial_data("NCT04320615")
#info = extract_info(data)

#print("Title:", info["title"])
#print("Conditions:", info["conditions"])
#print("Interventions:", info["interventions"])
#print("Enrollment:", info["enrollment"])
#print("Start Date:", info["start_date"], "Completion Date:", info["completion_date"])
#print("Countries:", set(info["locations"]))

#plot_condition_intervention_graph(info["conditions"], info["interventions"], "NCT04320615")
#plot_timeline(info["start_date"], info["completion_date"], info["enrollment"], "NCT04320615")
#plot_locations(info["locations"], "NCT04320615")

