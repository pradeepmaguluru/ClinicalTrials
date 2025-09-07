from py2neo import Graph, Node, Relationship
import requests

# 🔹 Connect to Neo4j (update credentials)
graph = Graph(
    "neo4j+s://e25ee5b5.databases.neo4j.io",
    auth=("neo4j", "YdnHjlT2Os79cAUI3sFkJQrZplKdUzNnK1jo027YaFY")
)

# 🔹 ClinicalTrials.gov API
BASE = "https://clinicaltrials.gov/api/v2/studies"
params = {
    "query.cond": "cancer",
    "pageSize": 10,
    "fields": "NCTId,protocolSection,derivedSection"
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
        break

    studies = data.get("studies", [])
    if not studies:
        print("✅ No more studies found.")
        break

    for s in studies:
        protocol = s.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})

        nct = ident.get("nctId")
        title = ident.get("officialTitle", ident.get("briefTitle", ""))
        org = ident.get("organization", {}).get("fullName")

        # 🔹 Create Study node
        study_node = Node("Study", id=nct, title=title, org=org)
        graph.merge(study_node, "Study", "id")

        # 🔹 Conditions
        conds = protocol.get("conditionsModule", {}).get("conditions", [])
        for c in conds:
            cond_node = Node("Condition", name=c)
            graph.merge(cond_node, "Condition", "name")
            graph.merge(Relationship(study_node, "INVESTIGATES", cond_node))

        # 🔹 Interventions
        ints = protocol.get("armsInterventionsModule", {}).get("interventions", [])
        for i in ints:
            name = i.get("name", "")
            if name:
                int_node = Node("Intervention", name=name)
                graph.merge(int_node, "Intervention", "name")
                graph.merge(Relationship(study_node, "USES", int_node))

        # 🔹 Sponsor
        sponsor = protocol.get("sponsorsModule", {}).get("leadSponsor", {}).get("name")
        if sponsor:
            sponsor_node = Node("Sponsor", name=sponsor)
            graph.merge(sponsor_node, "Sponsor", "name")
            graph.merge(Relationship(study_node, "SPONSORED_BY", sponsor_node))

        # 🔹 Status
        status = protocol.get("statusModule", {}).get("overallStatus")
        if status:
            status_node = Node("Status", name=status)
            graph.merge(status_node, "Status", "name")
            graph.merge(Relationship(study_node, "HAS_STATUS", status_node))

        # 🔹 Phases
        phases = protocol.get("designModule", {}).get("phases", [])
        for ph in phases:
            phase_node = Node("Phase", name=ph)
            graph.merge(phase_node, "Phase", "name")
            graph.merge(Relationship(study_node, "HAS_PHASE", phase_node))

        # ==============================
        # 🔹 Derived Section Data
        # ==============================
        derived = s.get("derivedSection", {})

        # Derived MeSH Conditions
        cond_meshes = derived.get("conditionBrowseModule", {}).get("meshes", [])
        for cm in cond_meshes:
            mesh_node = Node("ConditionMesh", id=cm.get("id"), term=cm.get("term"))
            graph.merge(mesh_node, "ConditionMesh", "id")
            graph.merge(Relationship(study_node, "INVESTIGATES_MESH", mesh_node))

        # Derived MeSH Interventions
        int_meshes = derived.get("interventionBrowseModule", {}).get("meshes", [])
        for im in int_meshes:
            mesh_node = Node("InterventionMesh", id=im.get("id"), term=im.get("term"))
            graph.merge(mesh_node, "InterventionMesh", "id")
            graph.merge(Relationship(study_node, "USES_MESH", mesh_node))

        # Derived Phases
        dphases = derived.get("phaseList", [])
        for ph in dphases:
            phase_node = Node("Phase", name=ph)
            graph.merge(phase_node, "Phase", "name")
            graph.merge(Relationship(study_node, "HAS_PHASE_DERIVED", phase_node))

        print(f"✅ Loaded study {nct}")

    # 🔹 Pagination
    token = data.get("nextPageToken")
    if token:
        params["pageToken"] = token
    else:
        break

print("🎯 All studies loaded into Neo4j!")
