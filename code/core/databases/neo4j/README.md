# Neo4j Service Class

A comprehensive, async-first Neo4j service class that provides session management, transaction handling, and graph-specific operations following Python best practices.

## Features

- ✅ **Async/Await Support**: Built for modern Python async applications using Neo4j's async driver
- ✅ **Session Management**: Automatic session lifecycle management with context managers
- ✅ **Transaction Support**: Explicit transaction control with automatic rollback
- ✅ **Graph Operations**: High-level methods for nodes, relationships, and path operations
- ✅ **Type Hints**: Full type annotation support
- ✅ **Error Handling**: Comprehensive error handling with logging
- ✅ **Cypher Query Support**: Full Cypher query capabilities with parameterization
- ✅ **Connection Pooling**: Managed by Neo4j driver for optimal performance
- ✅ **Graph Analytics**: Built-in methods for common graph analysis patterns

## Installation

Add the required dependency to your `pyproject.toml`:

```toml
neo4j = "^5.25.0"
```

Then install:

```bash
poetry install
```

## Quick Start

### Basic Usage

```python
from utils.databases.neo4j import Neo4jService
import asyncio

async def main():
    # Initialize the service
    neo4j_service = Neo4jService(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password",
        database="neo4j"
    )
    
    # Test connection
    if await neo4j_service.ping():
        print("Connected successfully!")
    
    # Create a node
    await neo4j_service.create_node(
        "Person",
        {"name": "John Doe", "age": 30}
    )
    
    # Query nodes
    people = await neo4j_service.find_nodes("Person")
    print(f"Found {len(people)} people")
    
    # Run custom Cypher query
    result = await neo4j_service.run_query(
        "MATCH (p:Person {name: $name}) RETURN p",
        {"name": "John Doe"}
    )
    
    # Clean up
    await neo4j_service.close()

asyncio.run(main())
```

## API Reference

### Initialization

```python
neo4j_service = Neo4jService(
    uri="bolt://localhost:7687",        # Neo4j connection URI
    user="neo4j",                       # Database user
    password="password",                # Database password
    database="neo4j",                   # Database name (Neo4j 4.0+)
    max_connection_lifetime=3600,       # Connection lifetime (seconds)
    max_connection_pool_size=100,       # Max connections in pool
    connection_acquisition_timeout=60,  # Connection timeout
    encrypted=False,                    # Use encryption
    trust="TRUST_ALL_CERTIFICATES",     # Trust policy
    user_agent="odlm-python/neo4j-service"  # User agent
)
```

### Core Query Methods

#### Basic Queries

```python
# Execute query and return all results
results = await neo4j_service.run_query(
    "MATCH (p:Person) WHERE p.age > $age RETURN p",
    {"age": 25}
)

# Execute query and return single result
person = await neo4j_service.run_query_single(
    "MATCH (p:Person {name: $name}) RETURN p",
    {"name": "John"}
)

# Execute query and return single value
count = await neo4j_service.run_query_value(
    "MATCH (p:Person) RETURN count(p) as total",
    key="total"
)

# Execute write query with statistics
stats = await neo4j_service.execute_write(
    "CREATE (p:Person {name: $name}) RETURN p",
    {"name": "Jane"}
)
print(f"Created {stats['nodes_created']} nodes")
```

### Graph-Specific Operations

#### Node Operations

```python
# Create a node
await neo4j_service.create_node(
    "Person",
    {"name": "Alice", "age": 30, "city": "NYC"},
    additional_labels=["Employee", "Developer"]
)

# Find nodes by label and properties
people = await neo4j_service.find_nodes(
    "Person",
    {"city": "NYC"},
    limit=10
)

# Get node degree (number of connections)
degree = await neo4j_service.get_node_degree(
    ":Person {name: 'Alice'}",
    direction="BOTH",
    relationship_type="KNOWS"
)
```

#### Relationship Operations

```python
# Create relationship between nodes
await neo4j_service.create_relationship(
    ":Person {name: 'Alice'}",        # From node pattern
    ":Person {name: 'Bob'}",          # To node pattern
    "KNOWS",                          # Relationship type
    {"since": 2020, "strength": 0.8}, # Properties
    from_params={"name": "Alice"},    # Parameters for from pattern
    to_params={"name": "Bob"}         # Parameters for to pattern
)
```

#### Path Operations

