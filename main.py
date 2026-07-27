"""
DownSuVid - Video Downloader with Smart Subtitle Processing
Main Application Entry Point
"""

import os
import sys
import logging

# Configure Kivy before importing other modules
from kivy.config import Config
Config.set('kivy', 'log_level', 'info')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', 0)
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

from app.config.constants import APP_NAME, APP_VERSION
from app.utils.logger import setup_logger

# Setup logger first
logger = setup_logger('DownSuVid', logging.INFO)


class DownSuVidApp(App):
    """Main Application Class"""
    
    def __init__(self, **kwargs):
        super(DownSuVidApp, self).__init__(**kwargs)
        self.title = f'{APP_NAME} v{APP_VERSION}'
        self.di_container = None
        
    def build(self):
        """Build the application UI"""
        try:
            logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
            
            # Initialize dependency injection
            from app.dependency_injection import DIContainer
            self.di_container = DIContainer()
            self.di_container.initialize_all()
            
            # Setup RTL support for Arabic
            Window.softinput_mode = 'below_target'
            
            # Apply theme
            self._apply_theme()
            
            # Initialize navigation
            from app.presentation.navigation.navigation_manager import NavigationManager
            self.navigation_manager = NavigationManager()
            
            # Load KV files
            self._load_kv_files()
            
            logger.info("Application built successfully")
            
            return self.navigation_manager.get_root_widget()
            
        except Exception as e:
            logger.critical(f"Failed to build application: {e}", exc_info=True)
            raise
    
    def _apply_theme(self):
        """Apply application theme"""
        try:
            from app.config.app_config import AppConfig
            config = AppConfig()
            theme = config.get('theme', 'dark')
            
            if theme == 'dark':
                Window.clearcolor = (0.12, 0.12, 0.12, 1)
            else:
                Window.clearcolor = (0.95, 0.95, 0.95, 1)
            
            logger.info(f"Theme '{theme}' applied")
            
        except Exception as e:
            logger.warning(f"Failed to apply theme: {e}")
            Window.clearcolor = (0.12, 0.12, 0.12, 1)
    
    def _load_kv_files(self):
        """Load all KV files"""
        try:
            import os as _os
            
            kv_dir = _os.path.join(_os.path.dirname(__file__), 'app', 'presentation', 'screens')
            
            screens = ['downloader', 'downloads', 'models', 'settings', 'about']
            for screen in screens:
                kv_file = _os.path.join(kv_dir, screen, f'{screen}_screen.kv')
                if _os.path.exists(kv_file):
                    Builder.load_file(kv_file)
                    logger.debug(f"Loaded KV: {kv_file}")
                else:
                    logger.warning(f"KV file not found: {kv_file}")
            
            logger.info("All KV files loaded")
            
        except Exception as e:
            logger.error(f"Failed to load KV files: {e}")
    
    def on_start(self):
        """Called when application starts"""
        logger.info(f"{APP_NAME} started successfully")
    
    def on_pause(self):
        """Called when application is paused"""
        return True
    
    def on_resume(self):
        """Called when application resumes"""
        pass
    
    def on_stop(self):
        """Called when application stops"""
        logger.info("Application stopping")
        if self.di_container:
            self.di_container.shutdown()
        logger.info("Application stopped")


if __name__ == '__main__':
    try:
        app = DownSuVidApp()
        app.run()
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)