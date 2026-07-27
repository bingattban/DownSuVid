# DownSuVid - Video Downloader with Smart Subtitle Processing
# Complete Application in Single File for Buildozer Compatibility

import os
import sys
import json
import hashlib
import sqlite3
import threading
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any, Callable
from enum import Enum
import re

# Kivy Configuration - MUST be before any Kivy imports
from kivy.config import Config
Config.set('kivy', 'log_level', 'info')
Config.set('kivy', 'exit_on_escape', 0)
Config.set('graphics', 'resizable', 1)
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')

# Kivy Imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.clock import Clock, mainthread
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty,
    ListProperty, DictProperty, ObjectProperty
)
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.lang import Builder

# ============================================================
# Constants
# ============================================================
APP_NAME = "DownSuVid"
APP_NAME_AR = "DownSuVid"
APP_VERSION = "1.0.0"

STORAGE_ROOT = "DownSuVid"
STORAGE_DOWNLOADS = "Downloads"
STORAGE_VIDEOS = "Videos"
STORAGE_SUBTITLES = "Subtitles"
STORAGE_AUDIO = "Audio"
STORAGE_TEMP = "Temp"
STORAGE_CACHE = "Cache"
STORAGE_LOGS = "Logs"
STORAGE_DATABASE = "Database"
STORAGE_CONFIG = "Config"
STORAGE_MODELS = "Models"
STORAGE_PACKAGES = "Packages"

DATABASE_NAME = "downsuviid.db"

# Colors - Material Design
COLOR_PRIMARY = (0.0, 0.59, 0.53, 1)
COLOR_PRIMARY_DARK = (0.0, 0.47, 0.42, 1)
COLOR_ACCENT = (1.0, 0.76, 0.03, 1)
COLOR_BACKGROUND_DARK = (0.12, 0.12, 0.12, 1)
COLOR_BACKGROUND_LIGHT = (0.95, 0.95, 0.95, 1)
COLOR_SURFACE_DARK = (0.18, 0.18, 0.18, 1)
COLOR_SURFACE_LIGHT = (1.0, 1.0, 1.0, 1)
COLOR_ERROR = (0.96, 0.26, 0.21, 1)
COLOR_SUCCESS = (0.3, 0.69, 0.31, 1)
COLOR_WARNING = (1.0, 0.76, 0.03, 1)
COLOR_TEXT_PRIMARY_DARK = (1.0, 1.0, 1.0, 0.87)
COLOR_TEXT_SECONDARY_DARK = (1.0, 1.0, 1.0, 0.60)
COLOR_TEXT_PRIMARY_LIGHT = (0.0, 0.0, 0.0, 0.87)
COLOR_TEXT_SECONDARY_LIGHT = (0.0, 0.0, 0.0, 0.60)

# ============================================================
# Utility Functions
# ============================================================

def get_storage_path(*args):
    base = str(Path.home() / STORAGE_ROOT)
    path = os.path.join(base, *args)
    os.makedirs(path, exist_ok=True)
    return path

def format_file_size(size_bytes):
    if size_bytes is None:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def format_time(seconds):
    if seconds is None:
        return "--:--"
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip('. ') or 'unnamed'

# ============================================================
# Database Manager
# ============================================================

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._connection = None
        self._init_database()
    
    def _init_database(self):
        db_dir = get_storage_path(STORAGE_DATABASE)
        db_path = os.path.join(db_dir, DATABASE_NAME)
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._create_tables()
    
    def _create_tables(self):
        cursor = self._connection.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS downloads (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT,
                file_path TEXT,
                status TEXT DEFAULT 'pending',
                progress REAL DEFAULT 0.0,
                size_total INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                action TEXT NOT NULL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self._connection.commit()
        cursor.close()
    
    def execute(self, query, params=None):
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self._connection.commit()
            if query.strip().upper().startswith('SELECT'):
                return [dict(row) for row in cursor.fetchall()]
            return None
        except Exception as e:
            self._connection.rollback()
            raise e
        finally:
            cursor.close()
    
    def close(self):
        if self._connection:
            self._connection.close()

# ============================================================
# Settings Manager
# ============================================================

class SettingsManager:
    _instance = None
    _defaults = {
        'language': 'ar',
        'theme': 'dark',
        'video_quality': '720p',
        'max_parallel_downloads': '3',
        'auto_resume': 'true',
        'notification_enabled': 'true',
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._db = DatabaseManager()
        self._load_defaults()
    
    def _load_defaults(self):
        for key, value in self._defaults.items():
            existing = self._db.execute("SELECT value FROM settings WHERE key = ?", (key,))
            if not existing:
                self._db.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?)",
                    (key, value)
                )
    
    def get(self, key, default=None):
        result = self._db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        if result:
            return result[0]['value']
        return default or self._defaults.get(key, '')
    
    def set(self, key, value):
        self._db.execute(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, datetime.now().isoformat())
        )
    
    def get_bool(self, key, default=False):
        value = self.get(key)
        return value.lower() == 'true' if value else default
    
    def get_int(self, key, default=0):
        try:
            return int(self.get(key))
        except:
            return default

