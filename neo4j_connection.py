
from neo4j import GraphDatabase

class Neo4jConnection:
    """Simple Neo4j database connection"""
    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the Neo4j connection"""
        self.driver.close()

    def run_query(self, query, parameters=None):
        """Execute a Cypher query"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

def connect_neo4j():
    """Connect to Neo4j database"""
  
    uri = "neo4j+ssc://8a569689.databases.neo4j.io"
    user = "neo4j"
    password = "n6zO8HsnKL-CffsF6DmzHlT5BPGNfNWGzUzYuVfIX_k"
    
    try:
        conn = Neo4jConnection(uri, user, password)
        print("Connected to Neo4j successfully")
        return conn
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        return None

def close_connection(driver):
    """Close Neo4j connection"""
    if driver:
        driver.close()