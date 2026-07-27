"""
Navigation Manager Module
"""

from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex

from app.utils.logger import LoggerMixin
from app.presentation.screens.downloader.downloader_screen import DownloaderScreen
from app.presentation.screens.downloads.downloads_screen import DownloadsScreen
from app.presentation.screens.models.models_screen import ModelsScreen
from app.presentation.screens.settings.settings_screen import SettingsScreen
from app.config.constants import (
    COLOR_PRIMARY,
    COLOR_PRIMARY_DARK,
    COLOR_ACCENT
)


class NavigationManager(LoggerMixin):
    """Manager for application navigation"""
    
    def __init__(self):
        self.screen_manager = ScreenManager()
        self.bottom_nav = None
        self._init_navigation()
        self.logger.info("NavigationManager initialized")
    
    def _init_navigation(self):
        """Initialize navigation structure"""
        # Create bottom navigation
        self.bottom_nav = MDBottomNavigation(
            panel_color=get_color_from_hex('#1E1E1E'),
            text_color_active=get_color_from_hex('#FFFFFF'),
            text_color_normal=get_color_from_hex('#B0B0B0'),
            selected_color_background=get_color_from_hex('#2E2E2E'),
        )
        
        # Add navigation items
        self._add_nav_item(
            'downloader',
            'تحميل',
            'download',
            DownloaderScreen()
        )
        
        self._add_nav_item(
            'downloads',
            'المُحَمَّلات',
            'folder-download',
            DownloadsScreen()
        )
        
        self._add_nav_item(
            'models',
            'النماذج',
            'cpu-64-bit',
            ModelsScreen()
        )
        
        self._add_nav_item(
            'settings',
            'الإعدادات',
            'cog',
            SettingsScreen()
        )
        
        self.logger.info("Navigation items created")
    
    def _add_nav_item(self, name: str, text: str, icon: str, screen):
        """Add navigation item with screen"""
        nav_item = MDBottomNavigationItem(
            name=name,
            text=text,
            icon=icon,
        )
        
        # Add screen to item
        screen.name = name
        nav_item.add_widget(screen)
        
        # Add to bottom navigation
        self.bottom_nav.add_widget(nav_item)
        
        self.logger.debug(f"Navigation item added: {name}")
    
    def get_root_widget(self):
        """Get root widget for the application"""
        return self.bottom_nav
    
    def switch_to_screen(self, screen_name: str):
        """Switch to a specific screen"""
        try:
            self.bottom_nav.switch_tab(screen_name)
            self.logger.debug(f"Switched to screen: {screen_name}")
        except Exception as e:
            self.logger.error(f"Failed to switch screen: {e}")