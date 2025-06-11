from src.constants import kg_password, kg_uri, kg_user
from neo4j import GraphDatabase
from src.helpers.embedding_helper import embed

def universal_formatting_function(input:dict, heading = ""):
    out = f"{heading}:\n" if heading else "" 
    for k, v in input.items():
        # print(v, type(v))
        if isinstance(v, list):
            if all(isinstance(item, dict) for item in v):
                out += f"{k}:\n" + "\n".join([f"  - {', '.join(f'{sub_k}: {sub_v}' for sub_k, sub_v in item.items())}" for item in v]) + "\n"
            else:
                out += f"{k}: {', '.join(v)}\n"
        else:
            out += f"{k}: {v}\n"
    return out 

def get_relevant_issues_with_articles(product_name, subtopic_name, query_text, threshold=0.5, top_k=5):
    """
    Fetch top semantically matching issues for a given product and subtopic from the knowledge graph,
    including articles related to the issues via the 'solved_by' relationship.
    """
    driver = GraphDatabase.driver(kg_uri, auth=(kg_user, kg_password))
    query_embedding = embed(query_text)

    cypher = """
    MATCH (p:Product)
    WHERE toLower(p.name) = toLower($product_name) OR any(alias IN p.alias WHERE toLower(alias) = toLower($product_name))

    OPTIONAL MATCH (p)-[:has_subtopic]->(s:SubTopic)
    WHERE $subtopic_name IS NULL OR any(word IN split(toLower($subtopic_name), " ") WHERE word IN split(toLower(s.name), " ") OR any(alias IN s.alias WHERE toLower(alias) = word))

    OPTIONAL MATCH (s)-[:has_issue]->(i:Issue)
    WHERE i.embedding IS NOT NULL

    OPTIONAL MATCH (i)-[:solved_by]->(a:Article)

    WITH p, s, i, a, vector.similarity.cosine(i.embedding, $query_embedding) AS score
    WHERE score > $threshold

    RETURN 
        i.id AS issue_id,
        i.description AS description,
        score,
        p.name AS product,
        s.name AS subtopic,
        collect(DISTINCT {id: a.id, title: a.title, content: a.content}) AS related_articles
    ORDER BY score DESC
    LIMIT $top_k
    """

    with driver.session() as session:
        result = session.run(
            cypher,
            product_name=product_name,
            subtopic_name=subtopic_name,
            query_embedding=query_embedding,
            threshold=threshold,
            top_k=top_k
        )
        return [record.data() for record in result]


def format_issues_with_articles(issues):
    """
    Format the list of issues with their related articles into a readable string format.

    Args:
        issues (list): List of issue dictionaries.

    Returns:
        str: Formatted string containing issue and article details.
    """
    output = ""
    for issue in issues:
        output += f"Issue ID: {issue['issue_id']}\n"
        output += f"Description: {issue['description']}\n"
        output += f"Product: {issue['product']}\n"
        output += f"Subtopic: {issue['subtopic']}\n"
        output += f"Score: {issue['score']:.4f}\n"
        output += "Related Articles:\n"
        for article in issue['related_articles']:
            output += f" - {article['title']} (ID: {article['id']})\n"
        output += "---\n"
    return output


def get_product_details_with_outages(product_name):
    """
    Fetch product details along with any active outages associated with the product.

    Args:
        product_id (str): The ID of the product.

    Returns:
        dict: A dictionary containing product details and active outages.
    """
    driver = GraphDatabase.driver(kg_uri, auth=(kg_user, kg_password))
    with driver.session() as session:
        # Query to fetch product details
        product_query = """
        MATCH (p:Product {name: $product_name})
        RETURN p.id AS product_id, p.name AS name, p.alias AS alias
        """
        product_result = session.run(product_query, product_name=product_name)
        product_details = product_result.single()

        if not product_details:
            return {"error": "Product not found"}

        # Query to fetch active outages related to the product
        outage_query = """
        MATCH (p:Product {name: $product_name})-[:has_outage]->(o:Outage)
        WHERE o.status = 'Active'
        RETURN o.id AS outage_id, o.title AS title, o.description AS description, 
               o.start_time AS start_time, o.expected_resolution AS expected_resolution, 
               o.impact AS impact, o.location AS location
        """
        outage_result = session.run(outage_query, product_name=product_name)
        outages = [record.data() for record in outage_result]

        # Combine product details and outages
        return {
            "product": {
                "id": product_details["product_id"],
                "name": product_details["name"],
                "alias": product_details["alias"]
            },
            "active_outages": outages
        }