```python
# Find paths between nodes
paths = await neo4j_service.find_paths(
    ":Person {name: 'Alice'}",     # Start node
    ":Person {name: 'Charlie'}",   # End node
    relationship_pattern=":KNOWS*", # Relationship pattern
    max_depth=3                    # Maximum path length
)

# Analyze path results
for path in paths:
    nodes = path['nodes']
    relationships = path['relationships']
    print(f"Path length: {len(relationships)}")
```

### Session and Transaction Management

#### Session Management

```python
# Manual session management
async with neo4j_service.get_session() as session:
    result = await session.run(
        "MATCH (n) RETURN count(n) as total"
    )
    record = await result.single()
    print(f"Total nodes: {record['total']}")
```

#### Transaction Management

```python
# Explicit transactions
async with neo4j_service.get_transaction() as tx:
    # Multiple operations in one transaction
    await tx.run("CREATE (p:Person {name: 'Alice'})")
    await tx.run("CREATE (p:Person {name: 'Bob'})")
    await tx.run(
        "MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'}) "
        "CREATE (a)-[:KNOWS]->(b)"
    )
    # Auto-commit if no exception, rollback if exception
```

### Utility Methods

```python
# Test connectivity
is_connected = await neo4j_service.ping()

# Get database information
db_info = await neo4j_service.get_database_info()
print(f"Nodes: {db_info['node_count']}")
print(f"Relationships: {db_info['relationship_count']}")
print(f"Labels: {db_info['labels']}")

# Clear database (WARNING: deletes all data!)
stats = await neo4j_service.clear_database()

# Close driver
await neo4j_service.close()
```

## Advanced Usage

### Repository Pattern

```python
class PersonRepository:
    def __init__(self, neo4j_service: Neo4jService):
        self.graph = neo4j_service
    
    async def create_person(self, name: str, age: int, **attrs):
        properties = {"name": name, "age": age, **attrs}
        return await self.graph.create_node("Person", properties)
    
    async def get_friends(self, person_name: str):
        query = """
        MATCH (p:Person {name: $name})-[:FRIENDS_WITH]-(friend)
        RETURN friend.name as name, friend.age as age
        """
        return await self.graph.run_query(query, {"name": person_name})
    
    async def suggest_friends(self, person_name: str, limit: int = 5):
        query = """
        MATCH (p:Person {name: $name})-[:FRIENDS_WITH]-(friend)-[:FRIENDS_WITH]-(suggestion)
        WHERE NOT (p)-[:FRIENDS_WITH]-(suggestion) AND p <> suggestion
        RETURN suggestion.name as name, count(friend) as mutual_friends
        ORDER BY mutual_friends DESC LIMIT $limit
        """
        return await self.graph.run_query(
            query, 
            {"name": person_name, "limit": limit}
        )
```

### Configuration from Environment

```python
import os

neo4j_service = Neo4jService(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    user=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password"),
    database=os.getenv("NEO4J_DATABASE", "neo4j"),
    max_connection_pool_size=int(os.getenv("NEO4J_POOL_SIZE", "100"))
)
```

### Graph Analytics Examples

```python
# Find most connected nodes
query = """
MATCH (n)-[r]-()
RETURN labels(n) as labels, n.name as name, count(r) as degree
ORDER BY degree DESC
LIMIT 10
"""
most_connected = await neo4j_service.run_query(query)

# Find communities (nodes with many mutual connections)
query = """
MATCH (a)-[:KNOWS]-(b)-[:KNOWS]-(c)-[:KNOWS]-(a)
WHERE id(a) < id(b) AND id(b) < id(c)
RETURN a.name, b.name, c.name
"""
triangles = await neo4j_service.run_query(query)

# Calculate centrality measures
query = """
CALL gds.pageRank.stream('myGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name as name, score
ORDER BY score DESC
"""
centrality = await neo4j_service.run_query(query)
```

## Integration with FastAPI

```python
from fastapi import FastAPI, Depends
from utils.databases.neo4j import Neo4jService

app = FastAPI()

# Global instance
neo4j_service = Neo4jService(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j"
)

# Dependency injection
async def get_graph():
    return neo4j_service

@app.get("/persons/{person_name}")
async def get_person(
    person_name: str, 
    graph: Neo4jService = Depends(get_graph)
):
    person = await graph.run_query_single(
        "MATCH (p:Person {name: $name}) RETURN p",
        {"name": person_name}
    )
    return person

@app.get("/persons/{person_name}/friends")
async def get_friends(
    person_name: str,
    graph: Neo4jService = Depends(get_graph)
):
    friends = await graph.run_query(
        """
        MATCH (p:Person {name: $name})-[:KNOWS]-(friend:Person)
        RETURN friend.name as name, friend.age as age
        """,
        {"name": person_name}
    )
    return friends

@app.on_event("shutdown")
async def shutdown():
    await neo4j_service.close()
```