# ============================================================
# History Manager
# ============================================================

class HistoryManager:
    def __init__(self):
        self._db = DatabaseManager()
    
    def add(self, url, title=None, action="download", status="completed"):
        self._db.execute(
            "INSERT INTO history (url, title, action, status) VALUES (?, ?, ?, ?)",
            (url, title, action, status)
        )
    
    def get_recent(self, limit=20):
        result = self._db.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return result or []
    
    def clear(self):
        self._db.execute("DELETE FROM history")

# ============================================================
# Storage Manager
# ============================================================

class StorageManager:
    def get_storage_info(self):
        categories = {
            'videos': STORAGE_VIDEOS,
            'subtitles': STORAGE_SUBTITLES,
            'temp': STORAGE_TEMP,
            'cache': STORAGE_CACHE,
        }
        
        usage = {}
        for name, directory in categories.items():
            path = get_storage_path(directory)
            total_size = 0
            if os.path.exists(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        try:
                            total_size += os.path.getsize(fp)
                        except:
                            pass
            usage[name] = total_size
        
        usage['total'] = sum(usage.values())
        return usage
    
    def clean_temp(self):
        count = 0
        for folder in [STORAGE_TEMP, STORAGE_CACHE]:
            path = get_storage_path(folder)
            if os.path.exists(path):
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            count += 1
                    except:
                        pass
        return count

# ============================================================
# Download Engine
# ============================================================

class DownloadEngine:
    def __init__(self):
        self._ytdlp = None
    
    def _get_ytdlp(self):
        if self._ytdlp is None:
            try:
                import yt_dlp
                self._ytdlp = yt_dlp
            except ImportError:
                pass
        return self._ytdlp
    
    def extract_info(self, url):
        yt_dlp = self._get_ytdlp()
        if not yt_dlp:
            return None
        try:
            options = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"Extract error: {e}")
            return None
    
    def download_video(self, url, output_path, quality="720p", progress_callback=None):
        yt_dlp = self._get_ytdlp()
        if not yt_dlp:
            return False
        try:
            quality_value = quality.rstrip('p')
            format_string = f'bestvideo[height<={quality_value}]+bestaudio/best[height<={quality_value}]'
            
            def progress_hook(d):
                if progress_callback and d.get('status') == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    speed = d.get('speed', 0)
                    progress = {
                        'percentage': (downloaded / total * 100) if total else 0,
                        'speed': speed,
                        'downloaded': downloaded,
                        'total': total,
                        'eta': d.get('eta'),
                    }
                    progress_callback(progress)
            
            options = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'format': format_string,
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False
    
    def get_subtitles(self, url):
        info = self.extract_info(url)
        if not info:
            return []
        
        subtitles = []
        subs = info.get('subtitles', {})
        for lang in subs.keys():
            subtitles.append({'language': lang, 'type': 'manual'})
        
        auto_subs = info.get('automatic_captions', {})
        for lang in auto_subs.keys():
            subtitles.append({'language': lang, 'type': 'auto'})
        
        return subtitles
    
    def download_subtitle(self, url, language, output_path):
        yt_dlp = self._get_ytdlp()
        if not yt_dlp:
            return None
        try:
            options = {
                'outtmpl': os.path.join(output_path, '%(title)s'),
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [language],
                'subtitlesformat': 'srt',
                'quiet': True,
            }
            
            info = self.extract_info(url)
            if not info:
                return None
            
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            
            title = info.get('title', 'subtitle')
            sub_path = os.path.join(output_path, f"{title}.{language}.srt")
            
            if os.path.exists(sub_path):
                return sub_path
            
            return None
        except Exception as e:
            print(f"Subtitle download error: {e}")
            return None

# ============================================================
# KV Language
# ============================================================

KV = '''
<ModernButton@Button>:
    background_normal: ''
    background_color: (0.0, 0.59, 0.53, 1)
    color: 1, 1, 1, 1
    font_size: sp(14)
    size_hint_y: None
    height: dp(48)
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(8)]
'''

