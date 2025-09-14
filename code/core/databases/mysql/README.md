# MySQL Service Class

A comprehensive, async-first MySQL service class that provides connection pooling, transaction management, and proper error handling following Python best practices.

## Features

- ✅ **Async/Await Support**: Built for modern Python async applications
- ✅ **Connection Pooling**: Efficient connection management for better performance
- ✅ **Transaction Management**: Automatic rollback on errors
- ✅ **Type Hints**: Full type annotation support
- ✅ **Error Handling**: Comprehensive error handling with logging
- ✅ **SQL Injection Protection**: Parameterized queries support
- ✅ **Sync Compatibility**: Both async and sync methods available
- ✅ **Context Managers**: Automatic resource cleanup
- ✅ **Logging Integration**: Uses project's loguru logger

## Installation

Add the required dependencies to your `pyproject.toml`:

```toml
aiomysql = "^0.2.0"
pymysql = "^1.1.0"
```

Then install:

```bash
poetry install
```

## Quick Start

### Basic Usage

```python
from utils.databases.mysql import MySQLService
import asyncio

async def main():
    # Initialize the service
    mysql_service = MySQLService(
        host="localhost",
        port=3306,
        user="your_username",
        password="your_password",
        database="your_database",
        minsize=1,  # Min pool size
        maxsize=10  # Max pool size
    )
    
    # Test connection
    if await mysql_service.aping():
        print("Connected successfully!")
    
    # Execute a query
    await mysql_service.aexecute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        ("John Doe", "john@example.com")
    )
    
    # Fetch data
    user = await mysql_service.afetch_one(
        "SELECT * FROM users WHERE email = %s",
        ("john@example.com",)
    )
    
    # Clean up
    await mysql_service.aclose()

asyncio.run(main())
```

## API Reference

### Initialization

```python
mysql_service = MySQLService(
    host="localhost",          # MySQL server host
    port=3306,                # MySQL server port
    user="root",              # Database user
    password="",              # Database password
    database="",              # Database name
    charset="utf8mb4",        # Character encoding
    autocommit=False,         # Auto-commit transactions
    minsize=1,                # Minimum pool size
    maxsize=10,               # Maximum pool size
    pool_recycle=3600,        # Connection recycle time (seconds)
    connect_timeout=10,       # Connection timeout
    read_timeout=30,          # Read timeout
    write_timeout=30,         # Write timeout
)
```

### Async Methods

#### Execute Operations

```python
# Insert/Update/Delete queries
affected_rows = await mysql_service.aexecute(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    ("John Doe", "john@example.com")
)

# Execute multiple queries with different parameters
total_rows = await mysql_service.aexecute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    [("User1", "user1@example.com"), ("User2", "user2@example.com")]
)
```

#### Fetch Operations

```python
# Fetch single row
user = await mysql_service.afetch_one(
    "SELECT * FROM users WHERE id = %s",
    (1,)
)

# Fetch all rows
users = await mysql_service.afetch_all("SELECT * FROM users")

# Fetch limited rows
recent_users = await mysql_service.afetch_many(
    "SELECT * FROM users ORDER BY created_at DESC",
    size=10
)
```

#### Transactions

```python
# Automatic transaction management
async with mysql_service.atransaction() as conn:
    async with conn.cursor() as cursor:
        await cursor.execute("INSERT INTO users ...")
        await cursor.execute("UPDATE profiles ...")
        # Auto-commit if no exception, rollback if exception occurs
```

### Sync Methods

All async methods have sync equivalents without the 'a' prefix:

```python
# Sync operations
users = mysql_service.fetch_all("SELECT * FROM users")
affected = mysql_service.execute("INSERT INTO users ...")

# Sync transactions
with mysql_service.transaction() as conn:
    with conn.cursor() as cursor:
        cursor.execute("INSERT ...")
```

### Utility Methods

```python
# Test connectivity
is_connected = await mysql_service.aping()  # Async
is_connected = mysql_service.ping()         # Sync

# Close connection pool
await mysql_service.aclose()
```

## Advanced Usage

### Repository Pattern

```python
class UserRepository:
    def __init__(self, mysql_service: MySQLService):
        self.db = mysql_service
    
    async def create_user(self, name: str, email: str) -> int:
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        await self.db.aexecute(query, (name, email))
        
        result = await self.db.afetch_one("SELECT LAST_INSERT_ID() as id")
        return result['id']
    
    async def get_user_by_email(self, email: str) -> dict:
        query = "SELECT * FROM users WHERE email = %s"
        return await self.db.afetch_one(query, (email,))
```

### Configuration from Environment

```python
import os

mysql_service = MySQLService(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DATABASE", ""),
    maxsize=int(os.getenv("MYSQL_POOL_SIZE", "10"))
)
```

### Error Handling

```python
try:
    await mysql_service.aexecute("INSERT INTO users ...")
except Exception as e:
    # All database errors are caught and re-raised with context
    logger.error(f"Database operation failed: {e}")
```

## Best Practices

1. **Use Parameterized Queries**: Always use parameterized queries to prevent SQL injection
2. **Connection Pooling**: Use connection pooling for better performance in production
3. **Transaction Management**: Use transactions for operations that need to be atomic
4. **Resource Cleanup**: Always call `aclose()` when shutting down your application
5. **Error Handling**: Implement proper error handling around database operations
6. **Logging**: The service logs operations automatically using the project's logger

## Examples

See `example_usage.py` for comprehensive examples including:
- Basic CRUD operations
- Transaction handling
- Repository pattern implementation
- Error handling examples
- Both async and sync usage patterns

## Integration with FastAPI

```python
from fastapi import FastAPI, Depends
from utils.databases.mysql import MySQLService

app = FastAPI()

# Create a global instance
mysql_service = MySQLService(
    host="localhost",
    user="your_user",
    password="your_password",
    database="your_db"
)

# Dependency injection
async def get_db():
    return mysql_service

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: MySQLService = Depends(get_db)):
    user = await db.afetch_one(
        "SELECT * FROM users WHERE id = %s",
        (user_id,)
    )
    return user

@app.on_event("shutdown")
async def shutdown():
    await mysql_service.aclose()
```

## Performance Tips

1. **Connection Pool Size**: Set `maxsize` based on your concurrent load
2. **Connection Recycling**: Use `pool_recycle` to avoid connection timeouts
3. **Batch Operations**: Use `aexecute_many` for bulk operations
4. **Fetch Limits**: Use `afetch_many` instead of `afetch_all` for large datasets
5. **Indexes**: Ensure proper database indexes for your queries

## Troubleshooting

### Common Issues

1. **Connection Timeout**: Increase `connect_timeout` if connecting to a slow server
2. **Pool Exhaustion**: Increase `maxsize` if you have high concurrency
3. **Memory Usage**: Use `afetch_many` with pagination for large result sets
4. **Charset Issues**: Use `utf8mb4` charset for full Unicode support

### Logging

The service uses the project's loguru logger. Set log levels appropriately:

```python
from public.public_variable import logger
logger.add("mysql.log", level="DEBUG")  # For detailed debugging
```