def format_product_details_with_outages(details):
    """
    Format product details and active outages into a readable string format.

    Args:
        details (dict): A dictionary containing product details and active outages.

    Returns:
        str: Formatted string containing product and outage details.
    """
    output = f"Product Info:\n"
    output += f"ID: {details['product']['id']}\n"
    output += f"Name: {details['product']['name']}\n"
    output += f"Aliases: {', '.join(details['product']['alias'])}\n\n"

    if details['active_outages']:
        output += "Active Outages:\n"
        for outage in details['active_outages']:
            output += f"Outage ID: {outage['outage_id']}\n"
            output += f"Title: {outage['title']}\n"
            output += f"Description: {outage['description']}\n"
            output += f"Start Time: {outage['start_time']}\n"
            output += f"Expected Resolution: {outage['expected_resolution']}\n"
            output += f"Impact: {outage['impact']}\n"
            output += f"Location: {outage['location']}\n"
            output += "---\n"
    else:
        output += "No active outages.\n"

    return output

def get_subtopic_details(product_name, subtopic_name):
    """
    Fetch subtopic details for a given product and subtopic name.

    Args:
        product_name (str): Name of the product.
        subtopic_name (str): Name of the subtopic.

    Returns:
        dict: A dictionary containing subtopic details.
    """
    driver = GraphDatabase.driver(kg_uri, auth=(kg_user, kg_password))
    with driver.session() as session:
        query = """
        MATCH (p:Product)-[:has_subtopic]->(s:SubTopic)
        WHERE toLower(p.name) = toLower($product_name) AND  any(word IN split(toLower($subtopic_name), " ") WHERE word IN split(toLower(s.name), " ") OR any(alias IN s.alias WHERE toLower(alias) = word))

        RETURN s.id AS id, s.name AS name, s.alias AS alias, s.Constraints AS constraints, 
               s.Access AS access, s.`Common Issues` AS common_issues
        """
        result = session.run(query, product_name=product_name, subtopic_name=subtopic_name)
        subtopic_details = result.single()
        if subtopic_details:
            return {
                "id": subtopic_details["id"],
                "name": subtopic_details["name"],
                "alias": subtopic_details["alias"],
                "Constraints": subtopic_details["constraints"],
                "Access": subtopic_details["access"],
                "Common_Issues": subtopic_details["common_issues"]
            }
        return None
def get_user_device_relationship(user_id):
    """
    Fetch the device associated with a specific user ID based on the 'has_device' relationship.

    Args:
        user_id (str): The ID of the user.

    Returns:
        dict: A dictionary containing user and device details.
    """
    driver = GraphDatabase.driver(kg_uri, auth=(kg_user, kg_password))
    with driver.session() as session:
        query = """
        MATCH (u:User {id: $user_id})-[:has_device]->(d:Device)
        RETURN u.name AS name, u.email AS email, u.location AS location, u.band AS band, u.team AS team,
               d.id AS device_id, d.model AS device_model, d.os AS device_os, d.os_version AS os_version, 
               d.ram AS ram, d.storage AS storage, d.lastupdate AS last_update, d.issued_on AS issued_on, 
               d.pending_updates AS pending_updates
        """
        result = session.run(query, user_id=user_id)
        user_device_details = result.single()
        if user_device_details:
            return {
                "name": user_device_details["name"],
                "email": user_device_details["email"],
                "location": user_device_details["location"],
                "band": user_device_details["band"],
                "team": user_device_details["team"],
                "device": {
                    "model": user_device_details["device_model"],
                    "os": user_device_details["device_os"],
                    "os_version": user_device_details["os_version"],
                    "ram": user_device_details["ram"],
                    "storage": user_device_details["storage"],
                    "last_update": user_device_details["last_update"],
                    "issued_on": user_device_details["issued_on"],
                    "pending_updates": user_device_details["pending_updates"],
                    "device_id": user_device_details["device_id"]
                    
                }
            }
        return None

