"""
Example usage of Neo4jService class

This file demonstrates best practices for using the Neo4jService class
with graph operations, Cypher queries, and async patterns.
"""

import asyncio
from neo4j_service import Neo4jService
from typing import Dict, List

async def basic_example():
    """Example of basic Neo4j operations"""
    
    # Initialize the service
    neo4j_service = Neo4jService(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password",
        database="neo4j"
    )
    
    try:
        # Test connectivity
        if await neo4j_service.ping():
            print("✅ Neo4j connection successful")
        else:
            print("❌ Neo4j connection failed")
            return
        
        # Example 1: Create nodes
        print("\n📝 Creating nodes...")
        
        # Create person nodes
        await neo4j_service.create_node(
            "Person",
            {"name": "Alice", "age": 30, "city": "New York"}
        )
        
        await neo4j_service.create_node(
            "Person", 
            {"name": "Bob", "age": 25, "city": "San Francisco"}
        )
        
        await neo4j_service.create_node(
            "Person",
            {"name": "Charlie", "age": 35, "city": "New York"}
        )
        
        # Create company nodes
        await neo4j_service.create_node(
            "Company",
            {"name": "TechCorp", "industry": "Technology", "size": "Large"}
        )
        
        await neo4j_service.create_node(
            "Company",
            {"name": "DataInc", "industry": "Analytics", "size": "Medium"}
        )
        
        print("✅ Nodes created successfully")
        
        # Example 2: Create relationships
        print("\n🔗 Creating relationships...")
        
        # Alice works at TechCorp
        await neo4j_service.create_relationship(
            ":Person {name: 'Alice'}",
            ":Company {name: 'TechCorp'}",
            "WORKS_AT",
            {"role": "Engineer", "since": 2020}
        )
        
        # Bob works at DataInc
        await neo4j_service.create_relationship(
            ":Person {name: 'Bob'}",
            ":Company {name: 'DataInc'}",
            "WORKS_AT",
            {"role": "Analyst", "since": 2021}
        )
        
        # Alice knows Bob
        await neo4j_service.create_relationship(
            ":Person {name: 'Alice'}",
            ":Person {name: 'Bob'}",
            "KNOWS",
            {"since": 2019, "relationship": "friend"}
        )
        
        # Charlie knows Alice
        await neo4j_service.create_relationship(
            ":Person {name: 'Charlie'}",
            ":Person {name: 'Alice'}",
            "KNOWS",
            {"since": 2018, "relationship": "colleague"}
        )
        
        print("✅ Relationships created successfully")
        
        # Example 3: Query nodes
        print("\n🔍 Querying nodes...")
        
        # Find all persons
        persons = await neo4j_service.find_nodes("Person")
        print(f"Found {len(persons)} persons:")
        for person in persons:
            node_data = person['n']
            print(f"  - {node_data['name']} ({node_data['age']}) from {node_data['city']}")
        
        # Find persons in New York
        ny_persons = await neo4j_service.find_nodes(
            "Person",
            {"city": "New York"}
        )
        print(f"\nFound {len(ny_persons)} persons in New York")
        
        # Example 4: Custom Cypher queries
        print("\n📊 Running custom queries...")
        
        # Find all work relationships
        work_query = """
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        RETURN p.name as person_name, r.role as role, c.name as company_name, r.since as since
        ORDER BY r.since
        """
        
        work_relationships = await neo4j_service.run_query(work_query)
        print("Work relationships:")
        for rel in work_relationships:
            print(f"  - {rel['person_name']} works as {rel['role']} at {rel['company_name']} since {rel['since']}")
        
        # Find mutual connections
        mutual_query = """
        MATCH (p1:Person)-[:KNOWS]-(p2:Person)-[:KNOWS]-(p3:Person)
        WHERE p1 <> p3
        RETURN p1.name as person1, p2.name as connector, p3.name as person3
        """
        
        mutual_connections = await neo4j_service.run_query(mutual_query)
        if mutual_connections:
            print("\nMutual connections:")
            for conn in mutual_connections:
                print(f"  - {conn['person1']} connected to {conn['person3']} through {conn['connector']}")
        
        # Example 5: Path finding
        print("\n🛤️  Finding paths...")
        
        # Find paths between Alice and Bob
        paths = await neo4j_service.find_paths(
            ":Person {name: 'Alice'}",
            ":Person {name: 'Bob'}",
            relationship_pattern="*",
            max_depth=3
        )
        
        print(f"Found {len(paths)} paths between Alice and Bob")
        
        # Example 6: Node degree analysis
        print("\n📈 Analyzing node connections...")
        
        alice_degree = await neo4j_service.get_node_degree(
            ":Person {name: 'Alice'}",
            direction="BOTH"
        )
        print(f"Alice has {alice_degree} total connections")
        
        # Get database statistics
        print("\n📊 Database statistics...")
        db_info = await neo4j_service.get_database_info()
        print(f"Total nodes: {db_info.get('node_count', 'Unknown')}")
        print(f"Total relationships: {db_info.get('relationship_count', 'Unknown')}")
        print(f"Node labels: {', '.join(db_info.get('labels', []))}")
        print(f"Relationship types: {', '.join(db_info.get('relationship_types', []))}")
        
        print("\n" + "="*50)
        print("🎉 All basic examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in basic example: {e}")
    finally:
        await neo4j_service.close()


