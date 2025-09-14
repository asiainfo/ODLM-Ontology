"""
Database Utilities Package

This package provides unified access to all database services with
configuration-driven initialization.
"""

from .service_factory import (
    DatabaseServiceFactory,
    get_database_factory,
    create_mysql_service,
    create_neo4j_service,
    create_postgres_service,
    create_qdrant_service,
    create_all_database_services,
    test_database_connections
)

# Import individual services for direct use
from .mysql import MySQLService
from .neo4j import Neo4jService
from .postgres import PostgresORMService
from .qdrant.qdrant import QdrantService

__all__ = [
    # Factory functions
    'DatabaseServiceFactory',
    'get_database_factory',
    'create_mysql_service',
    'create_neo4j_service',
    'create_postgres_service',
    'create_qdrant_service',
    'create_all_database_services',
    'test_database_connections',
    # Service classes
    'MySQLService',
    'Neo4jService',
    'PostgresORMService',
    'QdrantService',
]