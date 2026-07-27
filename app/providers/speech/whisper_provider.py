"""
Whisper Provider Implementation
"""

from typing import Optional, Callable, List, Dict
from app.utils.logger import LoggerMixin
from app.providers.speech.speech_provider import SpeechToTextProvider


class WhisperProvider(SpeechToTextProvider):
    """Whisper speech-to-text provider"""
    
    def __init__(self):
        super().__init__()
        self._model = None
        self._model_id = None
        self.logger.info("WhisperProvider created")
    
    async def initialize(self) -> bool:
        """Initialize Whisper"""
        try:
            # Lazy import
            import whisper
            self._whisper_module = whisper
            self.logger.info("Whisper initialized")
            return True
        except ImportError:
            self.logger.warning("Whisper not installed")
            return False
        except Exception as e:
            self.logger.error(f"Whisper initialization failed: {e}")
            return False
    
    async def is_available(self) -> bool:
        """Check if Whisper is available"""
        try:
            import whisper
            return True
        except ImportError:
            return False
    
    async def download_model(self, model_id: str,
                            progress_callback: Optional[Callable] = None) -> bool:
        """Download Whisper model"""
        try:
            import whisper
            
            self.logger.info(f"Downloading Whisper model: {model_id}")
            
            # Model will be downloaded automatically on load
            model = whisper.load_model(model_id)
            self._model = model
            self._model_id = model_id
            
            if progress_callback:
                await progress_callback(model_id, 100.0, 'completed')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download model: {e}")
            return False
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete Whisper model"""
        try:
            import os
            import whisper
            
            # Get model directory
            model_dir = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
            
            if os.path.exists(model_dir):
                model_file = os.path.join(model_dir, f"{model_id}.pt")
                if os.path.exists(model_file):
                    os.remove(model_file)
                    self.logger.info(f"Model deleted: {model_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete model: {e}")
            return False
    
    async def verify_model(self, model_id: str) -> bool:
        """Verify model integrity"""
        try:
            import os
            
            model_dir = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
            model_file = os.path.join(model_dir, f"{model_id}.pt")
            
            return os.path.exists(model_file)
            
        except Exception:
            return False
    
    async def transcribe(self, audio_path: str,
                        language: Optional[str] = None,
                        progress_callback: Optional[Callable] = None) -> Optional[str]:
        """Transcribe audio"""
        try:
            if not self._model:
                self.logger.error("No model loaded")
                return None
            
            options = {}
            if language:
                options['language'] = language
            
            result = self._model.transcribe(audio_path, **options)
            
            return result.get('text', '')
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return None
    
    async def transcribe_with_timestamps(self, audio_path: str,
                                        language: Optional[str] = None) -> List[Dict]:
        """Transcribe with timestamps"""
        try:
            if not self._model:
                self.logger.error("No model loaded")
                return []
            
            options = {}
            if language:
                options['language'] = language
            
            result = self._model.transcribe(audio_path, **options)
            
            segments = []
            for seg in result.get('segments', []):
                segments.append({
                    'text': seg.get('text', '').strip(),
                    'start': seg.get('start', 0),
                    'end': seg.get('end', 0),
                    'confidence': seg.get('confidence', 0),
                })
            
            return segments
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return []
    
    async def get_available_models(self) -> List[Dict]:
        """Get available models"""
        return [
            {
                'id': 'tiny',
                'name': 'Whisper Tiny',
                'size': 75 * 1024 * 1024,
                'language': 'multi',
                'description': 'أسرع نموذج - دقة أقل',
            },
            {
                'id': 'base',
                'name': 'Whisper Base',
                'size': 145 * 1024 * 1024,
                'language': 'multi',
                'description': 'توازن بين السرعة والدقة',
            },
            {
                'id': 'small',
                'name': 'Whisper Small',
                'size': 488 * 1024 * 1024,
                'language': 'multi',
                'description': 'دقة جيدة',
            },
            {
                'id': 'medium',
                'name': 'Whisper Medium',
                'size': 1536 * 1024 * 1024,
                'language': 'multi',
                'description': 'دقة عالية',
            },
        ]
    
    async def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get model info"""
        models = await self.get_available_models()
        for model in models:
            if model['id'] == model_id:
                return model
        return None
    
    async def get_disk_usage(self) -> int:
        """Get disk usage"""
        try:
            import os
            
            model_dir = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
            
            if os.path.exists(model_dir):
                total = 0
                for file in os.listdir(model_dir):
                    file_path = os.path.join(model_dir, file)
                    if os.path.isfile(file_path):
                        total += os.path.getsize(file_path)
                return total
            
            return 0
            
        except Exception:
            return 0