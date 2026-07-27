"""
Speech-to-Text Provider Interface Module
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, List, Dict
from app.utils.logger import LoggerMixin


class SpeechToTextProvider(ABC, LoggerMixin):
    """Abstract base class for speech-to-text providers"""
    
    def __init__(self):
        self.logger.info(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the speech-to-text engine
        
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the speech-to-text engine is available
        
        Returns:
            True if engine is ready to use
        """
        pass
    
    @abstractmethod
    async def download_model(self, model_id: str, 
                            progress_callback: Optional[Callable] = None) -> bool:
        """
        Download a speech recognition model
        
        Args:
            model_id: Model identifier
            progress_callback: Progress update callback
            
        Returns:
            True if download successful
        """
        pass
    
    @abstractmethod
    async def delete_model(self, model_id: str) -> bool:
        """
        Delete a speech recognition model
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def verify_model(self, model_id: str) -> bool:
        """
        Verify model integrity
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if model is valid
        """
        pass
    
    @abstractmethod
    async def transcribe(self, audio_path: str, 
                        language: Optional[str] = None,
                        progress_callback: Optional[Callable] = None) -> Optional[str]:
        """
        Transcribe audio to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (optional)
            progress_callback: Progress callback
            
        Returns:
            Transcribed text or None
        """
        pass
    
    @abstractmethod
    async def transcribe_with_timestamps(self, audio_path: str,
                                        language: Optional[str] = None) -> List[Dict]:
        """
        Transcribe audio with timestamps
        
        Args:
            audio_path: Path to audio file
            language: Language code
            
        Returns:
            List of dicts with text, start_time, end_time
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[Dict]:
        """
        Get available speech recognition models
        
        Returns:
            List of model information
        """
        pass
    
    @abstractmethod
    async def get_model_info(self, model_id: str) -> Optional[Dict]:
        """
        Get model information
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model information dictionary
        """
        pass
    
    @abstractmethod
    async def get_disk_usage(self) -> int:
        """
        Get disk usage by models
        
        Returns:
            Size in bytes
        """
        pass


class SpeechProviderFactory:
    """Factory for creating speech providers"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class):
        """Register a provider"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, name: str) -> Optional[SpeechToTextProvider]:
        """
        Create a speech provider
        
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
                SpeechToTextProvider.logger.error(f"Failed to create provider {name}: {e}")
                return None
        return None
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of registered provider names"""
        return list(cls._providers.keys())