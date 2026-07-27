"""
Package Entity Module
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PackageType(Enum):
    """Package type enumeration"""
    TRANSLATION = "translation"
    LANGUAGE_MODEL = "language_model"
    OTHER = "other"


class PackageStatus(Enum):
    """Package status enumeration"""
    NOT_INSTALLED = "not_installed"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
    PAUSED = "paused"
    UPDATING = "updating"


class PackageProvider(Enum):
    """Package provider enumeration"""
    ARGOS = "argos"
    MARIAN = "marian"
    OPUS = "opus"
    CUSTOM = "custom"


@dataclass
class PackageInfo:
    """Package information entity"""
    id: str
    name: str
    type: PackageType
    provider: PackageProvider
    
    # Language pair
    source_language: str
    target_language: str
    source_language_name: Optional[str] = None
    target_language_name: Optional[str] = None
    
    # Version
    version: Optional[str] = None
    latest_version: Optional[str] = None
    
    # File information
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    download_url: Optional[str] = None
    size_total: int = 0
    size_downloaded: int = 0
    sha256: Optional[str] = None
    
    # Status
    status: PackageStatus = PackageStatus.NOT_INSTALLED
    is_active: bool = False
    
    # Progress
    progress: float = 0.0
    
    # Requirements
    min_ram_mb: int = 256
    min_storage_mb: int = 50
    
    # Performance metrics
    translation_quality_score: Optional[float] = None
    average_translation_time_ms: Optional[int] = None
    
    # Description
    description: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    installed_at: Optional[datetime] = None
    
    def get_formatted_size(self) -> str:
        """Get formatted size"""
        from app.utils.file_utils import FileUtils
        return FileUtils.format_file_size(self.size_total)
    
    def get_language_pair(self) -> str:
        """Get language pair string"""
        return f"{self.source_language} → {self.target_language}"
    
    def is_installed(self) -> bool:
        """Check if package is installed"""
        return self.status == PackageStatus.INSTALLED
    
    def is_downloading(self) -> bool:
        """Check if package is downloading"""
        return self.status == PackageStatus.DOWNLOADING
    
    def can_download(self) -> bool:
        """Check if package can be downloaded"""
        return self.status in [PackageStatus.NOT_INSTALLED, PackageStatus.FAILED]