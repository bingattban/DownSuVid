"""
Downloader Screen Module
"""

import asyncio
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.chip import MDChip
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivy.utils import platform

from app.utils.logger import LoggerMixin
from app.services.download.download_service import DownloadService
from app.services.subtitle.subtitle_service import SubtitleService
from app.domain.entities.download import DownloadStatus


class DownloaderScreen(MDScreen, LoggerMixin):
    """Downloader screen for URL input and video info"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.download_service = DownloadService()
        self.subtitle_service = SubtitleService()
        self.current_download_id = None
        self.video_info = None
        self.logger.info("DownloaderScreen initialized")
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.logger.debug("Downloader screen entered")
    
    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            from kivy.app import App
            app = App.get_running_app()
            
            # Try to get clipboard content
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.READ_EXTERNAL_STORAGE])
            
            # Use Kivy clipboard
            from kivy.core.clipboard import Clipboard
            clipboard_text = Clipboard.paste()
            
            if clipboard_text:
                self.ids.url_input.text = clipboard_text
                self.logger.info("URL pasted from clipboard")
        except Exception as e:
            self.logger.error(f"Failed to paste URL: {e}")
            self.show_error("فشل في لصق الرابط")
    
    def clear_url(self):
        """Clear URL input"""
        self.ids.url_input.text = ""
    
    def clear_all(self):
        """Clear all inputs and results"""
        self.clear_url()
        self.hide_video_info()
        self.hide_formats()
        self.hide_subtitle_options()
        self.hide_progress()
        self.current_download_id = None
        self.video_info = None
    
    def analyze_url(self):
        """Analyze the entered URL"""
        url = self.ids.url_input.text.strip()
        
        if not url:
            self.show_error("الرجاء إدخال رابط الفيديو")
            return
        
        if not self._validate_url(url):
            self.show_error("الرابط غير صالح")
            return
        
        # Start analysis in background
        self.ids.analyze_btn.disabled = True
        self.ids.analyze_btn.text = "جاري التحليل..."
        
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self._analyze_url_async(url)))
    
    async def _analyze_url_async(self, url: str):
        """Analyze URL asynchronously"""
        try:
            self.video_info = await self.download_service.analyze_url(url)
            
            if self.video_info:
                # Update UI on main thread
                Clock.schedule_once(lambda dt: self._show_video_info())
            else:
                Clock.schedule_once(lambda dt: self.show_error("فشل في تحليل الرابط"))
        
        except Exception as e:
            self.logger.error(f"URL analysis error: {e}")
            Clock.schedule_once(lambda dt: self.show_error(f"خطأ في التحليل: {str(e)}"))
        
        finally:
            Clock.schedule_once(lambda dt: self._reset_analyze_button())
    
    def _reset_analyze_button(self):
        """Reset analyze button state"""
        self.ids.analyze_btn.disabled = False
        self.ids.analyze_btn.text = "تحليل الرابط"
    
    def _show_video_info(self):
        """Display video information"""
        if not self.video_info:
            return
        
        # Show thumbnail
        if self.video_info.thumbnail_url:
            self.ids.thumbnail.source = self.video_info.thumbnail_url
        
        # Show details
        self.ids.video_title.text = self.video_info.title or "غير معروف"
        self.ids.video_uploader.text = f"المُحَمِّل: {self.video_info.uploader or 'غير معروف'}"
        
        # Format duration
        if self.video_info.duration:
            minutes, seconds = divmod(self.video_info.duration, 60)
            hours, minutes = divmod(minutes, 60)
            if hours:
                duration_text = f"المدة: {hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_text = f"المدة: {minutes}:{seconds:02d}"
        else:
            duration_text = "المدة: غير معروف"
        self.ids.video_duration.text = duration_text
        
        self.ids.video_website.text = f"الموقع: {self.video_info.website or 'غير معروف'}"
        
        # Show video info card
        self.ids.video_info_card.opacity = 1
        self.ids.video_info_card.disabled = False
        
        # Show formats
        self._show_formats()
        
        # Show subtitle options
        self._show_subtitle_options()
        
        # Show download button
        self.ids.download_btn.opacity = 1
        self.ids.download_btn.disabled = False
    
    def _show_formats(self):
        """Display available formats"""
        if not self.video_info:
            return
        
        quality_grid = self.ids.quality_grid
        quality_grid.clear_widgets()
        
        for fmt in self.video_info.formats[:6]:  # Show top 6
            chip = MDChip(
                text=fmt.get('quality', 'Unknown'),
                icon='video',
                check=True,
                type='choice',
                callback=self._on_quality_selected
            )
            quality_grid.add_widget(chip)
        
        # Show formats card
        self.ids.formats_card.opacity = 1
        self.ids.formats_card.disabled = False
    
    def _on_quality_selected(self, chip, checked):
        """Handle quality selection"""
        if checked:
            self.selected_quality = chip.text
            self.logger.debug(f"Quality selected: {chip.text}")
    
    def _show_subtitle_options(self):
        """Display subtitle options"""
        if not self.video_info:
            return
        
        subtitle_box = self.ids.subtitle_languages_box
        subtitle_box.clear_widgets()
        
        if self.video_info.subtitle_languages:
            # Show available languages
            for lang in self.video_info.subtitle_languages[:5]:
                lang_label = MDLabel(
                    text=f"• {lang}",
                    font_style='Caption',
                    theme_text_color='Secondary'
                )
                subtitle_box.add_widget(lang_label)
        else:
            no_sub_label = MDLabel(
                text="لا توجد ترجمات متاحة",
                font_style='Caption',
                theme_text_color='Secondary'
            )
            subtitle_box.add_widget(no_sub_label)
        
        # Show subtitle card
        self.ids.subtitle_card.opacity = 1
        self.ids.subtitle_card.disabled = False
    
    def start_download(self):
        """Start video download"""
        if not self.video_info:
            self.show_error("الرجاء تحليل الرابط أولاً")
            return
        
        quality = getattr(self, 'selected_quality', '720p')
        
        # Create download
        async def create_and_start():
            download = await self.download_service.create_download(self.video_info.url)
            if download:
                self.current_download_id = download.id
                Clock.schedule_once(
                    lambda dt: asyncio.ensure_future(
                        self.download_service.start_download(download.id, quality)
                    )
                )
                Clock.schedule_once(lambda dt: self._show_progress())
        
        asyncio.ensure_future(create_and_start())
    
    def download_subtitle_only(self):
        """Download subtitle only"""
        if not self.video_info:
            self.show_error("الرجاء تحليل الرابط أولاً")
            return
        
        async def download_subs():
            subtitles = await self.subtitle_service.process_subtitles(
                self.video_info.url
            )
            if subtitles:
                Clock.schedule_once(
                    lambda dt: self.show_success(f"تم تحميل {len(subtitles)} ترجمة")
                )
            else:
                Clock.schedule_once(
                    lambda dt: self.show_error("فشل في تحميل الترجمة")
                )
        
        asyncio.ensure_future(download_subs())
    
    def generate_subtitle(self):
        """Generate subtitle from audio"""
        if not self.video_info:
            self.show_error("الرجاء تحليل الرابط أولاً")
            return
        
        self.show_info("توليد الترجمة يتطلب تحميل الفيديو أولاً")
    
    def _show_progress(self):
        """Show download progress"""
        self.ids.progress_card.opacity = 1
        self.ids.progress_card.disabled = False
        self.ids.progress_title.text = "جاري التحميل..."
        self.ids.progress_bar.value = 0
        self.ids.progress_percentage.text = "0%"
    
    def update_progress(self, percentage: float, speed: str, eta: str):
        """Update progress display"""
        self.ids.progress_bar.value = percentage
        self.ids.progress_percentage.text = f"{percentage:.1f}%"
        self.ids.progress_speed.text = speed
        self.ids.progress_eta.text = eta
    
    def pause_download(self):
        """Pause current download"""
        if self.current_download_id:
            asyncio.ensure_future(
                self.download_service.pause_download(self.current_download_id)
            )
    
    def cancel_download(self):
        """Cancel current download"""
        if self.current_download_id:
            asyncio.ensure_future(
                self.download_service.cancel_download(self.current_download_id)
            )
            self.hide_progress()
    
    def hide_video_info(self):
        """Hide video info"""
        self.ids.video_info_card.opacity = 0
        self.ids.video_info_card.disabled = True
    
    def hide_formats(self):
        """Hide formats"""
        self.ids.formats_card.opacity = 0
        self.ids.formats_card.disabled = True
    
    def hide_subtitle_options(self):
        """Hide subtitle options"""
        self.ids.subtitle_card.opacity = 0
        self.ids.subtitle_card.disabled = True
    
    def hide_progress(self):
        """Hide progress"""
        self.ids.progress_card.opacity = 0
        self.ids.progress_card.disabled = True
        self.ids.download_btn.opacity = 0
        self.ids.download_btn.disabled = True
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL"""
        import re
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )
        return bool(url_pattern.match(url))
    
    def show_error(self, message: str):
        """Show error dialog"""
        dialog = MDDialog(
            title="خطأ",
            text=message,
            buttons=[
                MDFlatButton(
                    text="موافق",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_success(self, message: str):
        """Show success dialog"""
        dialog = MDDialog(
            title="تم بنجاح",
            text=message,
            buttons=[
                MDFlatButton(
                    text="موافق",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_info(self, message: str):
        """Show info dialog"""
        dialog = MDDialog(
            title="معلومة",
            text=message,
            buttons=[
                MDFlatButton(
                    text="موافق",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_history(self):
        """Show download history"""
        # Navigate to downloads screen
        self.manager.current = 'downloads'