"""
DownSuVid - Video Downloader Application
Simplified version for initial build
"""

import os
import sys

# Configure Kivy before any other imports
from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')
Config.set('kivy', 'exit_on_escape', 0)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

# Set window size for desktop testing
Window.size = (400, 700)


class DownloaderScreen(BoxLayout):
    """Main downloader screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        
        # Title
        title = Label(
            text='DownSuVid - تحميل الفيديو',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(20),
            bold=True,
            color=(0.1, 0.6, 0.8, 1)
        )
        self.add_widget(title)
        
        # URL Input
        self.url_input = TextInput(
            hint_text='أدخل رابط الفيديو هنا...',
            size_hint_y=None,
            height=dp(50),
            multiline=False,
            font_size=dp(14)
        )
        self.add_widget(self.url_input)
        
        # Buttons
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        analyze_btn = Button(
            text='تحليل الرابط',
            on_press=self.analyze_url,
            background_color=(0.1, 0.6, 0.8, 1)
        )
        btn_layout.add_widget(analyze_btn)
        
        download_btn = Button(
            text='تحميل',
            on_press=self.start_download,
            background_color=(0.2, 0.8, 0.3, 1)
        )
        btn_layout.add_widget(download_btn)
        
        self.add_widget(btn_layout)
        
        # Progress
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(20)
        )
        self.add_widget(self.progress)
        
        # Status
        self.status_label = Label(
            text='جاهز',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(12),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(self.status_label)
        
        # Info area
        scroll = ScrollView()
        self.info_label = Label(
            text='',
            size_hint_y=None,
            text_size=(dp(350), None),
            font_size=dp(11)
        )
        self.info_label.bind(texture_size=self.info_label.setter('size'))
        scroll.add_widget(self.info_label)
        self.add_widget(scroll)
    
    def analyze_url(self, instance):
        """Analyze URL button handler"""
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'الرجاء إدخال رابط'
            return
        
        self.status_label.text = 'جاري التحليل...'
        self.progress.value = 0
        
        # Simple URL validation
        if url.startswith('http://') or url.startswith('https://'):
            self.info_label.text = f'تم تحليل الرابط:\n{url}\n\nالميزات قيد التطوير...'
            self.status_label.text = 'تم التحليل بنجاح'
            self.progress.value = 100
        else:
            self.status_label.text = 'رابط غير صالح'
            self.info_label.text = 'الرجاء إدخال رابط صحيح يبدأ بـ http:// أو https://'
    
    def start_download(self, instance):
        """Start download button handler"""
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'الرجاء إدخال رابط'
            return
        
        self.status_label.text = 'جاري التحميل...'
        
        # Simulate download progress
        from kivy.clock import Clock
        
        def update_progress(dt):
            if self.progress.value < 100:
                self.progress.value += 10
                self.status_label.text = f'جاري التحميل... {int(self.progress.value)}%'
            else:
                self.status_label.text = 'اكتمل التحميل!'
                self.info_label.text += '\nتم التحميل بنجاح (محاكاة)'
                return False
            return True
        
        self.progress.value = 0
        Clock.schedule_interval(update_progress, 0.5)


class DownSuVidApp(App):
    """Main Application"""
    
    def build(self):
        self.title = 'DownSuVid'
        return DownloaderScreen()


if __name__ == '__main__':
    try:
        DownSuVidApp().run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