async def transaction_example():
    """Example of transaction management"""
    
    neo4j_service = Neo4jService(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password",
        database="neo4j"
    )
    
    try:
        print("\n💼 Transaction example...")
        
        # Example 1: Successful transaction
        async with neo4j_service.get_transaction() as tx:
            # Create multiple nodes in one transaction
            await tx.run(
                "CREATE (p:Person {name: $name, age: $age})",
                name="David", age=28
            )
            await tx.run(
                "CREATE (p:Person {name: $name, age: $age})",
                name="Emma", age=32
            )
            await tx.run(
                "MATCH (d:Person {name: 'David'}), (e:Person {name: 'Emma'}) "
                "CREATE (d)-[:KNOWS {since: 2022}]->(e)"
            )
            print("✅ Transaction completed successfully")
        
        # Example 2: Transaction with error handling
        try:
            async with neo4j_service.get_transaction() as tx:
                await tx.run(
                    "CREATE (p:Person {name: $name})",
                    name="Frank"
                )
                # This will cause an error (invalid Cypher)
                await tx.run("INVALID CYPHER QUERY")
        except Exception as e:
            print(f"⚠️  Transaction rolled back due to error: {e}")
        
        # Verify Frank was not created (due to rollback)
        frank = await neo4j_service.run_query_single(
            "MATCH (p:Person {name: 'Frank'}) RETURN p"
        )
        if frank is None:
            print("✅ Rollback successful - Frank was not created")
        
        print("\n" + "="*50)
        print("🎉 Transaction examples completed!")
        
    except Exception as e:
        print(f"❌ Error in transaction example: {e}")
    finally:
        await neo4j_service.close()


