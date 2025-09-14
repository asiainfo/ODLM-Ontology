"""
Neo4j Service Class with Async Support

This module provides a comprehensive Neo4j service class that supports 
asynchronous operations with proper session management, transaction handling,
and graph-specific operations.

Best Practices Implemented:
- Async/await patterns for non-blocking operations
- Session and transaction management
- Comprehensive error handling and logging
- Type hints for better code maintainability
- Graph-specific query helpers
- Connection pooling via Neo4j driver
"""

import neo4j
from neo4j import AsyncGraphDatabase, AsyncSession, AsyncTransaction
from neo4j.exceptions import ConstraintError
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Tuple
from contextlib import asynccontextmanager
import traceback
from public.public_variable import logger


class Neo4jService:
    """
    Neo4j Database Service with async support
    
    Features:
    - Async session and transaction management
    - Cypher query execution with parameters
    - Graph-specific operations (nodes, relationships, paths)
    - Comprehensive error handling and logging
    - Connection pooling managed by Neo4j driver
    - Support for complex graph queries and analytics
    """
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
        database: str = "neo4j",
        # Connection pool settings
        max_connection_lifetime: int = 3600,
        max_connection_pool_size: int = 100,
        connection_acquisition_timeout: int = 60,
        # Additional settings
        encrypted: bool = False,
        trust: str = "TRUST_ALL_CERTIFICATES",
        user_agent: str = "odlm-python/neo4j-service",
    ):
        """
        Initialize Neo4j service with connection parameters
        
        Args:
            uri: Neo4j connection URI (bolt://, neo4j://, bolt+s://, neo4j+s://)
            user: Database user
            password: Database password  
            database: Database name (for Neo4j 4.0+)
            max_connection_lifetime: Max lifetime for connections (seconds)
            max_connection_pool_size: Maximum number of connections in pool
            connection_acquisition_timeout: Timeout for acquiring connection
            encrypted: Whether to use encryption
            trust: Trust policy for certificates
            user_agent: User agent string
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        
        # Create the async driver with connection pooling
        try:
            self._driver = AsyncGraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_lifetime=max_connection_lifetime,
                max_connection_pool_size=max_connection_pool_size,
                connection_acquisition_timeout=connection_acquisition_timeout,
                encrypted=encrypted,
                trust=trust,
                user_agent=user_agent
            )
            logger.info(f"Neo4j service initialized for database: {database} at {uri}")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to initialize Neo4j driver: {str(e)}")
    
    @asynccontextmanager
    async def get_session(self, **kwargs) -> AsyncGenerator[AsyncSession, None]:
        """
        Async context manager for getting database sessions
        
        Args:
            **kwargs: Additional session configuration
        
        Usage:
            async with service.get_session() as session:
                result = await session.run("MATCH (n) RETURN n LIMIT 1")
        """
        session = None
        try:
            session = self._driver.session(database=self.database, **kwargs)
            yield session
        except Exception as e:
            logger.error(f"Error with Neo4j session: {str(e)}")
            raise
        finally:
            if session:
                await session.close()
    
    @asynccontextmanager
    async def get_transaction(self, **kwargs) -> AsyncGenerator[AsyncTransaction, None]:
        """
        Async context manager for explicit transactions
        
        Args:
            **kwargs: Additional transaction configuration
            
        Usage:
            async with service.get_transaction() as tx:
                await tx.run("CREATE (n:Person {name: $name})", name="Alice")
                await tx.run("CREATE (n:Person {name: $name})", name="Bob")
                # Auto-commit if no exception, rollback if exception
        """
        async with self.get_session(**kwargs) as session:
            async with session.begin_transaction() as tx:
                try:
                    yield tx
                except Exception as e:
                    logger.error(f"Transaction error, will rollback: {str(e)}")
                    raise
    
    # Basic Query Methods
    
    async def run_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return all results
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            **kwargs: Additional session configuration
            
        Returns:
            List of records as dictionaries
        """
        async with self.get_session(**kwargs) as session:
            try:
                result = await session.run(query, parameters or {})
                records = []
                async for record in result:
                    records.append(dict(record))
                logger.debug(f"Query executed successfully, returned {len(records)} records")
                return records
            except Exception as e:
                logger.error(f"Failed to execute query: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Parameters: {parameters}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to execute query: {str(e)}")
    
    async def run_query_single(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a Cypher query and return a single result
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            **kwargs: Additional session configuration
            
        Returns:
            Single record as dictionary or None
        """
        async with self.get_session(**kwargs) as session:
            try:
                result = await session.run(query, parameters or {})
                record = await result.single()
                if record:
                    logger.debug("Query executed successfully, returned single record")
                    return dict(record)
                logger.debug("Query executed successfully, no records found")
                return None
            except Exception as e:
                logger.error(f"Failed to execute single query: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Parameters: {parameters}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to execute single query: {str(e)}")
    
    async def run_query_value(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        key: str = None,
        **kwargs
    ) -> Any:
        """
        Execute a Cypher query and return a single value
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            key: Specific key to extract from record (if None, returns first value)
            **kwargs: Additional session configuration
            
        Returns:
            Single value from the first record
        """
        record = await self.run_query_single(query, parameters, **kwargs)
        if record:
            if key:
                return record.get(key)
            else:
                # Return first value in the record
                return next(iter(record.values())) if record else None
        return None
    
    async def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a write query (CREATE, UPDATE, DELETE, MERGE)
        
        Args:
            query: Cypher write query
            parameters: Query parameters
            **kwargs: Additional session configuration
            
        Returns:
            Query statistics and results
        """
        async with self.get_session(**kwargs) as session:
            try:
                result = await session.run(query, parameters or {})
                # Consume all results to get statistics
                records = []
                async for record in result:
                    records.append(dict(record))
                
                # Get query statistics by consuming the result
                summary = await result.consume()
                stats = {
                    'records': records,
                    'nodes_created': summary.counters.nodes_created,
                    'nodes_deleted': summary.counters.nodes_deleted,
                    'relationships_created': summary.counters.relationships_created,
                    'relationships_deleted': summary.counters.relationships_deleted,
                    'properties_set': summary.counters.properties_set,
                    'labels_added': summary.counters.labels_added,
                    'labels_removed': summary.counters.labels_removed,
                    'indexes_added': summary.counters.indexes_added,
                    'indexes_removed': summary.counters.indexes_removed,
                    'constraints_added': summary.counters.constraints_added,
                    'constraints_removed': summary.counters.constraints_removed,
                }
                
                logger.debug(f"Write query executed successfully: {stats}")
                return stats
            except ConstraintError as e:
                error_msg = str(e).lower()
                # Handle "already exists" constraint errors gracefully
                if "already exists" in error_msg:
                    logger.warning(f"⚠️  Node/relationship already exists, skipping creation: {str(e)}")
                    return {
                        'records': [],
                        'nodes_created': 0,
                        'nodes_deleted': 0,
                        'relationships_created': 0,
                        'relationships_deleted': 0,
                        'properties_set': 0,
                        'labels_added': 0,
                        'labels_removed': 0,
                        'indexes_added': 0,
                        'indexes_removed': 0,
                        'constraints_added': 0,
                        'constraints_removed': 0,
                        'status': 'already_exists',
                        'warning': f"Item already exists and was skipped: {str(e)}"
                    }
                else:
                    # Re-raise other constraint errors
                    logger.error(f"Constraint error: {str(e)}")
                    logger.error(f"Query: {query}")
                    logger.error(f"Parameters: {parameters}")
                    logger.error(traceback.format_exc())
                    raise Exception(f"Constraint error: {str(e)}")
            except Exception as e:
                logger.error(f"Failed to execute write query: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Parameters: {parameters}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to execute write query: {str(e)}")
    
    # Graph-Specific Operations
    
    async def create_node(
        self,
        label: str,
        properties: Dict[str, Any],
        additional_labels: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a single node with given label and properties
        
        Args:
            label: Primary node label
            properties: Node properties
            additional_labels: Additional labels for the node
            **kwargs: Additional session configuration
            
        Returns:
            Created node information
        """
        labels = [label] + (additional_labels or [])
        labels_str = ":".join(labels)
        
        query = f"CREATE (n:{labels_str} $properties) RETURN n"
        result = await self.execute_write(query, {"properties": properties}, **kwargs)
        
        logger.debug(f"Created node with label {label} and {len(properties)} properties")
        return result
    
    async def create_relationship(
        self,
        from_node_query: str,
        to_node_query: str,
        relationship_type: str,
        properties: Dict[str, Any] = None,
        from_params: Dict[str, Any] = None,
        to_params: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a relationship between two nodes, skipping if relationship already exists
        
        Args:
            from_node_query: Cypher pattern to match the source node
            to_node_query: Cypher pattern to match the target node  
            relationship_type: Type of the relationship
            properties: Relationship properties
            from_params: Parameters for from_node_query
            to_params: Parameters for to_node_query
            **kwargs: Additional session configuration
            
        Returns:
            Relationship creation statistics
        """
        # First check if the relationship already exists
        check_query = f"""
        MATCH (from {from_node_query})
        MATCH (to {to_node_query})
        RETURN EXISTS((from)-[:{relationship_type}]->(to)) as relationship_exists
        """
        
        check_params = {}
        if from_params:
            check_params.update(from_params)
        if to_params:
            check_params.update(to_params)
        
        # Check if relationship already exists
        exists = await self.run_query_value(check_query, check_params, key="relationship_exists", **kwargs)
        
        if exists:
            logger.warning(f"⚠️  Relationship {relationship_type} already exists between nodes, skipping creation")
            return {
                'records': [],
                'nodes_created': 0,
                'nodes_deleted': 0,
                'relationships_created': 0,
                'relationships_deleted': 0,
                'properties_set': 0,
                'labels_added': 0,
                'labels_removed': 0,
                'indexes_added': 0,
                'indexes_removed': 0,
                'constraints_added': 0,
                'constraints_removed': 0,
                'status': 'already_exists',
                'warning': f"Relationship {relationship_type} already exists and was skipped"
            }
        
        # Create the relationship if it doesn't exist
        props_clause = ""
        if properties:
            props_clause = " $rel_props"
        
        query = f"""
        MATCH (from {from_node_query})
        MATCH (to {to_node_query})
        CREATE (from)-[r:{relationship_type}{props_clause}]->(to)
        RETURN r
        """
        
        params = {}
        if from_params:
            params.update(from_params)
        if to_params:
            params.update(to_params)
        if properties:
            params["rel_props"] = properties
        
        result = await self.execute_write(query, params, **kwargs)
        logger.debug(f"Created relationship of type {relationship_type}")
        return result
    
    async def find_nodes(
        self,
        label: str = None,
        properties: Dict[str, Any] = None,
        limit: int = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Find nodes by label and/or properties
        
        Args:
            label: Node label to filter by
            properties: Properties to match
            limit: Maximum number of nodes to return
            **kwargs: Additional session configuration
            
        Returns:
            List of matching nodes
        """
        query_parts = ["MATCH (n"]
        params = {}
        
        if label:
            query_parts.append(f":{label}")
        
        if properties:
            # Build property matching
            prop_conditions = []
            for key, value in properties.items():
                param_name = f"prop_{key}"
                prop_conditions.append(f"{key}: ${param_name}")
                params[param_name] = value
            
            if prop_conditions:
                query_parts.append(" {")
                query_parts.append(", ".join(prop_conditions))
                query_parts.append("}")
        
        query_parts.append(") RETURN n")
        
        if limit:
            query_parts.append(f" LIMIT {limit}")
        
        query = "".join(query_parts)
        return await self.run_query(query, params, **kwargs)
    
    async def find_paths(
        self,
        start_node_query: str,
        end_node_query: str,
        relationship_pattern: str = "*",
        max_depth: int = 5,
        start_params: Dict[str, Any] = None,
        end_params: Dict[str, Any] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Find paths between nodes
        
        Args:
            start_node_query: Cypher pattern for start node
            end_node_query: Cypher pattern for end node
            relationship_pattern: Relationship pattern (e.g., "*", ":KNOWS*", ":KNOWS*1..3")
            max_depth: Maximum path depth
            start_params: Parameters for start node query
            end_params: Parameters for end node query
            **kwargs: Additional session configuration
            
        Returns:
            List of paths with nodes and relationships
        """
        query = f"""
        MATCH (start {start_node_query})
        MATCH (end {end_node_query})
        MATCH path = (start)-[{relationship_pattern}*1..{max_depth}]-(end)
        RETURN path, nodes(path) as nodes, relationships(path) as relationships
        """
        
        params = {}
        if start_params:
            params.update(start_params)
        if end_params:
            params.update(end_params)
        
        return await self.run_query(query, params, **kwargs)
    
    async def get_node_degree(
        self,
        node_query: str,
        direction: str = "BOTH",
        relationship_type: str = None,
        params: Dict[str, Any] = None,
        **kwargs
    ) -> int:
        """
        Get the degree (number of relationships) of a node
        
        Args:
            node_query: Cypher pattern to match the node
            direction: Relationship direction ("INCOMING", "OUTGOING", "BOTH")
            relationship_type: Specific relationship type to count
            params: Parameters for node query
            **kwargs: Additional session configuration
            
        Returns:
            Node degree count
        """
        direction_map = {
            "INCOMING": "<-[r",
            "OUTGOING": "-[r",
            "BOTH": "-[r"
        }
        
        type_filter = f":{relationship_type}" if relationship_type else ""
        direction_prefix = direction_map.get(direction.upper(), "-[r")
        direction_suffix = "]-" if direction.upper() == "INCOMING" else "]->"
        if direction.upper() == "BOTH":
            direction_suffix = "]-"
        
        query = f"""
        MATCH (n {node_query})
        MATCH (n){direction_prefix}{type_filter}{direction_suffix}()
        RETURN count(r) as degree
        """
        
        result = await self.run_query_value(query, params or {}, "degree", **kwargs)
        return result or 0
    
    # Utility Methods
    
    async def get_database_info(self, **kwargs) -> Dict[str, Any]:
        """
        Get database information and statistics
        
        Returns:
            Database information including node/relationship counts
        """
        queries = {
            "node_count": "MATCH (n) RETURN count(n) as count",
            "relationship_count": "MATCH ()-[r]->() RETURN count(r) as count",
            "labels": "CALL db.labels() YIELD label RETURN collect(label) as labels",
            "relationship_types": "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types",
            "property_keys": "CALL db.propertyKeys() YIELD propertyKey RETURN collect(propertyKey) as keys"
        }
        
        info = {}
        for key, query in queries.items():
            try:
                if key in ["labels", "relationship_types", "property_keys"]:
                    result = await self.run_query_value(query, **kwargs)
                    info[key] = result or []
                else:
                    info[key] = await self.run_query_value(query, key="count", **kwargs) or 0
            except Exception as e:
                logger.warning(f"Could not get {key}: {str(e)}")
                info[key] = None
        
        return info
    
    async def clear_database(self, **kwargs) -> Dict[str, Any]:
        """
        Clear all nodes and relationships from the database
        WARNING: This will delete ALL data!
        
        Returns:
            Deletion statistics
        """
        logger.warning("Clearing entire Neo4j database - this will delete ALL data!")
        query = "MATCH (n) DETACH DELETE n"
        return await self.execute_write(query, **kwargs)
    
    async def ping(self, **kwargs) -> bool:
        """
        Test database connectivity
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = await self.run_query_value("RETURN 1 as test", **kwargs)
            success = result == 1
            if success:
                logger.info("Neo4j ping successful")
            else:
                logger.warning("Neo4j ping returned unexpected result")
            return success
        except Exception as e:
            logger.error(f"Neo4j ping failed: {str(e)}")
            return False
    
    async def close(self):
        """Close the Neo4j driver and all connections"""
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j driver closed")
    
    def __repr__(self) -> str:
        return f"Neo4jService(uri={self.uri}, database={self.database})"
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    # Static helper methods for handling constraint results
    
    @staticmethod
    def was_skipped_due_to_constraint(result: Dict[str, Any]) -> bool:
        """
        Check if a write operation was skipped due to a constraint violation
        
        Args:
            result: Result dictionary from write operations
            
        Returns:
            True if the operation was skipped due to a constraint, False otherwise
        """
        return result.get('status') == 'already_exists'
    
    @staticmethod
    def get_warning_message(result: Dict[str, Any]) -> Optional[str]:
        """
        Get the warning message from a write operation result
        
        Args:
            result: Result dictionary from write operations
            
        Returns:
            Warning message if present, None otherwise
        """
        return result.get('warning')