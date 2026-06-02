import networkx as nx
import json
from langchain_community.llms import Ollama
llm = Ollama(model="llama3.2:1b")
# Create graph
G = nx.Graph()
def add_entity(entity, entity_type, properties=None):
    """Add a node to the graph"""
    G.add_node(entity, type=entity_type, properties=properties or {})
def add_relationship(entity1, entity2, relation):
    """Add an edge between two entities"""
    G.add_edge(entity1, entity2, relation=relation)
def query_graph(question: str) -> str:
    """Use LLM to extract entities and query the graph"""
    prompt = f"""From the question: "{question}", extract the main entities and the relationship you want to find.
Return a JSON object with keys "entity1", "entity2", "relation". If unknown, return empty.
Example: {{"entity1": "India", "entity2": "capital", "relation": "has_capital"}}"""
    response = llm.invoke(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        data = json.loads(response[start:end])
        if data.get("entity1") and data.get("relation"):
            # Find neighbors
            neighbors = list(G.neighbors(data["entity1"]))
            if neighbors:
                return f"{data['entity1']} {data['relation']} {', '.join(neighbors)}"
    except:
        pass
    return "No graph information found."
def add_document_entities(text: str):
    """Extract entities from a document using LLM and add to graph"""
    prompt = f"Extract all important entities (people, places, things) from this text as a comma-separated list:\n{text[:500]}"
    entities = llm.invoke(prompt).split(',')
    for e in entities:
        add_entity(e.strip(), "document")