async def graph_analytics_example():
    """Example of graph analytics and complex queries"""
    
    neo4j_service = Neo4jService(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password",
        database="neo4j"
    )
    
    try:
        print("\n📊 Graph analytics example...")
        
        # Create a more complex graph for analytics
        companies = [
            {"name": "TechStart", "industry": "Technology", "size": "Small"},
            {"name": "MegaCorp", "industry": "Finance", "size": "Large"},
            {"name": "Innovation Labs", "industry": "Research", "size": "Medium"}
        ]
        
        persons = [
            {"name": "John", "age": 29, "skill": "Python"},
            {"name": "Jane", "age": 34, "skill": "Data Science"},
            {"name": "Mike", "age": 31, "skill": "DevOps"},
            {"name": "Sarah", "age": 27, "skill": "Frontend"}
        ]
        
        # Create nodes
        for company in companies:
            await neo4j_service.create_node("Company", company)
        
        for person in persons:
            await neo4j_service.create_node("Developer", person, ["Person"])
        
        # Create complex relationships
        relationships = [
            ("John", "TechStart", "WORKS_AT", {"role": "Senior Developer"}),
            ("Jane", "MegaCorp", "WORKS_AT", {"role": "Data Scientist"}),
            ("Mike", "Innovation Labs", "WORKS_AT", {"role": "DevOps Engineer"}),
            ("Sarah", "TechStart", "WORKS_AT", {"role": "Frontend Developer"}),
            ("John", "Jane", "KNOWS", {"relationship": "mentor"}),
            ("John", "Sarah", "MENTORS", {"since": 2023}),
            ("Mike", "Jane", "COLLABORATES_WITH", {"project": "ML Pipeline"}),
        ]
        
        for rel in relationships:
            person1, person2_or_company, rel_type, props = rel
            if rel_type == "WORKS_AT":
                await neo4j_service.create_relationship(
                    f":Developer {{name: '{person1}'}}",
                    f":Company {{name: '{person2_or_company}'}}",
                    rel_type,
                    props
                )
            else:
                await neo4j_service.create_relationship(
                    f":Developer {{name: '{person1}'}}",
                    f":Developer {{name: '{person2_or_company}'}}",
                    rel_type,
                    props
                )
        
        print("✅ Complex graph created for analytics")
        
        # Analytics Query 1: Find most connected developers
        most_connected_query = """
        MATCH (d:Developer)
        OPTIONAL MATCH (d)-[r]-()
        RETURN d.name as developer, d.skill as skill, count(r) as connections
        ORDER BY connections DESC
        LIMIT 5
        """
        
        most_connected = await neo4j_service.run_query(most_connected_query)
        print("\n🏆 Most connected developers:")
        for dev in most_connected:
            print(f"  - {dev['developer']} ({dev['skill']}): {dev['connections']} connections")
        
        # Analytics Query 2: Company with most developers
        company_size_query = """
        MATCH (c:Company)<-[:WORKS_AT]-(d:Developer)
        RETURN c.name as company, c.industry as industry, count(d) as developer_count
        ORDER BY developer_count DESC
        """
        
        company_sizes = await neo4j_service.run_query(company_size_query)
        print("\n🏢 Companies by developer count:")
        for company in company_sizes:
            print(f"  - {company['company']} ({company['industry']}): {company['developer_count']} developers")
        
        # Analytics Query 3: Skill distribution
        skill_distribution_query = """
        MATCH (d:Developer)
        RETURN d.skill as skill, count(d) as count
        ORDER BY count DESC
        """
        
        skills = await neo4j_service.run_query(skill_distribution_query)
        print("\n💻 Skill distribution:")
        for skill in skills:
            print(f"  - {skill['skill']}: {skill['count']} developers")
        
        # Analytics Query 4: Find mentorship chains
        mentorship_query = """
        MATCH path = (mentor:Developer)-[:MENTORS*1..3]->(mentee:Developer)
        RETURN [node in nodes(path) | node.name] as mentorship_chain,
               length(path) as chain_length
        ORDER BY chain_length DESC
        """
        
        mentorships = await neo4j_service.run_query(mentorship_query)
        print("\n👨‍🏫 Mentorship chains:")
        for chain in mentorships:
            chain_str = " → ".join(chain['mentorship_chain'])
            print(f"  - {chain_str} (length: {chain['chain_length']})")
        
        print("\n" + "="*50)
        print("🎉 Graph analytics examples completed!")
        
    except Exception as e:
        print(f"❌ Error in analytics example: {e}")
    finally:
        await neo4j_service.close()


class GraphRepository:
    """
    Example repository pattern for graph operations
    
    This shows how to build domain-specific abstractions on top of Neo4jService
    """
    
    def __init__(self, neo4j_service: Neo4jService):
        self.graph = neo4j_service
    
    async def create_person(self, name: str, age: int, **attributes) -> Dict:
        """Create a person node with attributes"""
        properties = {"name": name, "age": age, **attributes}
        return await self.graph.create_node("Person", properties)
    
    async def create_friendship(self, person1_name: str, person2_name: str, since: int = None):
        """Create a friendship relationship between two people"""
        props = {"since": since} if since else {}
        return await self.graph.create_relationship(
            f":Person {{name: '{person1_name}'}}",
            f":Person {{name: '{person2_name}'}}",
            "FRIENDS_WITH",
            props
        )
    
    async def get_friends(self, person_name: str) -> List[Dict]:
        """Get all friends of a person"""
        query = """
        MATCH (p:Person {name: $name})-[:FRIENDS_WITH]-(friend:Person)
        RETURN friend.name as name, friend.age as age
        ORDER BY friend.name
        """
        return await self.graph.run_query(query, {"name": person_name})
    
    async def get_mutual_friends(self, person1: str, person2: str) -> List[Dict]:
        """Find mutual friends between two people"""
        query = """
        MATCH (p1:Person {name: $person1})-[:FRIENDS_WITH]-(mutual:Person)-[:FRIENDS_WITH]-(p2:Person {name: $person2})
        RETURN mutual.name as name, mutual.age as age
        """
        return await self.graph.run_query(query, {"person1": person1, "person2": person2})
    
    async def suggest_friends(self, person_name: str, max_suggestions: int = 5) -> List[Dict]:
        """Suggest friends based on mutual connections"""
        query = """
        MATCH (p:Person {name: $name})-[:FRIENDS_WITH]-(friend:Person)-[:FRIENDS_WITH]-(suggestion:Person)
        WHERE NOT (p)-[:FRIENDS_WITH]-(suggestion) AND p <> suggestion
        RETURN suggestion.name as name, suggestion.age as age, count(friend) as mutual_friends
        ORDER BY mutual_friends DESC
        LIMIT $limit
        """
        return await self.graph.run_query(query, {"name": person_name, "limit": max_suggestions})


