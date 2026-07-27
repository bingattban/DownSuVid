"""
Notification Service Module
"""

from typing import Optional
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.config.app_config import AppConfig
from app.config.constants import (
    NOTIFICATION_CHANNEL_ID,
    NOTIFICATION_CHANNEL_NAME,
    NOTIFICATION_ID_DOWNLOAD,
    NOTIFICATION_ID_MODEL,
)


class NotificationService(LoggerMixin):
    """Service for managing notifications"""
    
    def __init__(self):
        self.config = AppConfig()
        self._android_notification = None
        self.logger.info("NotificationService initialized")
    
    async def initialize(self) -> bool:
        """Initialize notification service"""
        try:
            from kivy.utils import platform
            
            if platform == 'android':
                await self._init_android_notifications()
            
            self.logger.info("Notification service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize notifications: {e}")
            return False
    
    async def _init_android_notifications(self):
        """Initialize Android notifications"""
        try:
            from android import mActivity
            from android.app import NotificationChannel, NotificationManager
            from android.os import Build
            
            if Build.VERSION.SDK_INT >= 26:
                channel = NotificationChannel(
                    NOTIFICATION_CHANNEL_ID,
                    NOTIFICATION_CHANNEL_NAME,
                    NotificationManager.IMPORTANCE_LOW
                )
                channel.setDescription("إشعارات التحميل")
                
                notification_manager = mActivity.getSystemService(
                    NotificationManager
                )
                notification_manager.createNotificationChannel(channel)
                
                self.logger.info("Android notification channel created")
                
        except ImportError:
            self.logger.debug("Android notification not available (not on Android)")
        except Exception as e:
            self.logger.warning(f"Failed to init Android notifications: {e}")
    
    async def show_download_progress(self, download_id: str, title: str,
                                    progress: float, status: str = "downloading"):
        """
        Show download progress notification
        
        Args:
            download_id: Download ID
            title: Download title
            progress: Progress percentage
            status: Download status
        """
        if not await self._is_enabled():
            return
        
        try:
            from kivy.utils import platform
            
            if platform == 'android':
                await self._show_android_notification(
                    NOTIFICATION_ID_DOWNLOAD,
                    f"جاري تحميل: {title}",
                    f"{progress:.1f}% - {status}",
                    progress
                )
            
        except Exception as e:
            self.logger.error(f"Failed to show notification: {e}")
    
    async def show_download_complete(self, title: str):
        """
        Show download complete notification
        
        Args:
            title: Download title
        """
        if not await self._is_enabled():
            return
        
        try:
            from kivy.utils import platform
            
            if platform == 'android':
                await self._show_android_notification(
                    NOTIFICATION_ID_DOWNLOAD,
                    "تم التحميل بنجاح",
                    f"اكتمل تحميل: {title}",
                    100
                )
            
        except Exception as e:
            self.logger.error(f"Failed to show notification: {e}")
    
    async def show_download_error(self, title: str, error: str):
        """
        Show download error notification
        
        Args:
            title: Download title
            error: Error message
        """
        if not await self._is_enabled():
            return
        
        try:
            from kivy.utils import platform
            
            if platform == 'android':
                await self._show_android_notification(
                    NOTIFICATION_ID_DOWNLOAD,
                    "فشل التحميل",
                    f"{title}: {error}",
                    0
                )
            
        except Exception as e:
            self.logger.error(f"Failed to show notification: {e}")
    
    async def show_model_download_progress(self, model_name: str, progress: float):
        """
        Show model download progress
        
        Args:
            model_name: Model name
            progress: Progress percentage
        """
        if not await self._is_enabled():
            return
        
        try:
            from kivy.utils import platform
            
            if platform == 'android':
                await self._show_android_notification(
                    NOTIFICATION_ID_MODEL,
                    f"جاري تحميل النموذج: {model_name}",
                    f"{progress:.1f}%",
                    progress
                )
            
        except Exception as e:
            self.logger.error(f"Failed to show notification: {e}")
    
    async def _show_android_notification(self, notification_id: int, 
                                        title: str, message: str, progress: float):
        """Show Android notification"""
        try:
            from android.app import NotificationBuilder, PendingIntent
            from android.content import Intent
            from android.graphics import Color
            
            # Create intent
            intent = Intent()
            pending_intent = PendingIntent.getActivity(
                mActivity, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT
            )
            
            # Build notification
            builder = NotificationBuilder(mActivity, NOTIFICATION_CHANNEL_ID)
            builder.setContentTitle(title)
            builder.setContentText(message)
            builder.setSmallIcon(android.R.drawable.stat_sys_download)
            builder.setContentIntent(pending_intent)
            builder.setAutoCancel(True)
            builder.setProgress(100, int(progress), progress == 100)
            
            if progress == 100:
                builder.setOngoing(False)
            else:
                builder.setOngoing(True)
            
            # Show notification
            notification_manager = mActivity.getSystemService(
                NotificationManager
            )
            notification_manager.notify(notification_id, builder.build())
            
        except Exception as e:
            self.logger.warning(f"Android notification failed: {e}")
    
    async def cancel_notification(self, notification_id: int):
        """Cancel a notification"""
        try:
            from kivy.utils import platform
            
            if platform == 'android':
                notification_manager = mActivity.getSystemService(
                    NotificationManager
                )
                notification_manager.cancel(notification_id)
                
        except Exception as e:
            self.logger.warning(f"Failed to cancel notification: {e}")
    
    async def cancel_all(self):
        """Cancel all notifications"""
        await self.cancel_notification(NOTIFICATION_ID_DOWNLOAD)
        await self.cancel_notification(NOTIFICATION_ID_MODEL)
    
    async def _is_enabled(self) -> bool:
        """Check if notifications are enabled"""
        return self.config.get('notification_enabled', True)