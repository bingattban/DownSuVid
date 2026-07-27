"""
Database Manager Module
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager

from app.utils.logger import LoggerMixin
from app.config.constants import (
    STORAGE_ROOT,
    STORAGE_DATABASE,
    DATABASE_NAME,
    DATABASE_VERSION
)


class DatabaseManager(LoggerMixin):
    """Database Manager for SQLite operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self._connection: Optional[sqlite3.Connection] = None
        self._db_path: Optional[Path] = None
        self.logger.info("DatabaseManager created")
    
    def initialize(self, db_path: Optional[str] = None) -> None:
        """
        Initialize database
        
        Args:
            db_path: Path to database file
        """
        try:
            if db_path is None:
                db_dir = Path.home() / STORAGE_ROOT / STORAGE_DATABASE
                db_dir.mkdir(parents=True, exist_ok=True)
                self._db_path = db_dir / DATABASE_NAME
            else:
                self._db_path = Path(db_path)
            
            self._create_connection()
            self._run_migrations()
            self.logger.info(f"Database initialized at {self._db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_connection(self) -> None:
        """Create database connection"""
        try:
            self._connection = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
                timeout=10
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.execute("PRAGMA encoding='UTF-8'")
            
        except Exception as e:
            self.logger.error(f"Failed to create connection: {e}")
            raise
    
    def _run_migrations(self) -> None:
        """Run database migrations"""
        from app.database.migrations.migration_manager import MigrationManager
        migration_manager = MigrationManager(self)
        migration_manager.run_migrations()
    
    @contextmanager
    def get_cursor(self):
        """Get database cursor"""
        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def execute(self, query: str, params: Optional[Tuple] = None) -> None:
        """
        Execute SQL query
        
        Args:
            query: SQL query
            params: Query parameters
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """
        Execute SQL query with multiple parameter sets
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[sqlite3.Row]:
        """
        Fetch single row
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Single row or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[sqlite3.Row]:
        """
        Fetch all rows
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of rows
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def get_count(self, table: str, where: Optional[str] = None, 
                  params: Optional[Tuple] = None) -> int:
        """
        Get row count
        
        Args:
            table: Table name
            where: WHERE clause
            params: Query parameters
            
        Returns:
            Row count
        """
        query = f"SELECT COUNT(*) as count FROM {table}"
        if where:
            query += f" WHERE {where}"
        
        result = self.fetch_one(query, params)
        return result['count'] if result else 0
    
    def table_exists(self, table: str) -> bool:
        """
        Check if table exists
        
        Args:
            table: Table name
            
        Returns:
            True if table exists
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetch_one(query, (table,))
        return result is not None
    
    def get_database_size(self) -> int:
        """
        Get database file size
        
        Returns:
            Size in bytes
        """
        if self._db_path and self._db_path.exists():
            return self._db_path.stat().st_size
        return 0
    
    def vacuum(self) -> None:
        """Optimize database"""
        self.execute("VACUUM")
        self.logger.info("Database vacuumed")
    
    def backup(self, backup_path: Optional[str] = None) -> bool:
        """
        Backup database
        
        Args:
            backup_path: Backup file path
            
        Returns:
            True if successful
        """
        try:
            if backup_path is None:
                backup_dir = Path.home() / STORAGE_ROOT / STORAGE_DATABASE / 'backups'
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            source = sqlite3.connect(str(self._db_path))
            dest = sqlite3.connect(str(backup_path))
            
            source.backup(dest)
            
            dest.close()
            source.close()
            
            self.logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False
    
    def close(self) -> None:
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            self.logger.info("Database connection closed")