async def repository_example():
    """Example using the repository pattern"""
    
    neo4j_service = Neo4jService(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password",
        database="neo4j"
    )
    
    try:
        print("\n🏗️  Repository pattern example...")
        
        repo = GraphRepository(neo4j_service)
        
        # Create a social network
        people = [
            ("Alice", 30, {"city": "NYC", "job": "Engineer"}),
            ("Bob", 25, {"city": "SF", "job": "Designer"}),
            ("Charlie", 35, {"city": "NYC", "job": "Manager"}),
            ("Diana", 28, {"city": "LA", "job": "Analyst"}),
            ("Eve", 32, {"city": "NYC", "job": "Engineer"})
        ]
        
        # Create people
        for name, age, attrs in people:
            await repo.create_person(name, age, **attrs)
        
        # Create friendships
        friendships = [
            ("Alice", "Bob", 2020),
            ("Alice", "Charlie", 2019),
            ("Bob", "Diana", 2021),
            ("Charlie", "Eve", 2018),
            ("Diana", "Eve", 2022)
        ]
        
        for person1, person2, since in friendships:
            await repo.create_friendship(person1, person2, since)
        
        print("✅ Social network created")
        
        # Use repository methods
        alice_friends = await repo.get_friends("Alice")
        print(f"\n👥 Alice's friends: {[f['name'] for f in alice_friends]}")
        
        mutual_friends = await repo.get_mutual_friends("Alice", "Diana")
        print(f"🤝 Mutual friends between Alice and Diana: {[f['name'] for f in mutual_friends]}")
        
        suggestions = await repo.suggest_friends("Alice")
        print("💡 Friend suggestions for Alice:")
        for suggestion in suggestions:
            print(f"  - {suggestion['name']} (age {suggestion['age']}) - {suggestion['mutual_friends']} mutual friends")
        
        print("\n" + "="*50)
        print("🎉 Repository pattern example completed!")
        
    except Exception as e:
        print(f"❌ Error in repository example: {e}")
    finally:
        await neo4j_service.close()


async def cleanup_example():
    """Example of database cleanup (use with caution!)"""
    
    neo4j_service = Neo4jService(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password",
        database="neo4j"
    )
    
    try:
        print("\n🧹 Database cleanup example...")
        print("⚠️  WARNING: This will delete ALL data in the database!")
        
        # Get stats before cleanup
        before_stats = await neo4j_service.get_database_info()
        print(f"Before cleanup - Nodes: {before_stats.get('node_count', 0)}, "
              f"Relationships: {before_stats.get('relationship_count', 0)}")
        
        # Uncomment the line below to actually clear the database
        # result = await neo4j_service.clear_database()
        # print(f"✅ Database cleared. Deleted {result.get('nodes_deleted', 0)} nodes")
        
        print("💡 Cleanup commented out for safety. Uncomment to actually clear database.")
        
    except Exception as e:
        print(f"❌ Error in cleanup example: {e}")
    finally:
        await neo4j_service.close()


if __name__ == "__main__":
    print("🚀 Starting Neo4j Service Examples")
    print("="*50)
    
    # Run examples
    print("\n📘 Running Basic Examples:")
    asyncio.run(basic_example())
    
    print("\n📗 Running Transaction Examples:")
    asyncio.run(transaction_example())
    
    print("\n📙 Running Graph Analytics Examples:")
    asyncio.run(graph_analytics_example())
    
    print("\n📕 Running Repository Pattern Example:")
    asyncio.run(repository_example())
    
    print("\n📓 Running Cleanup Example:")
    asyncio.run(cleanup_example())
    
    print("\n✨ All examples completed!")