# ============================================================
# Main Screen
# ============================================================

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.download_engine = DownloadEngine()
        self.current_info = None
        self._build_ui()
    
    def _build_ui(self):
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        title = Label(
            text='DownSuVid - Video Downloader',
            font_size=sp(18),
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_x=0.6
        )
        header.add_widget(title)
        
        history_btn = Button(
            text='History',
            font_size=sp(12),
            background_color=COLOR_PRIMARY_DARK,
            size_hint_x=0.2,
            on_press=self._show_history
        )
        header.add_widget(history_btn)
        
        settings_btn = Button(
            text='Settings',
            font_size=sp(12),
            background_color=COLOR_PRIMARY_DARK,
            size_hint_x=0.2,
            on_press=self._show_settings
        )
        header.add_widget(settings_btn)
        
        self.add_widget(header)
        
        # URL Input
        url_label = Label(
            text='Video URL:',
            font_size=sp(14),
            bold=True,
            color=COLOR_TEXT_PRIMARY_DARK,
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        url_label.bind(size=url_label.setter('text_size'))
        self.add_widget(url_label)
        
        self.url_input = TextInput(
            hint_text='Enter video URL here...',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(45),
            multiline=False,
            background_color=COLOR_SURFACE_DARK,
            foreground_color=COLOR_TEXT_PRIMARY_DARK,
            hint_text_color=COLOR_TEXT_SECONDARY_DARK,
            cursor_color=COLOR_PRIMARY,
            padding=[dp(10), dp(10)]
        )
        self.add_widget(self.url_input)
        
        # Buttons
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(8))
        
        analyze_btn = Button(
            text='Analyze URL',
            font_size=sp(14),
            background_color=COLOR_PRIMARY,
            on_press=self._analyze_url
        )
        btn_row.add_widget(analyze_btn)
        
        download_btn = Button(
            text='Download',
            font_size=sp(14),
            background_color=COLOR_ACCENT,
            on_press=self._start_download
        )
        btn_row.add_widget(download_btn)
        
        self.add_widget(btn_row)
        
        # Info area
        scroll = ScrollView(size_hint_y=1)
        self.info_label = Label(
            text='Ready to download\n\nEnter a video URL and click Analyze',
            font_size=sp(12),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.info_label.bind(texture_size=self.info_label.setter('size'))
        scroll.add_widget(self.info_label)
        self.add_widget(scroll)
        
        # Progress
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(8))
        self.add_widget(self.progress_bar)
        
        # Status
        self.status_label = Label(
            text='Ready',
            font_size=sp(11),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(self.status_label)
    
    def _analyze_url(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'Please enter a URL'
            return
        
        if not url.startswith('http'):
            self.status_label.text = 'Invalid URL'
            return
        
        self.status_label.text = 'Analyzing...'
        
        def analyze():
            info = self.download_engine.extract_info(url)
            
            @mainthread
            def update_ui():
                if info:
                    self.current_info = info
                    title = info.get('title', 'Unknown')
                    uploader = info.get('uploader', 'Unknown')
                    duration = format_time(info.get('duration'))
                    website = info.get('extractor', 'Unknown')
                    
                    info_text = f"""
Title: {title}
Uploader: {uploader}
Duration: {duration}
Website: {website}

Ready to download!
                    """
                    self.info_label.text = info_text
                    self.status_label.text = 'Ready to download'
                else:
                    self.status_label.text = 'Failed to analyze URL'
            
            update_ui()
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _start_download(self, instance):
        if not self.current_info:
            self.status_label.text = 'Please analyze URL first'
            return
        
        url = self.current_info.get('webpage_url', self.url_input.text)
        quality = SettingsManager().get('video_quality', '720p')
        output_path = get_storage_path(STORAGE_VIDEOS)
        
        self.status_label.text = 'Downloading...'
        
        def progress_callback(progress):
            @mainthread
            def update():
                pct = progress.get('percentage', 0)
                speed = progress.get('speed', 0)
                downloaded = progress.get('downloaded', 0)
                total = progress.get('total', 0)
                
                self.progress_bar.value = pct
                speed_str = format_file_size(int(speed)) + '/s' if speed else ''
                self.status_label.text = f'{pct:.1f}% | {speed_str}'
            
            update()
        
        def do_download():
            success = self.download_engine.download_video(
                url, output_path, quality, progress_callback
            )
            
            @mainthread
            def update_ui():
                if success:
                    self.status_label.text = 'Download completed!'
                    HistoryManager().add(url=url, title=self.current_info.get('title'))
                else:
                    self.status_label.text = 'Download failed'
                self.progress_bar.value = 100 if success else 0
            
            update_ui()
        
        threading.Thread(target=do_download, daemon=True).start()
    
    def _show_history(self, instance):
        history = HistoryManager()
        entries = history.get_recent(20)
        
        content = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10))
        
        if entries:
            for entry in entries:
                text = f"{entry.get('title', 'Unknown')[:50]}\n{entry.get('url', '')[:60]}"
                lbl = Label(
                    text=text,
                    font_size=sp(11),
                    color=COLOR_TEXT_PRIMARY_DARK,
                    size_hint_y=None,
                    height=dp(40),
                    halign='left'
                )
                lbl.bind(size=lbl.setter('text_size'))
                content.add_widget(lbl)
        else:
            content.add_widget(Label(
                text='No download history',
                font_size=sp(14),
                color=COLOR_TEXT_SECONDARY_DARK
            ))
        
        scroll = ScrollView()
        scroll.add_widget(content)
        
        popup = Popup(title='Download History', content=scroll, size_hint=(0.9, 0.7))
        popup.open()
    
    def _show_settings(self, instance):
        settings = SettingsManager()
        storage = StorageManager()
        storage_info = storage.get_storage_info()
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Theme
        theme_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))
        theme_layout.add_widget(Label(
            text='Dark Mode',
            font_size=sp(14),
            color=COLOR_TEXT_PRIMARY_DARK,
            size_hint_x=0.6
        ))
        theme_switch = Switch(active=settings.get('theme') == 'dark', size_hint_x=0.4)
        theme_switch.bind(active=lambda s, v: settings.set('theme', 'dark' if v else 'light'))
        theme_layout.add_widget(theme_switch)
        content.add_widget(theme_layout)
        
        # Quality
        quality_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))
        quality_layout.add_widget(Label(
            text='Quality',
            font_size=sp(14),
            color=COLOR_TEXT_PRIMARY_DARK,
            size_hint_x=0.4
        ))
        quality_spinner = Spinner(
            text=settings.get('video_quality', '720p'),
            values=['1080p', '720p', '480p', '360p'],
            size_hint_x=0.6
        )
        quality_spinner.bind(text=lambda s, v: settings.set('video_quality', v))
        quality_layout.add_widget(quality_spinner)
        content.add_widget(quality_layout)
        
        # Storage info
        content.add_widget(Label(
            text=f'Storage used: {format_file_size(storage_info.get("total", 0))}',
            font_size=sp(12),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Clean button
        clean_btn = Button(
            text='Clean Temporary Files',
            font_size=sp(13),
            background_color=COLOR_WARNING,
            size_hint_y=None,
            height=dp(45),
            on_press=lambda x: self._clean_temp(storage)
        )
        content.add_widget(clean_btn)
        
        # About
        content.add_widget(Label(
            text=f'{APP_NAME} v{APP_VERSION}\nVideo Downloader Application',
            font_size=sp(11),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(50),
            halign='center'
        ))
        
        scroll = ScrollView()
        scroll.add_widget(content)
        
        popup = Popup(title='Settings', content=scroll, size_hint=(0.9, 0.8))
        popup.open()
    
    def _clean_temp(self, storage):
        count = storage.clean_temp()
        self.status_label.text = f'Cleaned {count} temporary files'

# ============================================================
# Main Application
# ============================================================

class DownSuVidApp(App):
    primary_color = ListProperty(list(COLOR_PRIMARY))
    surface_color = ListProperty(list(COLOR_SURFACE_DARK))
    text_primary_color = ListProperty(list(COLOR_TEXT_PRIMARY_DARK))
    text_secondary_color = ListProperty(list(COLOR_TEXT_SECONDARY_DARK))
    
    def build(self):
        self.title = f'{APP_NAME} v{APP_VERSION}'
        
        # Apply theme
        settings = SettingsManager()
        theme = settings.get('theme', 'dark')
        
        if theme == 'dark':
            Window.clearcolor = COLOR_BACKGROUND_DARK
        else:
            Window.clearcolor = COLOR_BACKGROUND_LIGHT
        
        # Load KV
        Builder.load_string(KV)
        
        # Return main screen
        return MainScreen()
    
    def on_start(self):
        print(f"{APP_NAME} v{APP_VERSION} started")
    
    def on_stop(self):
        print("App stopping")

# ============================================================
# Entry Point
# ============================================================

if __name__ == '__main__':
    try:
        DownSuVidApp().run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
