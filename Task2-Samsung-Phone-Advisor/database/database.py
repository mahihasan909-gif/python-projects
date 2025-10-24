"""
Database module for Samsung Phone Advisor
Handles PostgreSQL operations
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import os
import logging
from typing import List, Dict, Optional, Any
import json

logger = logging.getLogger(__name__)


class SamsungPhoneDatabase:
    """Handles all database operations for Samsung phone data."""
    
    def __init__(self, db_config=None):
        """Initialize database connection."""
        if db_config is None:
            # Default configuration - update these with your actual database credentials
            self.db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'database': os.getenv('DB_NAME', 'samsung_phones'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'password'),
                'port': os.getenv('DB_PORT', '5432')
            }
        else:
            self.db_config = db_config
        
        self.connection = None
        
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def create_tables(self):
        """Create the phones table if it doesn't exist."""
        if not self.connection:
            if not self.connect():
                return False
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS samsung_phones (
            id SERIAL PRIMARY KEY,
            model_name VARCHAR(255) NOT NULL UNIQUE,
            release_date VARCHAR(100),
            display TEXT,
            battery VARCHAR(100),
            camera TEXT,
            ram VARCHAR(100),
            storage VARCHAR(200),
            price VARCHAR(100),
            url TEXT,
            additional_specs JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_model_name ON samsung_phones(model_name);
        CREATE INDEX IF NOT EXISTS idx_price ON samsung_phones(price);
        CREATE INDEX IF NOT EXISTS idx_specs ON samsung_phones USING GIN(additional_specs);
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            logger.info("Tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def insert_phone_data(self, phone_data: Dict[str, Any]):
        """Insert a single phone record."""
        if not self.connection:
            if not self.connect():
                return False
        
        insert_query = """
        INSERT INTO samsung_phones 
        (model_name, release_date, display, battery, camera, ram, storage, price, url, additional_specs)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (model_name) 
        DO UPDATE SET 
            release_date = EXCLUDED.release_date,
            display = EXCLUDED.display,
            battery = EXCLUDED.battery,
            camera = EXCLUDED.camera,
            ram = EXCLUDED.ram,
            storage = EXCLUDED.storage,
            price = EXCLUDED.price,
            url = EXCLUDED.url,
            additional_specs = EXCLUDED.additional_specs,
            updated_at = CURRENT_TIMESTAMP
        """
        
        try:
            cursor = self.connection.cursor()
            
            # Prepare additional specs as JSON
            additional_specs = {
                k: v for k, v in phone_data.items() 
                if k not in ['model_name', 'release_date', 'display', 'battery', 
                           'camera', 'ram', 'storage', 'price', 'url']
            }
            
            cursor.execute(insert_query, (
                phone_data.get('model_name'),
                phone_data.get('release_date'),
                phone_data.get('display'),
                phone_data.get('battery'),
                phone_data.get('camera'),
                phone_data.get('ram'),
                phone_data.get('storage'),
                phone_data.get('price'),
                phone_data.get('url'),
                json.dumps(additional_specs) if additional_specs else None
            ))
            
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting phone data: {e}")
            return False
    
    def bulk_insert_from_csv(self, csv_file_path: str):
        """Insert multiple phone records from CSV file."""
        try:
            df = pd.read_csv(csv_file_path)
            success_count = 0
            
            for _, row in df.iterrows():
                phone_data = row.to_dict()
                if self.insert_phone_data(phone_data):
                    success_count += 1
            
            logger.info(f"Inserted {success_count}/{len(df)} phone records")
            return success_count
            
        except Exception as e:
            logger.error(f"Error bulk inserting from CSV: {e}")
            return 0
    
    def search_phones(self, query: str, limit: int = 10) -> List[Dict]:
        """Search phones by name, specs, or other criteria."""
        if not self.connection:
            if not self.connect():
                return []
        
        search_query = """
        SELECT * FROM samsung_phones 
        WHERE 
            model_name ILIKE %s 
            OR display ILIKE %s 
            OR camera ILIKE %s 
            OR battery ILIKE %s
            OR ram ILIKE %s
            OR storage ILIKE %s
        ORDER BY 
            CASE 
                WHEN model_name ILIKE %s THEN 1 
                ELSE 2 
            END,
            model_name
        LIMIT %s
        """
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            search_term = f"%{query}%"
            exact_match = f"%{query}%"
            
            cursor.execute(search_query, (
                search_term, search_term, search_term, search_term, search_term, search_term,
                exact_match, limit
            ))
            
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error searching phones: {e}")
            return []
    
    def get_phone_by_name(self, model_name: str) -> Optional[Dict]:
        """Get a specific phone by exact model name."""
        if not self.connection:
            if not self.connect():
                return None
        
        query = "SELECT * FROM samsung_phones WHERE model_name ILIKE %s"
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (f"%{model_name}%",))
            result = cursor.fetchone()
            cursor.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Error getting phone by name: {e}")
            return None
    
    def get_phones_by_price_range(self, min_price: int, max_price: int) -> List[Dict]:
        """Get phones within a specific price range."""
        if not self.connection:
            if not self.connect():
                return []
        
        # Extract numeric price values
        query = """
        SELECT * FROM samsung_phones 
        WHERE 
            price IS NOT NULL 
            AND CAST(REGEXP_REPLACE(price, '[^0-9]', '', 'g') AS INTEGER) BETWEEN %s AND %s
        ORDER BY CAST(REGEXP_REPLACE(price, '[^0-9]', '', 'g') AS INTEGER)
        """
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (min_price, max_price))
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting phones by price range: {e}")
            return []
    
    def get_all_phones(self, limit: int = 50) -> List[Dict]:
        """Get all phones from database."""
        if not self.connection:
            if not self.connect():
                return []
        
        query = "SELECT * FROM samsung_phones ORDER BY model_name LIMIT %s"
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting all phones: {e}")
            return []
    
    def compare_phones(self, phone_names: List[str]) -> List[Dict]:
        """Get multiple phones for comparison."""
        if not self.connection:
            if not self.connect():
                return []
        
        placeholders = ', '.join(['%s'] * len(phone_names))
        query = f"""
        SELECT * FROM samsung_phones 
        WHERE model_name IN ({placeholders})
        ORDER BY model_name
        """
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, phone_names)
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error comparing phones: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self.connection:
            if not self.connect():
                return {}
        
        queries = {
            'total_phones': "SELECT COUNT(*) as count FROM samsung_phones",
            'phones_with_price': "SELECT COUNT(*) as count FROM samsung_phones WHERE price IS NOT NULL",
            'latest_phone': "SELECT model_name FROM samsung_phones ORDER BY created_at DESC LIMIT 1",
            'avg_price': """SELECT AVG(CAST(REGEXP_REPLACE(price, '[^0-9]', '', 'g') AS INTEGER)) as avg_price 
                           FROM samsung_phones WHERE price IS NOT NULL AND price != ''"""
        }
        
        stats = {}
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            for stat_name, query in queries.items():
                cursor.execute(query)
                result = cursor.fetchone()
                stats[stat_name] = result[list(result.keys())[0]] if result else None
            
            cursor.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}


