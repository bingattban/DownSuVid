"""
Updater Service Module
"""

import asyncio
from typing import Optional, Dict
import json

from app.utils.logger import LoggerMixin
from app.config.constants import (
    APP_VERSION,
    UPDATE_CHECK_URL,
    GITHUB_REPO,
)
from app.config.app_config import AppConfig


class UpdaterService(LoggerMixin):
    """Service for checking and managing updates"""
    
    def __init__(self):
        self.config = AppConfig()
        self._update_info: Optional[Dict] = None
        self.logger.info("UpdaterService initialized")
    
    async def check_updates_async(self) -> Optional[Dict]:
        """
        Check for updates asynchronously
        
        Returns:
            Update info dictionary or None
        """
        try:
            if not await self._is_enabled():
                self.logger.debug("Update check disabled")
                return None
            
            self.logger.info("Checking for updates...")
            
            # Try to fetch latest release info
            update_info = await self._fetch_update_info()
            
            if update_info:
                latest_version = update_info.get('version', '0.0.0')
                
                if self._is_newer_version(latest_version, APP_VERSION):
                    self._update_info = update_info
                    self.logger.info(f"Update available: {latest_version}")
                    return update_info
                else:
                    self.logger.info("Already up to date")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Update check failed: {e}")
            return None
    
    async def _fetch_update_info(self) -> Optional[Dict]:
        """Fetch update info from server"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                # Try GitHub API
                response = await client.get(
                    UPDATE_CHECK_URL,
                    timeout=10,
                    headers={'Accept': 'application/vnd.github.v3+json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return {
                        'version': data.get('tag_name', '').lstrip('v'),
                        'name': data.get('name', ''),
                        'description': data.get('body', ''),
                        'url': data.get('html_url', ''),
                        'download_url': data.get('assets', [{}])[0].get('browser_download_url', ''),
                        'size': data.get('assets', [{}])[0].get('size', 0),
                        'published_at': data.get('published_at', ''),
                    }
            
            return None
            
        except ImportError:
            self.logger.debug("httpx not available for update check")
            return None
        except Exception as e:
            self.logger.debug(f"Failed to fetch update info: {e}")
            return None
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """
        Compare version strings
        
        Args:
            latest: Latest version
            current: Current version
            
        Returns:
            True if latest is newer
        """
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad to same length
            while len(latest_parts) < 3:
                latest_parts.append(0)
            while len(current_parts) < 3:
                current_parts.append(0)
            
            for l, c in zip(latest_parts, current_parts):
                if l > c:
                    return True
                elif l < c:
                    return False
            
            return False
            
        except Exception:
            return False
    
    async def get_update_info(self) -> Optional[Dict]:
        """Get cached update info"""
        return self._update_info
    
    async def has_update(self) -> bool:
        """Check if update is available"""
        return self._update_info is not None
    
    async def clear_update_info(self):
        """Clear cached update info"""
        self._update_info = None
    
    async def _is_enabled(self) -> bool:
        """Check if update check is enabled"""
        return self.config.get('auto_check_updates', True)
    
    async def download_update(self) -> bool:
        """
        Download update
        
        Returns:
            True if download started
        """
        if not self._update_info:
            return False
        
        download_url = self._update_info.get('download_url')
        if not download_url:
            return False
        
        self.logger.info(f"Update download started: {download_url}")
        
        # Placeholder for actual download implementation
        # Would download APK and prompt user to install
        
        return True