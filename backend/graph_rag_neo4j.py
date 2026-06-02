from neo4j import GraphDatabase
import json
from langchain_community.llms import Ollama
llm = Ollama(model="llama3.2:1b")
class Neo4jGraph:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="test1234"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    def close(self):
        self.driver.close()
    def extract_entities(self, question: str) -> dict:
        prompt = f"From: '{question}', extract entity and relation as JSON: {{\"entity\":\"...\",\"relation\":\"...\"}}"
        resp = llm.invoke(prompt)
        try:
            return json.loads(resp[resp.find('{'):resp.rfind('}')+1])
        except:
            return {}
    def query(self, question: str) -> str:
        data = self.extract_entities(question)
        entity = data.get("entity")
        if not entity:
            return "No entity found."
        with self.driver.session() as session:
            result = session.run("MATCH (a {name: $e})-[r]->(b) RETURN b.name AS name", e=entity)
            neighbors = [record["name"] for record in result]
        if neighbors:
            return f"{entity} is connected to: {', '.join(neighbors)}"
        return f"No connections for {entity}."
graph_neo = Neo4jGraph()
