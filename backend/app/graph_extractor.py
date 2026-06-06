import networkx as nx
import json
from langchain_community.llms import Ollama
llm = Ollama(model="llama3.2:1b")
G = nx.Graph()
def extract_entities_and_relations(text: str) -> list:
    prompt = f"""Extract all (subject, relation, object) triples from the text.
Return a JSON array of objects with keys: subject, relation, object.
Only meaningful relationships.
Text: {text}
Output:"""
    response = llm.invoke(prompt)
    try:
        start = response.find('[')
        end = response.rfind(']') + 1
        return json.loads(response[start:end])
    except:
        return []
def add_to_graph(triples: list):
    for t in triples:
        s, r, o = t.get("subject"), t.get("relation"), t.get("object")
        if s and r and o:
            G.add_node(s, type="entity")
            G.add_node(o, type="entity")
            G.add_edge(s, o, relation=r)
def process_document(text: str):
    triples = extract_entities_and_relations(text)
    add_to_graph(triples)
    return triples
def query_graph(question: str) -> str:
    for node in G.nodes:
        if node.lower() in question.lower():
            neighbors = list(G.neighbors(node))
            if neighbors:
                return f"{node} is related to: {', '.join(neighbors)}"
    return "No relevant information in knowledge graph."
