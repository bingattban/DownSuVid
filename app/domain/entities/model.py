"""
Model Entity Module
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class ModelType(Enum):
    """Model type enumeration"""
    SPEECH_TO_TEXT = "speech_to_text"
    TRANSLATION = "translation"
    OTHER = "other"


class ModelStatus(Enum):
    """Model status enumeration"""
    NOT_INSTALLED = "not_installed"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
    PAUSED = "paused"
    UPDATING = "updating"
    REPAIRING = "repairing"


class ModelProvider(Enum):
    """Model provider enumeration"""
    WHISPER = "whisper"
    FASTER_WHISPER = "faster_whisper"
    VOSK = "vosk"
    CUSTOM = "custom"


@dataclass
class ModelInfo:
    """Model information entity"""
    id: str
    name: str
    type: ModelType
    provider: ModelProvider
    
    # Version
    version: Optional[str] = None
    latest_version: Optional[str] = None
    
    # Language support
    language: Optional[str] = None
    supported_languages: list = field(default_factory=list)
    
    # File information
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    download_url: Optional[str] = None
    size_total: int = 0
    size_downloaded: int = 0
    sha256: Optional[str] = None
    
    # Status
    status: ModelStatus = ModelStatus.NOT_INSTALLED
    is_active: bool = False
    
    # Progress
    progress: float = 0.0
    
    # Requirements
    min_ram_mb: int = 512
    min_storage_mb: int = 100
    recommended_device: Optional[str] = None
    
    # License
    license_info: Optional[str] = None
    license_url: Optional[str] = None
    
    # Description
    description: Optional[str] = None
    repository_url: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    installed_at: Optional[datetime] = None
    
    def get_formatted_size(self) -> str:
        """Get formatted size"""
        from app.utils.file_utils import FileUtils
        return FileUtils.format_file_size(self.size_total)
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage"""
        if self.size_total == 0:
            return 0.0
        return (self.size_downloaded / self.size_total) * 100
    
    def is_installed(self) -> bool:
        """Check if model is installed"""
        return self.status == ModelStatus.INSTALLED
    
    def is_downloading(self) -> bool:
        """Check if model is downloading"""
        return self.status == ModelStatus.DOWNLOADING
    
    def can_download(self) -> bool:
        """Check if model can be downloaded"""
        return self.status in [ModelStatus.NOT_INSTALLED, ModelStatus.FAILED]
    
    def can_update(self) -> bool:
        """Check if model can be updated"""
        return (self.is_installed() and 
                self.latest_version and 
                self.version != self.latest_version)
    
    def needs_repair(self) -> bool:
        """Check if model needs repair"""
        return self.status in [ModelStatus.FAILED, ModelStatus.NOT_INSTALLED]