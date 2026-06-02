from neo4j import GraphDatabase
import logging
logger = logging.getLogger("graph_rag")
class Neo4jGraph:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="test1234"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    def close(self):
        self.driver.close()
    def add_entity(self, entity_name, entity_type, properties=None):
        with self.driver.session() as session:
            session.run(
                "MERGE (e:Entity {name: $name}) SET e.type = $type, e += $props",
                name=entity_name, type=entity_type, props=properties or {}
            )
    def add_relationship(self, entity1, entity2, relation):
        with self.driver.session() as session:
            session.run(
                "MATCH (a:Entity {name: $e1}), (b:Entity {name: $e2}) "
                "MERGE (a)-[r:RELATES {type: $rel}]->(b)",
                e1=entity1, e2=entity2, rel=relation
            )
    def query(self, question):
        # Simple query: extract entities from question and find connected nodes
        # For now, return a placeholder
        return "Graph query result. Use Neo4j browser at http://localhost:7474 to explore."
graph = Neo4jGraph()
