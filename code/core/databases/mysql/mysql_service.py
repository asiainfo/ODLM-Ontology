"""
MySQL Service Class with Async Support

This module provides a comprehensive MySQL service class that supports both
synchronous and asynchronous operations with connection pooling, transaction
management, and proper error handling.

Best Practices Implemented:
- Connection pooling for performance
- Async/await patterns for non-blocking operations
- Context managers for automatic resource cleanup
- Comprehensive error handling and logging
- Type hints for better code maintainability
- Transaction support with rollback capabilities
"""

import aiomysql
import pymysql
from typing import Any, Dict, List, Optional, Union, Tuple, AsyncGenerator
from contextlib import asynccontextmanager, contextmanager
import traceback
from public.public_variable import logger


class MySQLService:
    """
    MySQL Database Service with async support
    
    Features:
    - Connection pooling for both sync and async operations
    - Transaction management with automatic rollback
    - Comprehensive error handling and logging
    - Support for parameterized queries to prevent SQL injection
    - Both async and sync methods for flexibility
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "",
        charset: str = "utf8mb4",
        autocommit: bool = False,
        # Connection pool settings
        minsize: int = 1,
        maxsize: int = 10,
        pool_recycle: int = 3600,
    ):
        """
        Initialize MySQL service with connection parameters
        
        Args:
            host: MySQL server host
            port: MySQL server port
            user: Database user
            password: Database password
            database: Database name
            charset: Character encoding
            autocommit: Whether to autocommit transactions
            minsize: Minimum pool size
            maxsize: Maximum pool size
            pool_recycle: Seconds after which a connection is recreated
        """
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'db': database,
            'charset': charset,
            'autocommit': autocommit,
        }
        
        self.pool_config = {
            'minsize': minsize,
            'maxsize': maxsize,
            'pool_recycle': pool_recycle,
        }
        
        self._async_pool: Optional[aiomysql.Pool] = None
        self._sync_pool: Optional[pymysql.Connection] = None
        
        logger.info(f"MySQL service initialized for database: {database} at {host}:{port}")
    
    async def _get_async_pool(self) -> aiomysql.Pool:
        """Get or create async connection pool"""
        if self._async_pool is None or self._async_pool.closed:
            try:
                self._async_pool = await aiomysql.create_pool(
                    **self.config,
                    **self.pool_config
                )
                logger.info("Async MySQL connection pool created successfully")
            except Exception as e:
                logger.error(f"Failed to create async MySQL pool: {str(e)}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to create async MySQL pool: {str(e)}")
        
        return self._async_pool
    
    def _get_sync_connection(self) -> pymysql.Connection:
        """Get sync connection (creates new connection each time for simplicity)"""
        try:
            connection = pymysql.connect(**self.config)
            logger.debug("Sync MySQL connection created successfully")
            return connection
        except Exception as e:
            logger.error(f"Failed to create sync MySQL connection: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create sync MySQL connection: {str(e)}")
    
    @asynccontextmanager
    async def get_async_connection(self) -> AsyncGenerator[aiomysql.Connection, None]:
        """
        Async context manager for getting database connections
        
        Usage:
            async with service.get_async_connection() as conn:
                # Use connection
                pass
        """
        pool = await self._get_async_pool()
        conn = None
        try:
            conn = await pool.acquire()
            yield conn
        except Exception as e:
            if conn:
                await conn.ensure_closed()
            logger.error(f"Error with async connection: {str(e)}")
            raise
        finally:
            if conn and not conn.closed:
                await pool.release(conn)
    
    @contextmanager
    def get_sync_connection(self):
        """
        Sync context manager for getting database connections
        
        Usage:
            with service.get_sync_connection() as conn:
                # Use connection
                pass
        """
        conn = None
        try:
            conn = self._get_sync_connection()
            yield conn
        except Exception as e:
            logger.error(f"Error with sync connection: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    # Async Methods
    
    async def aexecute(
        self, 
        query: str, 
        params: Optional[Union[Dict, List, Tuple]] = None
    ) -> int:
        """
        Execute a query asynchronously (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL query string
            params: Query parameters for parameterized queries
            
        Returns:
            Number of affected rows
        """
        async with self.get_async_connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    affected_rows = await cursor.execute(query, params)
                    await conn.commit()
                    logger.debug(f"Query executed successfully, affected rows: {affected_rows}")
                    return affected_rows
            except Exception as e:
                await conn.rollback()
                logger.error(f"Failed to execute query: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to execute query: {str(e)}")
    
    async def afetch_one(
        self, 
        query: str, 
        params: Optional[Union[Dict, List, Tuple]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row asynchronously
        
        Args:
            query: SQL query string
            params: Query parameters for parameterized queries
            
        Returns:
            Single row as dictionary or None if no results
        """
        async with self.get_async_connection() as conn:
            try:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    result = await cursor.fetchone()
                    logger.debug(f"Fetch one completed, result: {bool(result)}")
                    return result
            except Exception as e:
                logger.error(f"Failed to fetch one: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to fetch one: {str(e)}")
    
    async def afetch_all(
        self, 
        query: str, 
        params: Optional[Union[Dict, List, Tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows asynchronously
        
        Args:
            query: SQL query string
            params: Query parameters for parameterized queries
            
        Returns:
            List of rows as dictionaries
        """
        async with self.get_async_connection() as conn:
            try:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    result = await cursor.fetchall()
                    logger.debug(f"Fetch all completed, rows: {len(result)}")
                    return result
            except Exception as e:
                logger.error(f"Failed to fetch all: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to fetch all: {str(e)}")
    
    async def afetch_many(
        self, 
        query: str, 
        size: int, 
        params: Optional[Union[Dict, List, Tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple rows asynchronously
        
        Args:
            query: SQL query string
            size: Number of rows to fetch
            params: Query parameters for parameterized queries
            
        Returns:
            List of rows as dictionaries
        """
        async with self.get_async_connection() as conn:
            try:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    result = await cursor.fetchmany(size)
                    logger.debug(f"Fetch many completed, rows: {len(result)}")
                    return result
            except Exception as e:
                logger.error(f"Failed to fetch many: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to fetch many: {str(e)}")
    
    async def aexecute_many(
        self, 
        query: str, 
        params_list: List[Union[Dict, List, Tuple]]
    ) -> int:
        """
        Execute a query multiple times with different parameters asynchronously
        
        Args:
            query: SQL query string
            params_list: List of parameters for each execution
            
        Returns:
            Total number of affected rows
        """
        async with self.get_async_connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    affected_rows = await cursor.executemany(query, params_list)
                    await conn.commit()
                    logger.debug(f"Execute many completed, affected rows: {affected_rows}")
                    return affected_rows
            except Exception as e:
                await conn.rollback()
                logger.error(f"Failed to execute many: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Params count: {len(params_list)}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to execute many: {str(e)}")
    
    @asynccontextmanager
    async def atransaction(self):
        """
        Async transaction context manager
        
        Usage:
            async with service.atransaction() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("INSERT ...")
                    await cursor.execute("UPDATE ...")
                # Auto-commit if no exception, rollback if exception
        """
        async with self.get_async_connection() as conn:
            try:
                await conn.begin()
                yield conn
                await conn.commit()
                logger.debug("Transaction committed successfully")
            except Exception as e:
                await conn.rollback()
                logger.error(f"Transaction rolled back due to error: {str(e)}")
                logger.error(traceback.format_exc())
                raise
    
    # Sync Methods (for compatibility)
    
    def execute(
        self, 
        query: str, 
        params: Optional[Union[Dict, List, Tuple]] = None
    ) -> int:
        """
        Execute a query synchronously (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL query string
            params: Query parameters for parameterized queries
            
        Returns:
            Number of affected rows
        """
        with self.get_sync_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    affected_rows = cursor.execute(query, params)
                    conn.commit()
                    logger.debug(f"Sync query executed successfully, affected rows: {affected_rows}")
                    return affected_rows
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to execute sync query: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to execute sync query: {str(e)}")
    
    def fetch_one(
        self, 
        query: str, 
        params: Optional[Union[Dict, List, Tuple]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row synchronously
        
        Args:
            query: SQL query string
            params: Query parameters for parameterized queries
            
        Returns:
            Single row as dictionary or None if no results
        """
        with self.get_sync_connection() as conn:
            try:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    logger.debug(f"Sync fetch one completed, result: {bool(result)}")
                    return result
            except Exception as e:
                logger.error(f"Failed to sync fetch one: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to sync fetch one: {str(e)}")
    
    def fetch_all(
        self, 
        query: str, 
        params: Optional[Union[Dict, List, Tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows synchronously
        
        Args:
            query: SQL query string
            params: Query parameters for parameterized queries
            
        Returns:
            List of rows as dictionaries
        """
        with self.get_sync_connection() as conn:
            try:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchall()
                    logger.debug(f"Sync fetch all completed, rows: {len(result)}")
                    return result
            except Exception as e:
                logger.error(f"Failed to sync fetch all: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                logger.error(traceback.format_exc())
                raise Exception(f"Failed to sync fetch all: {str(e)}")
    
    @contextmanager
    def transaction(self):
        """
        Sync transaction context manager
        
        Usage:
            with service.transaction() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT ...")
                    cursor.execute("UPDATE ...")
                # Auto-commit if no exception, rollback if exception
        """
        with self.get_sync_connection() as conn:
            try:
                conn.begin()
                yield conn
                conn.commit()
                logger.debug("Sync transaction committed successfully")
            except Exception as e:
                conn.rollback()
                logger.error(f"Sync transaction rolled back due to error: {str(e)}")
                logger.error(traceback.format_exc())
                raise
    
    # Utility Methods
    
    async def aclose(self):
        """Close async connection pool"""
        if self._async_pool and not self._async_pool.closed:
            self._async_pool.close()
            await self._async_pool.wait_closed()
            logger.info("Async MySQL connection pool closed")
    
    async def aping(self) -> bool:
        """
        Test async database connectivity
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            async with self.get_async_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    logger.info("Async MySQL ping successful")
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Async MySQL ping failed: {str(e)}")
            return False
    
    def ping(self) -> bool:
        """
        Test sync database connectivity
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_sync_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    logger.info("Sync MySQL ping successful")
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Sync MySQL ping failed: {str(e)}")
            return False
    
    def __repr__(self) -> str:
        return f"MySQLService(host={self.config['host']}, database={self.config['db']})"