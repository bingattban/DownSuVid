"""
Downloads Screen Module
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.progressbar import MDProgressBar
from kivy.clock import Clock
import asyncio

from app.utils.logger import LoggerMixin
from app.services.download.download_service import DownloadService
from app.domain.entities.download import DownloadStatus


class DownloadsScreen(MDScreen, LoggerMixin):
    """Screen for managing downloads"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.download_service = DownloadService()
        self.logger.info("DownloadsScreen initialized")
    
    def on_enter(self):
        """Refresh downloads list when screen is displayed"""
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self._refresh_downloads()))
    
    async def _refresh_downloads(self):
        """Refresh downloads list"""
        try:
            downloads = await self.download_service.get_downloads()
            
            Clock.schedule_once(lambda dt: self._update_downloads_list(downloads))
        except Exception as e:
            self.logger.error(f"Failed to refresh downloads: {e}")
    
    def _update_downloads_list(self, downloads):
        """Update downloads list UI"""
        downloads_list = self.ids.downloads_list
        downloads_list.clear_widgets()
        
        if not downloads:
            empty_label = MDLabel(
                text='لا توجد تحميلات حالياً',
                halign='center',
                font_style='Subtitle1',
                theme_text_color='Secondary',
                opacity=0.5,
                size_hint_y=None,
                height=100
            )
            downloads_list.add_widget(empty_label)
            return
        
        for download in downloads:
            card = self._create_download_card(download)
            downloads_list.add_widget(card)
    
    def _create_download_card(self, download) -> MDCard:
        """Create download item card"""
        card = MDCard(
            orientation='vertical',
            padding=15,
            spacing=10,
            elevation=5,
            radius=[15],
            size_hint_y=None,
            height=150
        )
        
        # Title
        title_label = MDLabel(
            text=download.title or 'جاري التحميل...',
            font_style='Subtitle1',
            bold=True,
            theme_text_color='Primary'
        )
        card.add_widget(title_label)
        
        # Progress bar
        progress_bar = MDProgressBar(
            value=download.progress.percentage,
            max=100,
            type='determinate'
        )
        card.add_widget(progress_bar)
        
        # Status and buttons
        status_label = MDLabel(
            text=self._get_status_text(download.status),
            font_style='Caption',
            theme_text_color='Secondary'
        )
        card.add_widget(status_label)
        
        # Action buttons
        if download.status == DownloadStatus.DOWNLOADING:
            pause_btn = MDIconButton(
                icon='pause',
                on_release=lambda x: self._pause_download(download.id)
            )
            card.add_widget(pause_btn)
        elif download.status == DownloadStatus.PAUSED:
            resume_btn = MDIconButton(
                icon='play',
                on_release=lambda x: self._resume_download(download.id)
            )
            card.add_widget(resume_btn)
        elif download.status == DownloadStatus.FAILED:
            retry_btn = MDIconButton(
                icon='refresh',
                on_release=lambda x: self._retry_download(download.id)
            )
            card.add_widget(retry_btn)
        
        return card
    
    def _get_status_text(self, status: DownloadStatus) -> str:
        """Get status text in Arabic"""
        status_map = {
            DownloadStatus.PENDING: 'قيد الانتظار',
            DownloadStatus.ANALYZING: 'جاري التحليل',
            DownloadStatus.DOWNLOADING: 'جاري التحميل',
            DownloadStatus.PROCESSING: 'جاري المعالجة',
            DownloadStatus.COMPLETED: 'مكتمل',
            DownloadStatus.FAILED: 'فشل',
            DownloadStatus.CANCELLED: 'ملغى',
            DownloadStatus.PAUSED: 'متوقف',
        }
        return status_map.get(status, 'غير معروف')
    
    def _pause_download(self, download_id: str):
        """Pause download"""
        asyncio.ensure_future(self.download_service.pause_download(download_id))
    
    def _resume_download(self, download_id: str):
        """Resume download"""
        asyncio.ensure_future(self.download_service.resume_download(download_id))
    
    def _retry_download(self, download_id: str):
        """Retry download"""
        asyncio.ensure_future(self.download_service.retry_download(download_id))
    
    def clear_completed(self):
        """Clear completed downloads"""
        asyncio.ensure_future(self.download_service.clear_completed())
        asyncio.ensure_future(self._refresh_downloads())