def format_user_details(user_details, user_id):
    """
    Format user details and device details into a readable string format.

    Args:
        user_details (dict): A dictionary containing user and device details.
        user_id (str): The ID of the user.

    Returns:
        str: Formatted string containing user and device details.
    """
    if not user_details:
        return "User details not found."

    output = f"User Info:\n"
    output += f"User ID: {user_id}\n"
    output += f"Name: {user_details['name']}\n"
    output += f"Email: {user_details['email']}\n"
    output += f"Location: {user_details['location']}\n"
    output += f"Band: {user_details['band']}\n"
    output += f"Team: {user_details['team']}\n"
    output += f"\nDevice Info:\n"
    output += f"Device ID: {user_details['device']['device_id']}\n"
    output += f"Model: {user_details['device']['model']}\n"
    output += f"OS: {user_details['device']['os']}\n"
    output += f"OS Version: {user_details['device']['os_version']}\n"
    output += f"RAM: {user_details['device']['ram']} GB\n"
    output += f"Storage: {user_details['device']['storage']} GB\n"
    output += f"Last Update: {user_details['device']['last_update']}\n"
    output += f"Issued On: {user_details['device']['issued_on']}\n"
    output += f"Pending Updates: {user_details['device']['pending_updates']}\n"
    return output


def get_user_device_relationship(user_id):
    """
    Fetch the device associated with a specific user ID based on the 'has_device' relationship.

    Args:
        user_id (str): The ID of the user.

    Returns:
        dict: A dictionary containing user and device details.
    """
    driver = GraphDatabase.driver(kg_uri, auth=(kg_user, kg_password))
    with driver.session() as session:
        query = """
        MATCH (u:User {id: $user_id})-[:has_device]->(d:Device)
        RETURN u.name AS name, u.email AS email, u.location AS location, u.band AS band, u.team AS team,
               d.id AS device_id, d.model AS device_model, d.os AS device_os, d.os_version AS os_version, 
               d.ram AS ram, d.storage AS storage, d.lastupdate AS last_update, d.issued_on AS issued_on, 
               d.pending_updates AS pending_updates
        """
        result = session.run(query, user_id=user_id)
        user_device_details = result.single()
        if user_device_details:
            return {
                "name": user_device_details["name"],
                "email": user_device_details["email"],
                "location": user_device_details["location"],
                "band": user_device_details["band"],
                "team": user_device_details["team"],
                "device": {
                    "model": user_device_details["device_model"],
                    "os": user_device_details["device_os"],
                    "os_version": user_device_details["os_version"],
                    "ram": user_device_details["ram"],
                    "storage": user_device_details["storage"],
                    "last_update": user_device_details["last_update"],
                    "issued_on": user_device_details["issued_on"],
                    "pending_updates": user_device_details["pending_updates"],
                    "device_id": user_device_details["device_id"]
                    
                }
            }
        return None

def format_user_details(user_details, user_id):
    """
    Format user details and device details into a readable string format.

    Args:
        user_details (dict): A dictionary containing user and device details.
        user_id (str): The ID of the user.

    Returns:
        str: Formatted string containing user and device details.
    """
    if not user_details:
        return "User details not found."

    output = f"User Info:\n"
    output += f"User ID: {user_id}\n"
    output += f"Name: {user_details['name']}\n"
    output += f"Email: {user_details['email']}\n"
    output += f"Location: {user_details['location']}\n"
    output += f"Band: {user_details['band']}\n"
    output += f"Team: {user_details['team']}\n"
    output += f"\nDevice Info:\n"
    output += f"Device ID: {user_details['device']['device_id']}\n"
    output += f"Model: {user_details['device']['model']}\n"
    output += f"OS: {user_details['device']['os']}\n"
    output += f"OS Version: {user_details['device']['os_version']}\n"
    output += f"RAM: {user_details['device']['ram']} GB\n"
    output += f"Storage: {user_details['device']['storage']} GB\n"
    output += f"Last Update: {user_details['device']['last_update']}\n"
    output += f"Issued On: {user_details['device']['issued_on']}\n"
    output += f"Pending Updates: {user_details['device']['pending_updates']}\n"
    return output


