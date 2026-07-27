"""
Settings Screen Module
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineListItem
from kivy.clock import Clock
import asyncio

from app.utils.logger import LoggerMixin
from app.services.settings.settings_service import SettingsService
from app.services.storage.storage_service import StorageService


class SettingsScreen(MDScreen, LoggerMixin):
    """Screen for application settings"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_service = SettingsService()
        self.storage_service = StorageService()
        self.logger.info("SettingsScreen initialized")
    
    def on_enter(self):
        """Load settings when screen is displayed"""
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self._load_settings()))
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self._load_storage_info()))
    
    async def _load_settings(self):
        """Load current settings"""
        try:
            theme = await self.settings_service.get_theme()
            quality = await self.settings_service.get_video_quality()
            max_parallel = await self.settings_service.get_max_parallel_downloads()
            auto_resume = await self.settings_service.get_auto_resume()
            auto_clean = await self.settings_service.get_auto_clean_cache()
            
            Clock.schedule_once(lambda dt: self._update_settings_ui(
                theme, quality, max_parallel, auto_resume, auto_clean
            ))
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
    
    def _update_settings_ui(self, theme: str, quality: str, 
                           max_parallel: int, auto_resume: bool, 
                           auto_clean: bool):
        """Update settings UI"""
        self.ids.dark_mode_switch.active = (theme == 'dark')
        self.ids.quality_btn.text = quality
        self.ids.parallel_slider.value = max_parallel
        self.ids.auto_resume_switch.active = auto_resume
        self.ids.auto_clean_switch.active = auto_clean
    
    async def _load_storage_info(self):
        """Load storage information"""
        try:
            stats = await self.storage_service.get_storage_stats()
            
            from app.utils.file_utils import FileUtils
            used_space = FileUtils.format_file_size(stats.get('used_space', 0))
            
            Clock.schedule_once(
                lambda dt: setattr(
                    self.ids.storage_info, 
                    'text', 
                    f'المساحة المستخدمة: {used_space}'
                )
            )
        except Exception as e:
            self.logger.error(f"Failed to load storage info: {e}")
    
    def toggle_theme(self):
        """Toggle dark/light theme"""
        is_dark = self.ids.dark_mode_switch.active
        theme = 'dark' if is_dark else 'light'
        
        asyncio.ensure_future(self.settings_service.set_theme(theme))
        
        # Apply theme immediately
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if is_dark:
            app.theme_cls.theme_style = "Dark"
        else:
            app.theme_cls.theme_style = "Light"
    
    def show_quality_dialog(self):
        """Show quality selection dialog"""
        from app.config.constants import SUPPORTED_VIDEO_QUALITIES
        
        dialog = MDDialog(
            title="اختر الجودة",
            type="simple",
            items=[
                OneLineListItem(
                    text=q,
                    on_release=lambda x=q: self._set_quality(x, dialog)
                )
                for q in SUPPORTED_VIDEO_QUALITIES
            ]
        )
        dialog.open()
    
    def _set_quality(self, quality: str, dialog: MDDialog):
        """Set video quality"""
        asyncio.ensure_future(self.settings_service.set_video_quality(quality))
        self.ids.quality_btn.text = quality
        dialog.dismiss()
    
    def set_parallel_downloads(self, value: float):
        """Set parallel downloads count"""
        count = int(value)
        asyncio.ensure_future(
            self.settings_service.set_max_parallel_downloads(count)
        )
    
    def toggle_auto_resume(self):
        """Toggle auto resume"""
        enabled = self.ids.auto_resume_switch.active
        asyncio.ensure_future(
            self.settings_service.set_auto_resume(enabled)
        )
    
    def toggle_auto_clean(self):
        """Toggle auto clean"""
        enabled = self.ids.auto_clean_switch.active
        asyncio.ensure_future(
            self.settings_service.set_auto_clean_cache(enabled)
        )
    
    def clean_temp_files(self):
        """Clean temporary files"""
        async def clean():
            result = await self.storage_service.clean_all_temp()
            Clock.schedule_once(
                lambda dt: self._show_clean_result(result)
            )
        
        asyncio.ensure_future(clean())
    
    def _show_clean_result(self, result: dict):
        """Show clean result dialog"""
        dialog = MDDialog(
            title="تنظيف الملفات",
            text=f"تم حذف {result.get('total_files', 0)} ملف",
            buttons=[
                MDFlatButton(
                    text="موافق",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()