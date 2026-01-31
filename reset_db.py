"""
Script to reset the database by dropping and recreating it.
Run this if migrations are in a corrupted state.
"""
import MySQLdb
from accorix.settings import DATABASES

db_config = DATABASES['default']

try:
    # Connect to MySQL server (without database)
    conn = MySQLdb.connect(
        host=db_config['HOST'],
        user=db_config['USER'],
        password=db_config['PASSWORD'],
        port=int(db_config['PORT'])
    )
    cursor = conn.cursor()
    
    # Drop database if exists
    print(f"Dropping database {db_config['NAME']}...")
    cursor.execute(f"DROP DATABASE IF EXISTS `{db_config['NAME']}`")
    
    # Create database
    print(f"Creating database {db_config['NAME']}...")
    cursor.execute(f"CREATE DATABASE `{db_config['NAME']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Database reset successfully!")
    print("Now run: python manage.py migrate")
    
except Exception as e:
    print(f"Error: {e}")