## Common Graph Patterns

### Social Network

```python
# Create social network
await neo4j_service.create_node("Person", {"name": "Alice", "age": 30})
await neo4j_service.create_node("Person", {"name": "Bob", "age": 25})

# Create friendship
await neo4j_service.create_relationship(
    ":Person {name: 'Alice'}",
    ":Person {name: 'Bob'}",
    "FRIENDS_WITH",
    {"since": 2020}
)

# Find mutual friends
mutual_friends = await neo4j_service.run_query("""
    MATCH (a:Person {name: $person1})-[:FRIENDS_WITH]-(mutual)-[:FRIENDS_WITH]-(b:Person {name: $person2})
    RETURN mutual.name as name
""", {"person1": "Alice", "person2": "Charlie"})
```

### Knowledge Graph

```python
# Create entities and relationships
await neo4j_service.create_node("Concept", {"name": "Machine Learning"})
await neo4j_service.create_node("Concept", {"name": "Neural Networks"})
await neo4j_service.create_node("Person", {"name": "Geoffrey Hinton"})

# Create relationships
await neo4j_service.create_relationship(
    ":Concept {name: 'Neural Networks'}",
    ":Concept {name: 'Machine Learning'}",
    "IS_SUBFIELD_OF"
)

await neo4j_service.create_relationship(
    ":Person {name: 'Geoffrey Hinton'}",
    ":Concept {name: 'Neural Networks'}",
    "CONTRIBUTED_TO"
)
```

### Recommendation Engine

```python
# Find similar users based on shared interests
recommendations = await neo4j_service.run_query("""
    MATCH (user:Person {name: $user_name})-[:LIKES]->(item)<-[:LIKES]-(similar_user)
    MATCH (similar_user)-[:LIKES]->(recommendation)
    WHERE NOT (user)-[:LIKES]->(recommendation)
    RETURN recommendation.name as item, count(*) as score
    ORDER BY score DESC
    LIMIT $limit
""", {"user_name": "Alice", "limit": 10})
```

## Performance Tips

1. **Use Parameters**: Always use parameterized queries for security and performance
2. **Limit Results**: Use `LIMIT` in queries to avoid memory issues
3. **Index Your Data**: Create indexes on frequently queried properties
4. **Connection Pooling**: The driver handles connection pooling automatically
5. **Batch Operations**: Use transactions for multiple related operations
6. **Profile Queries**: Use `PROFILE` or `EXPLAIN` to optimize slow queries

## Best Practices

1. **Resource Management**: Always close the driver when shutting down
2. **Error Handling**: Implement proper error handling around graph operations
3. **Transaction Boundaries**: Use transactions for operations that must be atomic
4. **Query Optimization**: Profile and optimize expensive queries
5. **Data Modeling**: Design your graph model to match your query patterns
6. **Security**: Use parameterized queries to prevent Cypher injection

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check Neo4j service is running and URI is correct
2. **Authentication**: Verify username/password combination
3. **Database Access**: Ensure user has access to the specified database
4. **Memory Issues**: Use `LIMIT` clauses for large result sets
5. **Transaction Timeouts**: Increase timeout for long-running operations

### Performance Monitoring

```python
# Monitor query performance
import time

start_time = time.time()
result = await neo4j_service.run_query("MATCH (n) RETURN count(n)")
execution_time = time.time() - start_time
print(f"Query took {execution_time:.2f} seconds")

# Get query statistics
stats = await neo4j_service.execute_write(
    "CREATE (n:TestNode) RETURN n"
)
print(f"Nodes created: {stats['nodes_created']}")
```

## Examples

See `example_usage.py` for comprehensive examples including:

- Basic CRUD operations
- Transaction management
- Graph analytics queries
- Repository pattern implementation
- Social network modeling
- Path finding algorithms
- Performance optimization techniques

## Context Manager Support

```python
# Use as async context manager
async with Neo4jService(
    uri="bolt://localhost:7687",
    user="neo4j", 
    password="password"
) as graph:
    result = await graph.run_query("MATCH (n) RETURN count(n)")
    # Automatically closes on exit
```