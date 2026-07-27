"""
Dependency Injection Container
Centralized dependency management for the application
"""

from typing import Dict, Any, Optional
from app.utils.logger import LoggerMixin


class DIContainer(LoggerMixin):
    """
    Simple Dependency Injection Container
    Manages all application dependencies
    """
    
    _instance = None
    _services: Dict[str, Any] = {}
    _repositories: Dict[str, Any] = {}
    _providers: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DIContainer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.logger.info("DI Container initialized")
    
    def register_service(self, name: str, service: Any):
        """Register a service"""
        self._services[name] = service
        self.logger.debug(f"Service registered: {name}")
    
    def register_repository(self, name: str, repository: Any):
        """Register a repository"""
        self._repositories[name] = repository
        self.logger.debug(f"Repository registered: {name}")
    
    def register_provider(self, name: str, provider: Any):
        """Register a provider"""
        self._providers[name] = provider
        self.logger.debug(f"Provider registered: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self._services.get(name)
    
    def get_repository(self, name: str) -> Optional[Any]:
        """Get a registered repository"""
        return self._repositories.get(name)
    
    def get_provider(self, name: str) -> Optional[Any]:
        """Get a registered provider"""
        return self._providers.get(name)
    
    def initialize_all(self):
        """Initialize all core services"""
        try:
            # Initialize Database
            from app.database.database_manager import DatabaseManager
            db = DatabaseManager()
            db.initialize()
            self.register_service('database', db)
            
            # Initialize Config
            from app.config.app_config import AppConfig
            config = AppConfig()
            config.load_config()
            self.register_service('config', config)
            
            # Initialize Storage
            from app.services.storage.storage_service import StorageService
            storage = StorageService()
            self.register_service('storage', storage)
            
            # Initialize Download Service
            from app.services.download.download_service import DownloadService
            download_service = DownloadService()
            self.register_service('download', download_service)
            
            # Initialize Subtitle Service
            from app.services.subtitle.subtitle_service import SubtitleService
            subtitle_service = SubtitleService()
            self.register_service('subtitle', subtitle_service)
            
            # Initialize Queue Service
            from app.services.queue.queue_service import QueueService
            queue_service = QueueService()
            self.register_service('queue', queue_service)
            
            # Initialize Settings Service
            from app.services.settings.settings_service import SettingsService
            settings_service = SettingsService()
            self.register_service('settings', settings_service)
            
            # Initialize Model Service
            from app.services.models.model_service import ModelService
            model_service = ModelService()
            self.register_service('model', model_service)
            
            # Initialize Package Service
            from app.services.packages.package_service import PackageService
            package_service = PackageService()
            self.register_service('package', package_service)
            
            # Initialize History Service
            from app.services.history.history_service import HistoryService
            history_service = HistoryService()
            self.register_service('history', history_service)
            
            # Initialize Repositories
            from app.repositories.download_repository_impl import DownloadRepositoryImpl
            download_repo = DownloadRepositoryImpl()
            self.register_repository('download', download_repo)
            
            from app.repositories.settings_repository_impl import SettingsRepositoryImpl
            settings_repo = SettingsRepositoryImpl()
            self.register_repository('settings', settings_repo)
            
            from app.repositories.model_repository_impl import ModelRepositoryImpl
            model_repo = ModelRepositoryImpl()
            self.register_repository('model', model_repo)
            
            from app.repositories.package_repository_impl import PackageRepositoryImpl
            package_repo = PackageRepositoryImpl()
            self.register_repository('package', package_repo)
            
            from app.repositories.subtitle_repository_impl import SubtitleRepositoryImpl
            subtitle_repo = SubtitleRepositoryImpl()
            self.register_repository('subtitle', subtitle_repo)
            
            self.logger.info("All dependencies initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dependencies: {e}")
            raise
    
    def shutdown(self):
        """Cleanup all services"""
        try:
            if 'database' in self._services:
                self._services['database'].close()
            
            self._services.clear()
            self._repositories.clear()
            self._providers.clear()
            
            self.logger.info("All services shutdown")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Global DI instance
di_container = DIContainer()