"""
Example usage of MySQLService class

This file demonstrates best practices for using the MySQLService class
with both async and sync methods.
"""

import asyncio
from mysql_service import MySQLService


async def async_example():
    """Example of async database operations"""
    
    # Initialize the service
    mysql_service = MySQLService(
        host="localhost",
        port=3306,
        user="your_username",
        password="your_password",
        database="your_database",
        minsize=1,
        maxsize=10
    )
    
    try:
        # Test connectivity
        if await mysql_service.aping():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return
        
        # Example 1: Create a table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        await mysql_service.aexecute(create_table_query)
        print("✅ Table created successfully")
        
        # Example 2: Insert data using parameterized queries
        insert_query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        affected_rows = await mysql_service.aexecute(
            insert_query, 
            ("John Doe", "john@example.com")
        )
        print(f"✅ Inserted {affected_rows} row(s)")
        
        # Example 3: Insert multiple records
        insert_many_query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        users_data = [
            ("Alice Smith", "alice@example.com"),
            ("Bob Johnson", "bob@example.com"),
            ("Carol Williams", "carol@example.com")
        ]
        total_rows = await mysql_service.aexecute_many(insert_many_query, users_data)
        print(f"✅ Inserted {total_rows} row(s) with execute_many")
        
        # Example 4: Fetch single record
        user = await mysql_service.afetch_one(
            "SELECT * FROM users WHERE email = %s", 
            ("john@example.com",)
        )
        if user:
            print(f"✅ Found user: {user['name']} ({user['email']})")
        
        # Example 5: Fetch all records
        all_users = await mysql_service.afetch_all("SELECT * FROM users ORDER BY id")
        print(f"✅ Found {len(all_users)} total users")
        for user in all_users:
            print(f"  - {user['name']} ({user['email']})")
        
        # Example 6: Fetch limited records
        recent_users = await mysql_service.afetch_many(
            "SELECT * FROM users ORDER BY created_at DESC", 
            size=2
        )
        print(f"✅ Found {len(recent_users)} recent users")
        
        # Example 7: Update with parameters
        update_query = "UPDATE users SET name = %s WHERE email = %s"
        updated_rows = await mysql_service.aexecute(
            update_query, 
            ("John Smith", "john@example.com")
        )
        print(f"✅ Updated {updated_rows} row(s)")
        
        # Example 8: Transaction example
        async with mysql_service.atransaction() as conn:
            async with conn.cursor() as cursor:
                # Multiple operations in a transaction
                await cursor.execute(
                    "UPDATE users SET name = %s WHERE id = %s", 
                    ("Updated Name", 1)
                )
                await cursor.execute(
                    "INSERT INTO users (name, email) VALUES (%s, %s)", 
                    ("Transaction User", "transaction@example.com")
                )
                print("✅ Transaction completed successfully")
        
        # Example 9: Error handling example
        try:
            # This will fail due to duplicate email (UNIQUE constraint)
            await mysql_service.aexecute(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                ("Duplicate", "john@example.com")
            )
        except Exception as e:
            print(f"⚠️  Expected error caught: {e}")
        
        print("\n" + "="*50)
        print("🎉 All async examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in async example: {e}")
    finally:
        # Clean up connection pool
        await mysql_service.aclose()


def sync_example():
    """Example of sync database operations"""
    
    # Initialize the service
    mysql_service = MySQLService(
        host="localhost",
        port=3306,
        user="your_username",
        password="your_password",
        database="your_database"
    )
    
    try:
        # Test connectivity
        if mysql_service.ping():
            print("✅ Sync database connection successful")
        else:
            print("❌ Sync database connection failed")
            return
        
        # Example 1: Fetch data synchronously
        users = mysql_service.fetch_all("SELECT * FROM users LIMIT 3")
        print(f"✅ Sync: Found {len(users)} users")
        
        # Example 2: Insert with sync method
        affected = mysql_service.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            ("Sync User", "sync@example.com")
        )
        print(f"✅ Sync: Inserted {affected} row(s)")
        
        # Example 3: Sync transaction
        with mysql_service.transaction() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET name = %s WHERE email = %s",
                    ("Updated Sync User", "sync@example.com")
                )
                print("✅ Sync transaction completed")
        
        print("\n" + "="*50)
        print("🎉 All sync examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in sync example: {e}")


class MySQLRepository:
    """
    Example of a repository pattern using MySQLService
    
    This shows how to build higher-level abstractions on top of MySQLService
    """
    
    def __init__(self, mysql_service: MySQLService):
        self.db = mysql_service
    
    async def create_user(self, name: str, email: str) -> int:
        """Create a new user and return the ID"""
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        await self.db.aexecute(query, (name, email))
        
        # Get the last inserted ID
        result = await self.db.afetch_one("SELECT LAST_INSERT_ID() as id")
        return result['id']
    
    async def get_user_by_email(self, email: str) -> dict:
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        return await self.db.afetch_one(query, (email,))
    
    async def get_all_users(self) -> list:
        """Get all users"""
        return await self.db.afetch_all("SELECT * FROM users ORDER BY created_at DESC")
    
    async def update_user(self, user_id: int, name: str = None, email: str = None) -> int:
        """Update user information"""
        updates = []
        params = []
        
        if name:
            updates.append("name = %s")
            params.append(name)
        
        if email:
            updates.append("email = %s")
            params.append(email)
        
        if not updates:
            return 0
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        return await self.db.aexecute(query, params)
    
    async def delete_user(self, user_id: int) -> int:
        """Delete user by ID"""
        query = "DELETE FROM users WHERE id = %s"
        return await self.db.aexecute(query, (user_id,))


async def repository_example():
    """Example using the repository pattern"""
    mysql_service = MySQLService(
        host="localhost",
        port=3306,
        user="your_username",
        password="your_password",
        database="your_database"
    )
    
    try:
        repo = MySQLRepository(mysql_service)
        
        # Create user
        user_id = await repo.create_user("Repository User", "repo@example.com")
        print(f"✅ Created user with ID: {user_id}")
        
        # Get user
        user = await repo.get_user_by_email("repo@example.com")
        print(f"✅ Retrieved user: {user['name']}")
        
        # Update user
        updated = await repo.update_user(user_id, name="Updated Repository User")
        print(f"✅ Updated {updated} user(s)")
        
        # Get all users
        all_users = await repo.get_all_users()
        print(f"✅ Total users in database: {len(all_users)}")
        
    except Exception as e:
        print(f"❌ Repository example error: {e}")
    finally:
        await mysql_service.aclose()


if __name__ == "__main__":
    print("🚀 Starting MySQL Service Examples")
    print("="*50)
    
    # Run async examples
    print("\n📘 Running Async Examples:")
    asyncio.run(async_example())
    
    # Run sync examples
    print("\n📗 Running Sync Examples:")
    sync_example()
    
    # Run repository pattern example
    print("\n📙 Running Repository Pattern Example:")
    asyncio.run(repository_example())
    
    print("\n✨ All examples completed!")