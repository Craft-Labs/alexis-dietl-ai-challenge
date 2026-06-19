"""
Seed the Neo4j Knowledge Graph with Alexis Dietl's Culinary Profile.
Run this once to populate the KG with entities and relationships that the agent can query.
Usage: python seed_kg.py
"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

def seed_knowledge_graph():
    """Populate Neo4j with Alexis Dietl's culinary profile entities and relationships."""
    
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASS]):
        print("Error: Missing Neo4j environment variables. Please check your .env file.")
        return

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    with driver.session() as session:
        # Clear existing data
        print("Clearing existing data...")
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create entities and relationships
        print("Seeding new knowledge graph data...")
        session.run("""
        // ─── Create Core Nodes ───
        CREATE (p:Person {name: 'Alexis Dietl', profile: 'Open mind and remarkably diverse palate, connecting different hemispheres and contrasting culinary traditions.'})
        
        CREATE (r1:Region {name: 'South America', category: 'Geographic region'})
        CREATE (r2:Region {name: 'South Korea', category: 'Nation'})
        CREATE (r3:Region {name: 'North America', category: 'Geographic region'})
        
        CREATE (d1:Dish {name: 'Asado', description: 'Foundational pillar of diet, profound social ritual, bonding time, and celebration of community.'})
        CREATE (d2:Dish {name: 'Sweetbreads', description: 'Offal cut corresponding anatomically to veal thymus gland or pancreas; crispy outside, tender inside.'})
        CREATE (d3:Dish {name: 'Hot Dogs', description: 'Classic urban street food representing simplicity and convenience.'})
        CREATE (d4:Dish {name: 'Rice with Pork and Kimchi', description: 'East Asian dish combining complex carbohydrates, rich pork fat texture, and sharp aroma.'})
        CREATE (d5:Dish {name: 'Kimchi', description: 'Lacto-fermented vegetable dish seasoned with chili powder, garlic, and ginger.'})
        
        CREATE (i1:Ingredient {name: 'Red Meat', type: 'Protein'})
        CREATE (i2:Ingredient {name: 'Quebracho Firewood', type: 'Fuel / Aromatics'})
        CREATE (i3:Ingredient {name: 'Charcoal Briquettes', type: 'Fuel'})
        CREATE (i4:Ingredient {name: 'Lemon Juice', type: 'Acid / Marinade'})
        CREATE (i5:Ingredient {name: 'Processed Sausages', type: 'Emulsified meat'})
        CREATE (i6:Ingredient {name: 'Wheat Bun', type: 'Leavened bread'})
        CREATE (i7:Ingredient {name: 'Short-grain Sticky Rice', type: 'Carbohydrate'})
        CREATE (i8:Ingredient {name: 'Pork Fat', type: 'Fat'})
        CREATE (i9:Ingredient {name: 'Napa Cabbage', type: 'Vegetable'})
        CREATE (i10:Ingredient {name: 'Korean Radish', type: 'Vegetable'})
        CREATE (i11:Ingredient {name: 'Gochugaru', type: 'Chili Powder'})
        
        CREATE (t1:Technique {name: 'Slow-cooking', description: 'Cooking method over low, steady heat.'})
        CREATE (t2:Technique {name: 'Grilling', description: 'High-temperature open flame cooking.'})
        CREATE (t3:Technique {name: 'Lacto-fermentation', description: 'Live fermentation introducing deep umami, acidity, and gut-healthy properties.'})
        CREATE (t4:Technique {name: 'Meticulous Preparation', description: 'Cleaning, parboiling, and marinating offal cuts.'})

        CREATE (c1:Concept {name: 'Umami', description: 'Deep, savory flavor profile.'})
        CREATE (c2:Concept {name: 'Capsicum Heat', description: 'Spicy flavor dimension from chili inputs.'})

        // ─── Create Relationships ───
        // Preferences
        CREATE (p)-[:PREFERS]->(d1)
        CREATE (p)-[:PREFERS]->(d2)
        CREATE (p)-[:PREFERS]->(d3)
        CREATE (p)-[:PREFERS]->(d4)
        
        // Regional Connections
        CREATE (d1)-[:ORIGINATES_FROM]->(r1)
        CREATE (d2)-[:ORIGINATES_FROM]->(r1)
        CREATE (d3)-[:ASSOCIATED_WITH]->(r3)
        CREATE (d4)-[:ORIGINATES_FROM]->(r2)
        CREATE (d5)-[:ORIGINATES_FROM]->(r2)
        
        // Dish Ingredients
        CREATE (d1)-[:CONTAINS]->(i1)
        CREATE (d2)-[:CONTAINS]->(i4)
        CREATE (d3)-[:CONTAINS]->(i5)
        CREATE (d3)-[:CONTAINS]->(i6)
        CREATE (d4)-[:CONTAINS]->(i7)
        CREATE (d4)-[:CONTAINS]->(i8)
        CREATE (d4)-[:CONTAINS]->(d5)
        CREATE (d5)-[:CONTAINS]->(i9)
        CREATE (d5)-[:CONTAINS]->(i10)
        CREATE (d5)-[:CONTAINS]->(i11)
        
        // Techniques & Cooking Elements
        CREATE (d1)-[:REQUIRES]->(t1)
        CREATE (d1)-[:USES_FUEL]->(i2)
        CREATE (d1)-[:USES_FUEL]->(i3)
        CREATE (d2)-[:REQUIRES]->(t4)
        CREATE (d2)-[:REQUIRES]->(t2)
        CREATE (d5)-[:USES_PROCESS]->(t3)
        
        // Profiles & Concepts
        CREATE (t3)-[:PRODUCES]->(c1)
        CREATE (i11)-[:PROVIDES]->(c2)
        CREATE (d5)-[:PROVIDES]->(c1)
        """)
        
        # Create full-text search index updated for these new node labels
        print("Setting up full-text search index...")
        try:
            # Drop old index if it exists to avoid type conflicts
            session.run("DROP INDEX search_index IF EXISTS")
            
            session.run("""
            CREATE FULLTEXT INDEX search_index IF NOT EXISTS 
            FOR (n:Person|Region|Dish|Ingredient|Technique|Concept) 
            ON EACH [n.name, n.description, n.profile, n.category, n.type]
            """)
            print("Full-text search index successfully created.")
        except Exception as e:
            print(f"Index creation warning: {e}")
            
    driver.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_knowledge_graph()