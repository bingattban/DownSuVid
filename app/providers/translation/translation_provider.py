"""
Translation Provider Interface Module
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, List, Dict
from app.utils.logger import LoggerMixin


class TranslationProvider(ABC, LoggerMixin):
    """Abstract base class for translation providers"""
    
    def __init__(self):
        self.logger.info(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the translation engine
        
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the translation engine is available
        
        Returns:
            True if engine is ready
        """
        pass
    
    @abstractmethod
    async def download_package(self, source_lang: str, target_lang: str,
                              progress_callback: Optional[Callable] = None) -> bool:
        """
        Download translation package
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            progress_callback: Progress callback
            
        Returns:
            True if download successful
        """
        pass
    
    @abstractmethod
    async def delete_package(self, source_lang: str, target_lang: str) -> bool:
        """
        Delete translation package
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def verify_package(self, source_lang: str, target_lang: str) -> bool:
        """
        Verify package integrity
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            True if package is valid
        """
        pass
    
    @abstractmethod
    async def translate(self, text: str, source_lang: str, 
                       target_lang: str = "ar") -> Optional[str]:
        """
        Translate text
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text or None
        """
        pass
    
    @abstractmethod
    async def translate_batch(self, texts: List[str], source_lang: str,
                            target_lang: str = "ar") -> List[Optional[str]]:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of translated texts
        """
        pass
    
    @abstractmethod
    async def detect_language(self, text: str) -> Optional[str]:
        """
        Detect text language
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code or None
        """
        pass
    
    @abstractmethod
    async def get_available_packages(self) -> List[Dict]:
        """
        Get available translation packages
        
        Returns:
            List of package information
        """
        pass
    
    @abstractmethod
    async def get_installed_packages(self) -> List[Dict]:
        """
        Get installed translation packages
        
        Returns:
            List of installed packages
        """
        pass
    
    @abstractmethod
    async def is_package_installed(self, source_lang: str, 
                                   target_lang: str) -> bool:
        """
        Check if package is installed
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            True if package is installed
        """
        pass
    
    @abstractmethod
    async def get_disk_usage(self) -> int:
        """
        Get disk usage by packages
        
        Returns:
            Size in bytes
        """
        pass


class TranslationProviderFactory:
    """Factory for creating translation providers"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class):
        """Register a provider"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, name: str) -> Optional[TranslationProvider]:
        """
        Create a translation provider
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or None
        """
        provider_class = cls._providers.get(name)
        if provider_class:
            try:
                return provider_class()
            except Exception as e:
                TranslationProvider.logger.error(f"Failed to create provider {name}: {e}")
                return None
        return None
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of registered provider names"""
        return list(cls._providers.keys())