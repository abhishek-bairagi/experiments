# Let's define the Python script for ingesting sample graph data into Neo4j with vector embeddings.
# This script assumes you have Neo4j Python driver installed and a running Neo4j instance.

from neo4j import GraphDatabase

# Sample data for Slack product structure
data = {
    "products": [
        {"product_id": "p1", "name": "Slack", "aliases": ["slack", "slackapp"]}
    ],
    "subtopics": [
        {"subtopic_id": "s1", "name": "Channels", "aliases": ["channel", "ch"], "has_further_subtopic": False, "parent_topic_id": None},
        {"subtopic_id": "s2", "name": "Notifications", "aliases": ["alerts", "notifs"], "has_further_subtopic": False, "parent_topic_id": None}
    ],
    "issues": [
        {"issue_id": "i1", "description": "Unable to join Slack channels", "keywords": ["join", "channel", "access"], "embedding": [0.1]*384, "frequency": "high", "severity": "medium"},
        {"issue_id": "i2", "description": "Channels not loading", "keywords": ["load", "channel", "error"], "embedding": [0.2]*384, "frequency": "medium", "severity": "high"},
        {"issue_id": "i3", "description": "Slack notifications delayed", "keywords": ["notifications", "delay", "late"], "embedding": [0.3]*384, "frequency": "high", "severity": "medium"},
        {"issue_id": "i4", "description": "Notifications not appearing on desktop", "keywords": ["notifications", "desktop", "missing"], "embedding": [0.4]*384, "frequency": "low", "severity": "low"}
    ],
    "causes": [
        {"cause_id": "c1", "description": "User lacks permission", "conditions": "user not part of workspace"},
        {"cause_id": "c2", "description": "Slack cache issue", "conditions": "cache corrupted"},
        {"cause_id": "c3", "description": "Do Not Disturb mode enabled", "conditions": "DND enabled on Slack"},
        {"cause_id": "c4", "description": "System notifications disabled", "conditions": "desktop notifications off"}
    ],
    "solutions": [
        {"solution_id": "sol1", "description": "Request access from admin", "related_article_ids": ["a1"]},
        {"solution_id": "sol2", "description": "Clear Slack cache", "related_article_ids": ["a2"]},
        {"solution_id": "sol3", "description": "Disable Do Not Disturb", "related_article_ids": ["a3"]},
        {"solution_id": "sol4", "description": "Enable desktop notifications", "related_article_ids": ["a3"]}
    ],
    "articles": [
        {"article_id": "a1", "title": "Getting Slack Channel Access", "summary": "Guide to requesting access to channels", "url": "https://kb.example.com/slack-access", "tags": ["access", "admin"], "embedding": [0.01]*384},
        {"article_id": "a2", "title": "Fix Slack Cache Issues", "summary": "Steps to clear Slack cache", "url": "https://kb.example.com/slack-cache", "tags": ["cache", "clear"], "embedding": [0.02]*384},
        {"article_id": "a3", "title": "Manage Notification Settings", "summary": "Manage DND and notification preferences", "url": "https://kb.example.com/slack-notifs", "tags": ["dnd", "notifications"], "embedding": [0.03]*384}
    ],
    "user": {"user_id": "u1", "location": "NY", "device_type": "laptop", "issue_history": ["i1", "i3"]},
    "devices": [
        {"device_id": "d1", "type": "Mac", "os_version": "12.6"},
        {"device_id": "d2", "type": "Windows", "os_version": "11"}
    ],
    "outage": {"incident_id": "o1", "description": "Slack outage in US East", "timestamp": "2024-05-12T10:00:00Z", "affected_users": ["u1"]}
}

data.keys()  # Display keys for structure confirmation before writing ingestion logic.



from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "your_password"

driver = GraphDatabase.driver(uri, auth=(user, password))

data = {  # (Your JSON structure from earlier - already defined above)
    # truncated for brevity...
}

def create_vector_indexes(tx):
    tx.run("""
        CREATE VECTOR INDEX `issue-embeddings`
        FOR (i:Issue) ON (i.embedding)
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: 384,
            `vector.similarity_function`: 'cosine'
          }
        }
    """)
    tx.run("""
        CREATE VECTOR INDEX `article-embeddings`
        FOR (a:Article) ON (a.embedding)
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: 384,
            `vector.similarity_function`: 'cosine'
          }
        }
    """)