# SQLite fallback for development/testing
class SQLitePhoneDatabase:
    """SQLite-based fallback database for development."""
    
    def __init__(self, db_path="samsung_phones.db"):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Connect to SQLite database."""
        import sqlite3
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    def create_tables(self):
        """Create tables in SQLite."""
        if not self.connection:
            if not self.connect():
                return False
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS samsung_phones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL UNIQUE,
            release_date TEXT,
            display TEXT,
            battery TEXT,
            camera TEXT,
            ram TEXT,
            storage TEXT,
            price TEXT,
            url TEXT,
            additional_specs TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("SQLite tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating SQLite tables: {e}")
            return False
    
    def insert_phone_data(self, phone_data: Dict[str, Any]):
        """Insert phone data into SQLite."""
        if not self.connection:
            if not self.connect():
                return False
        
        insert_query = """
        INSERT OR REPLACE INTO samsung_phones 
        (model_name, release_date, display, battery, camera, ram, storage, price, url, additional_specs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.connection.cursor()
            additional_specs = json.dumps({
                k: v for k, v in phone_data.items() 
                if k not in ['model_name', 'release_date', 'display', 'battery', 
                           'camera', 'ram', 'storage', 'price', 'url']
            })
            
            cursor.execute(insert_query, (
                phone_data.get('model_name'),
                phone_data.get('release_date'),
                phone_data.get('display'),
                phone_data.get('battery'),
                phone_data.get('camera'),
                phone_data.get('ram'),
                phone_data.get('storage'),
                phone_data.get('price'),
                phone_data.get('url'),
                additional_specs
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting data to SQLite: {e}")
            return False
    
    def search_phones(self, query: str, limit: int = 10) -> List[Dict]:
        """Search phones in SQLite."""
        if not self.connection:
            if not self.connect():
                return []
        
        search_query = """
        SELECT * FROM samsung_phones 
        WHERE 
            model_name LIKE ? OR
            display LIKE ? OR
            camera LIKE ? OR
            battery LIKE ? OR
            ram LIKE ? OR
            storage LIKE ?
        ORDER BY model_name
        LIMIT ?
        """
        
        try:
            cursor = self.connection.cursor()
            search_term = f"%{query}%"
            cursor.execute(search_query, (search_term, search_term, search_term, 
                                        search_term, search_term, search_term, limit))
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error searching in SQLite: {e}")
            return []


if __name__ == "__main__":
    # Test the database functionality
    print("Testing Samsung Phone Database...")
    
    # Try PostgreSQL first, fall back to SQLite
    try:
        db = SamsungPhoneDatabase()
        if not db.connect():
            raise Exception("PostgreSQL connection failed")
        print("Using PostgreSQL database")
    except:
        db = SQLitePhoneDatabase("database/samsung_phones.db")
        if not db.connect():
            print("Failed to connect to any database")
            exit(1)
        print("Using SQLite database (fallback)")
    
    # Create tables
    db.create_tables()
    
    # Test with sample data
    sample_phone = {
        'model_name': 'Samsung Galaxy S23 Ultra',
        'release_date': '2023-02-01',
        'display': '6.8" Dynamic AMOLED 2X, 120Hz',
        'battery': '5000 mAh',
        'camera': '200 MP main',
        'ram': '12GB',
        'storage': '256GB',
        'price': '$1199'
    }
    
    if db.insert_phone_data(sample_phone):
        print("Successfully inserted test phone data")
    
    # Test search
    results = db.search_phones("S23")
    print(f"Search results for 'S23': {len(results)} phones found")
    
    if hasattr(db, 'disconnect'):
        db.disconnect()