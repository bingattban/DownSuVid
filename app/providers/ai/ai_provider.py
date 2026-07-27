"""
AI Provider Module - Optional AI Engine Support
"""

from typing import Optional, List, Dict, Any
from app.utils.logger import LoggerMixin


class AIProvider(LoggerMixin):
    """
    AI Provider abstraction layer
    
    This provider manages optional AI engines.
    Never imports unsupported AI libraries directly.
    All AI engines are loaded lazily and checked for compatibility.
    """
    
    def __init__(self):
        self._available_engines = {}
        self._active_engines = {}
        self.logger.info("AIProvider initialized")
    
    async def is_engine_available(self, engine_name: str) -> bool:
        """
        Check if an AI engine is available
        
        Args:
            engine_name: Engine name
            
        Returns:
            True if engine can be loaded
        """
        if engine_name in self._available_engines:
            return self._available_engines[engine_name]
        
        # Try to import engine
        available = await self._check_engine(engine_name)
        self._available_engines[engine_name] = available
        
        return available
    
    async def _check_engine(self, engine_name: str) -> bool:
        """
        Check if engine module can be imported
        
        Args:
            engine_name: Engine name
            
        Returns:
            True if importable
        """
        try:
            # Mapping of engine names to import paths
            engine_imports = {
                'whisper': 'whisper',
                'faster_whisper': 'faster_whisper',
                'argos': 'argostranslate',
                'marian': 'marian',
            }
            
            import_path = engine_imports.get(engine_name)
            if not import_path:
                self.logger.debug(f"Unknown engine: {engine_name}")
                return False
            
            # Try importing
            __import__(import_path)
            
            self.logger.info(f"Engine available: {engine_name}")
            return True
            
        except ImportError:
            self.logger.debug(f"Engine not available: {engine_name}")
            return False
        except Exception as e:
            self.logger.warning(f"Engine check failed for {engine_name}: {e}")
            return False
    
    async def get_engine(self, engine_name: str) -> Optional[Any]:
        """
        Get an AI engine instance
        
        Args:
            engine_name: Engine name
            
        Returns:
            Engine instance or None
        """
        if engine_name in self._active_engines:
            return self._active_engines[engine_name]
        
        if not await self.is_engine_available(engine_name):
            return None
        
        try:
            # Create engine instance based on type
            engine = await self._create_engine(engine_name)
            
            if engine:
                self._active_engines[engine_name] = engine
                self.logger.info(f"Engine created: {engine_name}")
            
            return engine
            
        except Exception as e:
            self.logger.error(f"Failed to create engine {engine_name}: {e}")
            return None
    
    async def _create_engine(self, engine_name: str) -> Optional[Any]:
        """
        Create engine instance
        
        Args:
            engine_name: Engine name
            
        Returns:
            Engine instance or None
        """
        try:
            # Speech engines
            if engine_name == 'whisper':
                return await self._create_whisper_engine()
            elif engine_name == 'faster_whisper':
                return await self._create_faster_whisper_engine()
            
            # Translation engines
            elif engine_name == 'argos':
                return await self._create_argos_engine()
            elif engine_name == 'marian':
                return await self._create_marian_engine()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Engine creation failed: {e}")
            return None
    
    async def _create_whisper_engine(self):
        """Create Whisper engine"""
        try:
            import whisper
            model = whisper.load_model("base")
            return model
        except Exception as e:
            self.logger.error(f"Whisper engine creation failed: {e}")
            return None
    
    async def _create_faster_whisper_engine(self):
        """Create Faster Whisper engine"""
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel("base", device="cpu")
            return model
        except Exception as e:
            self.logger.error(f"Faster Whisper engine creation failed: {e}")
            return None
    
    async def _create_argos_engine(self):
        """Create Argos Translate engine"""
        try:
            import argostranslate.package
            import argostranslate.translate
            
            # Update package index
            argostranslate.package.update_package_index()
            
            return argostranslate.translate
        except Exception as e:
            self.logger.error(f"Argos engine creation failed: {e}")
            return None
    
    async def _create_marian_engine(self):
        """Create Marian engine"""
        # Placeholder for future implementation
        self.logger.info("Marian engine not yet implemented")
        return None
    
    async def release_engine(self, engine_name: str):
        """Release an engine instance"""
        if engine_name in self._active_engines:
            del self._active_engines[engine_name]
            self.logger.info(f"Engine released: {engine_name}")
    
    async def get_available_engines(self) -> List[str]:
        """Get list of available engines"""
        available = []
        
        for engine in ['whisper', 'faster_whisper', 'argos', 'marian']:
            if await self.is_engine_available(engine):
                available.append(engine)
        
        return available