def ingest_data(tx, data):
    # Products
    for p in data["products"]:
        tx.run("MERGE (n:Product {product_id: $id}) SET n.name=$name, n.aliases=$aliases",
               id=p["product_id"], name=p["name"], aliases=p["aliases"])

    # Subtopics
    for s in data["subtopics"]:
        tx.run("""
            MERGE (n:Subtopic {subtopic_id: $id})
            SET n.name=$name, n.aliases=$aliases, n.has_further_subtopic=$has_more, n.parent_topic_id=$parent, n.is_generic=false
        """, id=s["subtopic_id"], name=s["name"], aliases=s["aliases"],
           has_more=s["has_further_subtopic"], parent=s["parent_topic_id"])

    # Issues
    for i in data["issues"]:
        tx.run("""
            MERGE (n:Issue {issue_id: $id})
            SET n.description=$desc, n.keywords=$kw, n.embedding=$embed, n.frequency=$freq, n.severity=$severity
        """, id=i["issue_id"], desc=i["description"], kw=i["keywords"], embed=i["embedding"],
               freq=i["frequency"], severity=i["severity"])

    # Causes
    for c in data["causes"]:
        tx.run("MERGE (n:Cause {cause_id: $id}) SET n.description=$desc, n.conditions=$cond",
               id=c["cause_id"], desc=c["description"], cond=c["conditions"])

    # Solutions
    for s in data["solutions"]:
        tx.run("MERGE (n:Solution {solution_id: $id}) SET n.description=$desc, n.related_article_ids=$articles",
               id=s["solution_id"], desc=s["description"], articles=s["related_article_ids"])

    # Articles
    for a in data["articles"]:
        tx.run("""
            MERGE (n:Article {article_id: $id})
            SET n.title=$title, n.summary=$summary, n.url=$url, n.tags=$tags, n.embedding=$embed
        """, id=a["article_id"], title=a["title"], summary=a["summary"],
               url=a["url"], tags=a["tags"], embed=a["embedding"])

    # User
    u = data["user"]
    tx.run("MERGE (u:User {user_id: $id}) SET u.location=$loc, u.device_type=$dt, u.issue_history=$hist",
           id=u["user_id"], loc=u["location"], dt=u["device_type"], hist=u["issue_history"])

    # Devices
    for d in data["devices"]:
        tx.run("MERGE (d:Device {device_id: $id}) SET d.type=$type, d.os_version=$os",
               id=d["device_id"], type=d["type"], os=d["os_version"])

    # Outage
    o = data["outage"]
    tx.run("MERGE (o:Outage {incident_id: $id}) SET o.description=$desc, o.timestamp=$ts, o.affected_users=$users",
           id=o["incident_id"], desc=o["description"], ts=o["timestamp"], users=o["affected_users"])

def create_relationships(tx):
    tx.run("""
        MATCH (p:Product {product_id: 'p1'}), (s1:Subtopic {subtopic_id: 's1'}), (s2:Subtopic {subtopic_id: 's2'})
        MERGE (p)-[:associated_with]->(s1)
        MERGE (p)-[:associated_with]->(s2)
    """)
    tx.run("""
        MATCH (s1:Subtopic {subtopic_id: 's1'}), (i1:Issue {issue_id: 'i1'}), (i2:Issue {issue_id: 'i2'})
        MERGE (s1)-[:has_issue]->(i1)
        MERGE (s1)-[:has_issue]->(i2)
    """)
    tx.run("""
        MATCH (s2:Subtopic {subtopic_id: 's2'}), (i3:Issue {issue_id: 'i3'}), (i4:Issue {issue_id: 'i4'})
        MERGE (s2)-[:has_issue]->(i3)
        MERGE (s2)-[:has_issue]->(i4)
    """)
    tx.run("""
        MATCH (i1:Issue {issue_id: 'i1'}), (c1:Cause {cause_id: 'c1'}), (sol1:Solution {solution_id: 'sol1'}), (a1:Article {article_id: 'a1'})
        MERGE (i1)-[:has_cause]->(c1)
        MERGE (c1)-[:has_solution]->(sol1)
        MERGE (sol1)-[:backed_by]->(a1)
    """)
    tx.run("""
        MATCH (i2:Issue {issue_id: 'i2'}), (c2:Cause {cause_id: 'c2'}), (sol2:Solution {solution_id: 'sol2'}), (a2:Article {article_id: 'a2'})
        MERGE (i2)-[:has_cause]->(c2)
        MERGE (c2)-[:has_solution]->(sol2)
        MERGE (sol2)-[:backed_by]->(a2)
    """)
    tx.run("""
        MATCH (i3:Issue {issue_id: 'i3'}), (c3:Cause {cause_id: 'c3'}), (sol3:Solution {solution_id: 'sol3'}), (a3:Article {article_id: 'a3'})
        MERGE (i3)-[:has_cause]->(c3)
        MERGE (c3)-[:has_solution]->(sol3)
        MERGE (sol3)-[:backed_by]->(a3)
    """)
    tx.run("""
        MATCH (i4:Issue {issue_id: 'i4'}), (c4:Cause {cause_id: 'c4'}), (sol4:Solution {solution_id: 'sol4'}), (a3:Article {article_id: 'a3'})
        MERGE (i4)-[:has_cause]->(c4)
        MERGE (c4)-[:has_solution]->(sol4)
        MERGE (sol4)-[:backed_by]->(a3)
    """)
    tx.run("""
        MATCH (u:User {user_id: 'u1'}), (d1:Device {device_id: 'd1'}), (d2:Device {device_id: 'd2'})
        MERGE (u)-[:has_device]->(d1)
        MERGE (u)-[:has_device]->(d2)
    """)
    tx.run("""
        MATCH (u:User {user_id: 'u1'}), (i1:Issue {issue_id: 'i1'}), (i3:Issue {issue_id: 'i3'})
        MERGE (u)-[:reported]->(i1)
        MERGE (u)-[:reported]->(i3)
    """)
    tx.run("""
        MATCH (o:Outage {incident_id: 'o1'}), (p:Product {product_id: 'p1'})
        MERGE (o)-[:related_to]->(p)
    """)

with driver.session() as session:
    session.write_transaction(create_vector_indexes)
    session.write_transaction(ingest_data, data)
    session.write_transaction(create_relationships)

driver.close()