def get_product_details_with_outages(product_name):
    """
    Fetch product details along with any active outages associated with the product.

    Args:
        product_id (str): The ID of the product.

    Returns:
        dict: A dictionary containing product details and active outages.
    """
    driver = GraphDatabase.driver(kg_uri, auth=(kg_user, kg_password))
    with driver.session() as session:
        # Query to fetch product details
        product_query = """
        MATCH (p:Product {name: $product_name})
        RETURN p.id AS product_id, p.name AS name, p.alias AS alias
        """
        product_result = session.run(product_query, product_name=product_name)
        product_details = product_result.single()

        if not product_details:
            return {"error": "Product not found"}

        # Query to fetch active outages related to the product
        outage_query = """
        MATCH (p:Product {name: $product_name})-[:has_outage]->(o:Outage)
        WHERE o.status = 'Active'
        RETURN o.id AS outage_id, o.title AS title, o.description AS description, 
               o.start_time AS start_time, o.expected_resolution AS expected_resolution, 
               o.impact AS impact, o.location AS location
        """
        outage_result = session.run(outage_query, product_name=product_name)
        outages = [record.data() for record in outage_result]

        # Combine product details and outages
        return {
            "product": {
                "id": product_details["product_id"],
                "name": product_details["name"],
                "alias": product_details["alias"]
            },
            "active_outages": outages
        }


def format_product_details_with_outages(details):
    """
    Format product details and active outages into a readable string format.

    Args:
        details (dict): A dictionary containing product details and active outages.

    Returns:
        str: Formatted string containing product and outage details.
    """
    output = f"Product Info:\n"
    output += f"ID: {details['product']['id']}\n"
    output += f"Name: {details['product']['name']}\n"
    output += f"Aliases: {', '.join(details['product']['alias'])}\n\n"

    if details['active_outages']:
        output += "Active Outages:\n"
        for outage in details['active_outages']:
            output += f"Outage ID: {outage['outage_id']}\n"
            output += f"Title: {outage['title']}\n"
            output += f"Description: {outage['description']}\n"
            output += f"Start Time: {outage['start_time']}\n"
            output += f"Expected Resolution: {outage['expected_resolution']}\n"
            output += f"Impact: {outage['impact']}\n"
            output += f"Location: {outage['location']}\n"
            output += "---\n"
    else:
        output += "No active outages.\n"

    return output

def get_subtopic_details(product_name, subtopic_name):
    """
    Fetch subtopic details for a given product and subtopic name.

    Args:
        product_name (str): Name of the product.
        subtopic_name (str): Name of the subtopic.

    Returns:
        dict: A dictionary containing subtopic details.
    """
    driver = GraphDatabase.driver(kg_uri, auth=(kg_user, kg_password))
    with driver.session() as session:
        query = """
        MATCH (p:Product)-[:has_subtopic]->(s:SubTopic)
        WHERE toLower(p.name) = toLower($product_name) AND  any(word IN split(toLower($subtopic_name), " ") WHERE word IN split(toLower(s.name), " ") OR any(alias IN s.alias WHERE toLower(alias) = word))

        RETURN s.id AS id, s.name AS name, s.alias AS alias, s.Constraints AS constraints, 
               s.Access AS access, s.`Common Issues` AS common_issues
        """
        result = session.run(query, product_name=product_name, subtopic_name=subtopic_name)
        subtopic_details = result.single()
        if subtopic_details:
            return {
                "id": subtopic_details["id"],
                "name": subtopic_details["name"],
                "alias": subtopic_details["alias"],
                "Constraints": subtopic_details["constraints"],
                "Access": subtopic_details["access"],
                "Common_Issues": subtopic_details["common_issues"]
            }
        return None
    
# # Example usage
# active_outages = get_product_details_with_outages("Outlook")
# # Example usage
# formatted_output_outage = format_product_details_with_outages(active_outages)
# print(formatted_output_outage)




# subtopic_details = get_subtopic_details(product_name="Webex", subtopic_name="Audio")
# if subtopic_details:
#     formatted_subtopic_details = universal_formatting_function(subtopic_details, heading="Subtopic Details")
#     print(formatted_subtopic_details)
# else:
#     print("Subtopic not found.")



def generate_structured_kg_output(input: dict):
    """
    Generate a structured KG output by combining all keys and their values from the input dictionary.

    Args:
        input (dict): Dictionary containing various formatted data.

    Returns:
        str: Combined structured KG output.
    """
    def format_section(key, value):
        if isinstance(value, dict):
            formatted_value = "\n".join(f"{sub_key}: {sub_value}" for sub_key, sub_value in value.items())
        elif isinstance(value, list):
            formatted_value = "\n".join(str(item) for item in value)
        else:
            formatted_value = str(value)

        line = "-"*10
        return f"🔹 {key}:\n{formatted_value}\n{line}\n"

    return  "\n".join(format_section(key, value) for key, value in input.items())

