"""
Argos Translate Provider Implementation
"""

from typing import Optional, Callable, List, Dict
from app.utils.logger import LoggerMixin
from app.providers.translation.translation_provider import TranslationProvider


class ArgosProvider(TranslationProvider):
    """Argos Translate provider"""
    
    def __init__(self):
        super().__init__()
        self._installed_packages = {}
        self.logger.info("ArgosProvider created")
    
    async def initialize(self) -> bool:
        """Initialize Argos Translate"""
        try:
            import argostranslate.package
            import argostranslate.translate
            
            self._argos_package = argostranslate.package
            self._argos_translate = argostranslate.translate
            
            # Update package index
            self._argos_package.update_package_index()
            
            # Load installed packages
            self._load_installed_packages()
            
            self.logger.info("Argos Translate initialized")
            return True
            
        except ImportError:
            self.logger.warning("Argos Translate not installed")
            return False
        except Exception as e:
            self.logger.error(f"Argos initialization failed: {e}")
            return False
    
    def _load_installed_packages(self):
        """Load installed packages"""
        try:
            installed = self._argos_package.get_installed_packages()
            for pkg in installed:
                key = f"{pkg.from_code}_{pkg.to_code}"
                self._installed_packages[key] = pkg
        except Exception as e:
            self.logger.warning(f"Failed to load packages: {e}")
    
    async def is_available(self) -> bool:
        """Check if Argos is available"""
        try:
            import argostranslate.package
            return True
        except ImportError:
            return False
    
    async def download_package(self, source_lang: str, target_lang: str,
                              progress_callback: Optional[Callable] = None) -> bool:
        """Download translation package"""
        try:
            # Find package
            available_packages = self._argos_package.get_available_packages()
            
            target_package = None
            for pkg in available_packages:
                if pkg.from_code == source_lang and pkg.to_code == target_lang:
                    target_package = pkg
                    break
            
            if not target_package:
                self.logger.error(f"Package not found: {source_lang} -> {target_lang}")
                return False
            
            # Download package
            if progress_callback:
                await progress_callback(f"{source_lang}_{target_lang}", 0.0, 'downloading')
            
            download_path = target_package.download()
            
            if progress_callback:
                await progress_callback(f"{source_lang}_{target_lang}", 50.0, 'installing')
            
            # Install package
            self._argos_package.install_from_path(download_path)
            
            if progress_callback:
                await progress_callback(f"{source_lang}_{target_lang}", 100.0, 'completed')
            
            # Reload installed packages
            self._load_installed_packages()
            
            self.logger.info(f"Package installed: {source_lang} -> {target_lang}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download package: {e}")
            return False
    
    async def delete_package(self, source_lang: str, target_lang: str) -> bool:
        """Delete translation package"""
        try:
            key = f"{source_lang}_{target_lang}"
            
            if key in self._installed_packages:
                pkg = self._installed_packages[key]
                
                # Remove package files
                import os
                if hasattr(pkg, 'package_path'):
                    os.remove(pkg.package_path)
                
                del self._installed_packages[key]
                self.logger.info(f"Package deleted: {source_lang} -> {target_lang}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete package: {e}")
            return False
    
    async def verify_package(self, source_lang: str, target_lang: str) -> bool:
        """Verify package integrity"""
        return await self.is_package_installed(source_lang, target_lang)
    
    async def translate(self, text: str, source_lang: str,
                       target_lang: str = "ar") -> Optional[str]:
        """Translate text"""
        try:
            key = f"{source_lang}_{target_lang}"
            
            if key not in self._installed_packages:
                self.logger.error(f"Package not installed: {source_lang} -> {target_lang}")
                return None
            
            translation = self._installed_packages[key].translate(text)
            return translation
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            return None
    
    async def translate_batch(self, texts: List[str], source_lang: str,
                             target_lang: str = "ar") -> List[Optional[str]]:
        """Translate multiple texts"""
        results = []
        
        for text in texts:
            translated = await self.translate(text, source_lang, target_lang)
            results.append(translated)
        
        return results
    
    async def detect_language(self, text: str) -> Optional[str]:
        """Detect text language"""
        try:
            # Simple detection based on character set
            arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06ff')
            
            if arabic_chars > len(text) * 0.3:
                return 'ar'
            
            # Default to English
            return 'en'
            
        except Exception:
            return None
    
    async def get_available_packages(self) -> List[Dict]:
        """Get available packages"""
        try:
            packages = []
            available = self._argos_package.get_available_packages()
            
            for pkg in available:
                packages.append({
                    'id': f"argos_{pkg.from_code}_{pkg.to_code}",
                    'name': f"{pkg.from_name} → {pkg.to_name}",
                    'source_lang': pkg.from_code,
                    'target_lang': pkg.to_code,
                    'source_lang_name': pkg.from_name,
                    'target_lang_name': pkg.to_name,
                    'size': 50 * 1024 * 1024,  # Approximate
                    'version': '1.0.0',
                    'installed': await self.is_package_installed(pkg.from_code, pkg.to_code),
                })
            
            return packages
            
        except Exception as e:
            self.logger.error(f"Failed to get packages: {e}")
            return []
    
    async def get_installed_packages(self) -> List[Dict]:
        """Get installed packages"""
        packages = []
        
        for key, pkg in self._installed_packages.items():
            parts = key.split('_')
            if len(parts) == 2:
                packages.append({
                    'id': f"argos_{key}",
                    'name': f"{parts[0]} → {parts[1]}",
                    'source_lang': parts[0],
                    'target_lang': parts[1],
                    'installed': True,
                })
        
        return packages
    
    async def is_package_installed(self, source_lang: str, target_lang: str) -> bool:
        """Check if package is installed"""
        key = f"{source_lang}_{target_lang}"
        return key in self._installed_packages
    
    async def get_disk_usage(self) -> int:
        """Get disk usage"""
        total = 0
        
        for pkg in self._installed_packages.values():
            if hasattr(pkg, 'package_path'):
                import os
                if os.path.exists(pkg.package_path):
                    total += os.path.getsize(pkg.package_path)
        
        return total