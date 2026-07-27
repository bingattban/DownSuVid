"""
Migration Manager Module
"""

from typing import List, Tuple
from app.utils.logger import LoggerMixin


class Migration:
    """Migration class"""
    
    def __init__(self, version: int, description: str, sql: str):
        self.version = version
        self.description = description
        self.sql = sql


class MigrationManager(LoggerMixin):
    """Database Migration Manager"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.migrations_table = "schema_migrations"
    
    def run_migrations(self) -> None:
        """Run all pending migrations"""
        try:
            self._create_migrations_table()
            current_version = self._get_current_version()
            
            migrations = self._get_migrations()
            
            for migration in migrations:
                if migration.version > current_version:
                    self._apply_migration(migration)
                    self.logger.info(f"Applied migration {migration.version}: {migration.description}")
            
            self.logger.info("All migrations applied successfully")
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            raise
    
    def _create_migrations_table(self) -> None:
        """Create migrations tracking table"""
        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db_manager.execute(query)
    
    def _get_current_version(self) -> int:
        """Get current database version"""
        if not self.db_manager.table_exists(self.migrations_table):
            return 0
        
        result = self.db_manager.fetch_one(
            "SELECT MAX(version) as version FROM schema_migrations"
        )
        return result['version'] if result['version'] else 0
    
    def _get_migrations(self) -> List[Migration]:
        """Get list of migrations"""
        return [
            Migration(
                version=1,
                description="Create initial tables",
                sql="""
                CREATE TABLE IF NOT EXISTS downloads (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    title TEXT,
                    thumbnail_url TEXT,
                    file_path TEXT,
                    subtitle_path TEXT,
                    status TEXT DEFAULT 'pending',
                    progress REAL DEFAULT 0.0,
                    speed TEXT,
                    size_total INTEGER DEFAULT 0,
                    size_downloaded INTEGER DEFAULT 0,
                    format_id TEXT,
                    quality TEXT,
                    website TEXT,
                    uploader TEXT,
                    duration INTEGER,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    action TEXT NOT NULL,
                    status TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS models (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    language TEXT,
                    version TEXT,
                    file_path TEXT,
                    size_total INTEGER DEFAULT 0,
                    size_downloaded INTEGER DEFAULT 0,
                    sha256 TEXT,
                    status TEXT DEFAULT 'not_installed',
                    progress REAL DEFAULT 0.0,
                    is_active INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS packages (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    source_lang TEXT,
                    target_lang TEXT,
                    version TEXT,
                    file_path TEXT,
                    size_total INTEGER DEFAULT 0,
                    size_downloaded INTEGER DEFAULT 0,
                    sha256 TEXT,
                    status TEXT DEFAULT 'not_installed',
                    progress REAL DEFAULT 0.0,
                    is_active INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    type TEXT DEFAULT 'string',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_type TEXT NOT NULL,
                    task_data TEXT,
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    current_version TEXT,
                    latest_version TEXT,
                    update_url TEXT,
                    status TEXT DEFAULT 'pending',
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_downloads_status ON downloads(status);
                CREATE INDEX IF NOT EXISTS idx_downloads_url ON downloads(url);
                CREATE INDEX IF NOT EXISTS idx_history_url ON history(url);
                CREATE INDEX IF NOT EXISTS idx_models_type ON models(type);
                CREATE INDEX IF NOT EXISTS idx_packages_type ON packages(type);
                CREATE INDEX IF NOT EXISTS idx_queue_status ON queue(status);
                CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
                """
            ),
        ]
    
    def _apply_migration(self, migration: Migration) -> None:
        """Apply a single migration"""
        # Execute migration SQL
        statements = migration.sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                self.db_manager.execute(statement)
        
        # Record migration
        self.db_manager.execute(
            "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
            (migration.version, migration.description)
        )