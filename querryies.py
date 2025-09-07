Get all studies
MATCH (s:Study)
RETURN s.id AS NCTId, s.title AS Title, s.org AS Organization
LIMIT 20;

Get a study with all linked nodes
MATCH (s:Study {id: "NCT02613390"})
OPTIONAL MATCH (s)-[:INVESTIGATES]->(c:Condition)
OPTIONAL MATCH (s)-[:USES]->(i:Intervention)
OPTIONAL MATCH (s)-[:SPONSORED_BY]->(sp:Sponsor)
OPTIONAL MATCH (s)-[:HAS_STATUS]->(st:Status)
OPTIONAL MATCH (s)-[:HAS_PHASE]->(p:Phase)
OPTIONAL MATCH (s)-[:INVESTIGATES_MESH]->(cm:ConditionMesh)
OPTIONAL MATCH (s)-[:USES_MESH]->(im:InterventionMesh)
OPTIONAL MATCH (s)-[:HAS_TYPE]->(stype:StudyType)
OPTIONAL MATCH (s)-[:HAS_PHASE_DERIVED]->(dp:Phase)
RETURN s.id AS NCTId, s.title AS Title, s.org AS Org,
       collect(DISTINCT c.name) AS Conditions,
       collect(DISTINCT i.name) AS Interventions,
       collect(DISTINCT sp.name) AS Sponsors,
       collect(DISTINCT st.name) AS Statuses,
       collect(DISTINCT p.name) AS Phases,
       collect(DISTINCT cm.term) AS ConditionMeshes,
       collect(DISTINCT im.term) AS InterventionMeshes,
       collect(DISTINCT stype.name) AS StudyTypes,
       collect(DISTINCT dp.name) AS DerivedPhases;


MATCH (s:Study)-[:USES]->(i:Intervention)
WHERE toLower(i.name) = "drug a"
RETURN s.id AS NCTId, s.title AS Title, collect(i.name) AS Interventions;


MATCH (s:Study)-[r:USES]->(i:Intervention)
RETURN s.id, i.name LIMIT 20;



MATCH (s:Study)-[:USES]->(i:Intervention)
WHERE toLower(i.name) = tolower("Opdivo")
RETURN s.id AS NCTId, s.title AS Title, collect(i.name) AS Interventions;



MATCH (s:Study {id:"NCT01078974"})
OPTIONAL MATCH (s)-[r]->(n)
RETURN s, r, n;



