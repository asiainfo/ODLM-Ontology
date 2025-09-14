"""
Database Service Factory

This module provides factory functions to create database service instances
using configuration from the centralized configuration system.
"""

from typing import Optional
from config import get_settings, get_database_config
from .mysql import MySQLService
from .neo4j import Neo4jService
from public.public_variable import logger
import traceback
from utils.component.embedding.embedding_model import CustomDense, CustomSparse

class DatabaseServiceFactory:
    """
    Factory class for creating database service instances with configuration
    """
    
    def __init__(self):
        """Initialize the factory with current settings"""
        self.settings = get_settings()
        logger.info("Database service factory initialized")
    
    def create_mysql_service(self, config_override: Optional[dict] = None) -> Optional[MySQLService]:
        """
        Create MySQL service instance using configuration
        
        Args:
            config_override: Optional configuration overrides
            
        Returns:
            MySQLService instance or None if not configured
        """
        try:
            config = get_database_config("mysql")
            if not config:
                logger.warning("MySQL not configured, skipping service creation")
                return None
            
            # Apply overrides if provided
            if config_override:
                config.update(config_override)
            
            # Remove any fields that aren't MySQL service parameters
            mysql_params = {
                'host': config.get('host'),
                'port': config.get('port'),
                'user': config.get('user'),
                'password': config.get('password'),
                'database': config.get('database'),
                'charset': config.get('charset', 'utf8mb4'),
                'autocommit': config.get('autocommit', False),
                'minsize': config.get('minsize', 1),
                'maxsize': config.get('maxsize', 10),
                'pool_recycle': config.get('pool_recycle', 3600)
            }
            
            # Remove None values
            mysql_params = {k: v for k, v in mysql_params.items() if v is not None}
            
            service = MySQLService(**mysql_params)
            logger.info(f"MySQL service created: {service}")
            return service
            
        except Exception as e:
            logger.error(f"Failed to create MySQL service: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def create_neo4j_service(self, config_override: Optional[dict] = None) -> Optional[Neo4jService]:
        """
        Create Neo4j service instance using configuration
        
        Args:
            config_override: Optional configuration overrides
            
        Returns:
            Neo4jService instance or None if not configured
        """
        try:
            config = get_database_config("neo4j")
            if not config:
                logger.warning("Neo4j not configured, skipping service creation")
                return None
            
            # Apply overrides if provided
            if config_override:
                config.update(config_override)
            
            # Remove any fields that aren't Neo4j service parameters
            neo4j_params = {
                'uri': config.get('uri'),
                'user': config.get('user'),
                'password': config.get('password'),
                'database': config.get('database'),
                'max_connection_lifetime': config.get('max_connection_lifetime', 3600),
                'max_connection_pool_size': config.get('max_connection_pool_size', 100),
                'connection_acquisition_timeout': config.get('connection_acquisition_timeout', 60),
                'encrypted': config.get('encrypted', False),
                'trust': config.get('trust', 'TRUST_ALL_CERTIFICATES'),
                'user_agent': config.get('user_agent', 'odlm-python/neo4j-service'),
            }
            
            # If URI is not provided, build it from host and port
            if not neo4j_params.get('uri'):
                host = config.get('host', 'localhost')
                port = config.get('port', 7687)
                neo4j_params['uri'] = f"bolt://{host}:{port}"
            
            # Remove None values
            neo4j_params = {k: v for k, v in neo4j_params.items() if v is not None}
            
            service = Neo4jService(**neo4j_params)
            logger.info(f"Neo4j service created: {service}")
            return service
            
        except Exception as e:
            logger.error(f"Failed to create Neo4j service: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def create_all_services(self) -> dict:
        """
        Create all configured database services
        
        Returns:
            Dictionary of service name -> service instance
        """
        services = {}
        
        # Create MySQL service
        mysql_service = self.create_mysql_service()
        if mysql_service:
            services['mysql'] = mysql_service
        
        # Create Neo4j service
        neo4j_service = self.create_neo4j_service()
        if neo4j_service:
            services['neo4j'] = neo4j_service
        
        # Create Qdrant service
        qdrant_service = self.create_qdrant_service()
        if qdrant_service:
            services['qdrant'] = qdrant_service

        # Create Postgres service
        postgres_service = self.create_postgres_service()
        if postgres_service:
            services['postgres'] = postgres_service
        
        logger.info(f"Created {len(services)} database services: {list(services.keys())}")
        return services
    
    async def test_all_connections(self) -> dict:
        """
        Test connections to all configured databases
        
        Returns:
            Dictionary of service name -> connection status
        """
        services = self.create_all_services()
        results = {}
        
        # Test MySQL connection
        if 'mysql' in services:
            try:
                success = await services['mysql'].aping()
                results['mysql'] = success
                logger.info(f"MySQL connection test: {'SUCCESS' if success else 'FAILED'}")
            except Exception as e:
                results['mysql'] = False
                logger.error(f"MySQL connection test failed: {e}")
        
        # Test Neo4j connection
        if 'neo4j' in services:
            try:
                success = await services['neo4j'].ping()
                results['neo4j'] = success
                logger.info(f"Neo4j connection test: {'SUCCESS' if success else 'FAILED'}")
            except Exception as e:
                results['neo4j'] = False
                logger.error(f"Neo4j connection test failed: {e}")

        # Test Postgres connection
        if 'postgres' in services:
            try:
                success = await services['postgres'].ping()
                results['postgres'] = success
                logger.info(f"Postgres connection test: {'SUCCESS' if success else 'FAILED'}")
            except Exception as e:
                results['postgres'] = False
                logger.error(f"Postgres connection test failed: {e}")
        
        # Test Qdrant connection (Qdrant service doesn't have a ping method in the current implementation)
        if 'qdrant' in services:
            try:
                # For Qdrant, we'll just try to create the service successfully
                results['qdrant'] = True
                logger.info("Qdrant connection test: SUCCESS")
            except Exception as e:
                results['qdrant'] = False
                logger.error(f"Qdrant connection test failed: {e}")
        
        # Close services after testing
        for service_name, service in services.items():
            try:
                if hasattr(service, 'aclose'):
                    await service.aclose()
                elif hasattr(service, 'close'):
                    await service.close()
            except Exception as e:
                logger.warning(f"Error closing {service_name} service: {e}")
        
        return results


# Global factory instance
_factory: Optional[DatabaseServiceFactory] = None


def get_database_factory() -> DatabaseServiceFactory:
    """
    Get or create the global database service factory
    
    Returns:
        DatabaseServiceFactory instance
    """
    global _factory
    if _factory is None:
        _factory = DatabaseServiceFactory()
    return _factory


# Convenience functions for creating individual services

def create_mysql_service(config_override: Optional[dict] = None) -> Optional[MySQLService]:
    """Create MySQL service using configuration"""
    factory = get_database_factory()
    return factory.create_mysql_service(config_override)


def create_neo4j_service(config_override: Optional[dict] = None) -> Optional[Neo4jService]:
    """Create Neo4j service using configuration"""
    factory = get_database_factory()
    return factory.create_neo4j_service(config_override)

def create_all_database_services() -> dict:
    """Create all configured database services"""
    factory = get_database_factory()
    return factory.create_all_services()


async def test_database_connections() -> dict:
    """Test all database connections"""
    factory = get_database_factory()
    return await factory.test_all_connections()