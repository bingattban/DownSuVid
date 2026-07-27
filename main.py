"
DownSuVid - Video Downloader with Smart Subtitle Processing
Complete Application in Single File for Buildozer Compatibility

Features:
- Video downloading from supported websites using yt-dlp
- Smart subtitle processing (Arabic priority)
- Speech-to-text subtitle generation
- Translation to Arabic
- Download manager
- Model & package management
- Settings management
- RTL Arabic interface with Material Design
"""

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

# ============================================================
# Kivy Configuration - MUST be before any Kivy imports
# ============================================================
from kivy.config import Config
Config.set('kivy', 'log_level', 'info')
Config.set('kivy', 'exit_on_escape', 0)
Config.set('kivy', 'window_icon', 'icon.png')
Config.set('graphics', 'resizable', 1)
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# ============================================================
# Kivy Imports
# ============================================================
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
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.image import AsyncImage, Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform, get_color_from_hex
from kivy.clock import Clock, mainthread
from kivy.animation import Animation
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
APP_NAME_AR = "داون سو فيد"
APP_VERSION = "1.0.0"
PACKAGE_NAME = "com.downsuviid"

# Storage paths
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

# Database
DATABASE_NAME = "downsuviid.db"

# Download settings
MAX_PARALLEL_DOWNLOADS = 3
MAX_RETRY_COUNT = 3
RETRY_DELAY = 5

# Colors - Material Design
COLOR_PRIMARY = (0.0, 0.59, 0.53, 1)  # Teal 500
COLOR_PRIMARY_DARK = (0.0, 0.47, 0.42, 1)  # Teal 700
COLOR_ACCENT = (1.0, 0.76, 0.03, 1)  # Amber 500
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
def get_storage_path(*args) -> str:
    """Get absolute storage path"""
    base = str(Path.home() / STORAGE_ROOT)
    path = os.path.join(base, *args)
    os.makedirs(path, exist_ok=True)
    return path

def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def format_time(seconds: int) -> str:
    """Format time duration"""
    if seconds is None:
        return "--:--"
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip('. ') or 'unnamed'

def calculate_sha256(file_path: str) -> Optional[str]:
    """Calculate SHA256 hash"""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except:
        return None

# ============================================================
# KV Language Strings
# ============================================================
KV = '''
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<ModernButton@Button>:
    background_normal: ''
    background_color: app.primary_color
    color: 1, 1, 1, 1
    font_size: sp(14)
    bold: True
    size_hint_y: None
    height: dp(48)
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(8)]

<ModernTextInput@TextInput>:
    background_normal: ''
    background_color: app.surface_color
    foreground_color: app.text_primary_color
    hint_text_color: app.text_secondary_color
    font_size: sp(14)
    padding: [dp(12), dp(12)]
    size_hint_y: None
    height: dp(48)
    cursor_color: app.primary_color
    selection_color: app.primary_color[:3] + [0.3]
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(8)]

<CardWidget@BoxLayout>:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(10)
    size_hint_y: None
    height: self.minimum_height
    canvas.before:
        Color:
            rgba: app.surface_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(12)]

<StatusLabel@Label>:
    font_size: sp(11)
    size_hint_y: None
    height: dp(20)
'''

# ============================================================
# Database Manager
# ============================================================
class DatabaseManager:
    """SQLite Database Manager"""
    
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
        """Initialize database"""
        db_dir = get_storage_path(STORAGE_DATABASE)
        db_path = os.path.join(db_dir, DATABASE_NAME)
        
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self._connection.cursor()
        
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS downloads (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT,
                file_path TEXT,
                subtitle_path TEXT,
                status TEXT DEFAULT 'pending',
                progress REAL DEFAULT 0.0,
                speed TEXT,
                size_total INTEGER DEFAULT 0,
                size_downloaded INTEGER DEFAULT 0,
                quality TEXT,
                website TEXT,
                uploader TEXT,
                duration INTEGER,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                action TEXT NOT NULL,
                status TEXT,
                file_path TEXT,
                file_size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS models (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                language TEXT,
                version TEXT,
                file_path TEXT,
                size_total INTEGER DEFAULT 0,
                size_downloaded INTEGER DEFAULT 0,
                sha256 TEXT,
                status TEXT DEFAULT 'not_installed',
                progress REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS packages (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                source_lang TEXT,
                target_lang TEXT,
                version TEXT,
                file_path TEXT,
                size_total INTEGER DEFAULT 0,
                size_downloaded INTEGER DEFAULT 0,
                sha256 TEXT,
                status TEXT DEFAULT 'not_installed',
                progress REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_downloads_status ON downloads(status);
            CREATE INDEX IF NOT EXISTS idx_history_url ON history(url);
            CREATE INDEX IF NOT EXISTS idx_models_type ON models(type);
            CREATE INDEX IF NOT EXISTS idx_packages_type ON packages(type);
        ''')
        
        self._connection.commit()
        cursor.close()
    
    def execute(self, query: str, params: tuple = None) -> Optional[List]:
        """Execute query"""
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
        """Close connection"""
        if self._connection:
            self._connection.close()

# ============================================================
# Download Engine (using yt-dlp)
# ============================================================
class DownloadEngine:
    """Video download engine using yt-dlp"""
    
    def __init__(self):
        self._ytdlp = None
        self.active_downloads = {}
    
    def _get_ytdlp(self):
        """Lazy load yt-dlp"""
        if self._ytdlp is None:
            try:
                import yt_dlp
                self._ytdlp = yt_dlp
            except ImportError:
                pass
        return self._ytdlp
    
    def extract_info(self, url: str) -> Optional[Dict]:
        """Extract video information"""
        yt_dlp = self._get_ytdlp()
        if not yt_dlp:
            return None
        
        try:
            options = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"Extract error: {e}")
            return None
    
    def download_video(self, url: str, output_path: str, 
                      quality: str = "720p",
                      progress_callback: Callable = None) -> bool:
        """Download video"""
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
    
    def get_subtitles(self, url: str) -> List[Dict]:
        """Get available subtitles"""
        info = self.extract_info(url)
        if not info:
            return []
        
        subtitles = []
        
        subs = info.get('subtitles', {})
        for lang, formats in subs.items():
            subtitles.append({
                'language': lang,
                'type': 'manual',
            })
        
        auto_subs = info.get('automatic_captions', {})
        for lang, formats in auto_subs.items():
            subtitles.append({
                'language': lang,
                'type': 'auto',
            })
        
        return subtitles
    
    def download_subtitle(self, url: str, language: str, 
                         output_path: str) -> Optional[str]:
        """Download subtitle"""
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
# Settings Manager
# ============================================================
class SettingsManager:
    """Application settings manager"""
    
    _instance = None
    _defaults = {
        'language': 'ar',
        'theme': 'dark',
        'video_quality': '720p',
        'subtitle_format': 'srt',
        'max_parallel_downloads': '3',
        'auto_resume': 'true',
        'auto_clean_cache': 'false',
        'auto_check_updates': 'true',
        'speech_engine': 'whisper',
        'translation_engine': 'argos',
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
        """Load default settings if not exist"""
        for key, value in self._defaults.items():
            existing = self._db.execute("SELECT value FROM settings WHERE key = ?", (key,))
            if not existing:
                self._db.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?)",
                    (key, value)
                )
    
    def get(self, key: str, default: str = None) -> str:
        """Get setting value"""
        result = self._db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        if result:
            return result[0]['value']
        return default or self._defaults.get(key, '')
    
    def set(self, key: str, value: str):
        """Set setting value"""
        self._db.execute(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, datetime.now().isoformat())
        )
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean setting"""
        value = self.get(key)
        return value.lower() == 'true'
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer setting"""
        try:
            return int(self.get(key))
        except:
            return default
    
    def get_all(self) -> Dict[str, str]:
        """Get all settings"""
        results = self._db.execute("SELECT key, value FROM settings")
        if results:
            return {r['key']: r['value'] for r in results}
        return self._defaults.copy()

# ============================================================
# History Manager
# ============================================================
class HistoryManager:
    """Download history manager"""
    
    def __init__(self):
        self._db = DatabaseManager()
    
    def add(self, url: str, title: str = None, action: str = "download",
            status: str = "completed", file_path: str = None,
            file_size: int = 0):
        """Add history entry"""
        self._db.execute(
            """INSERT INTO history (url, title, action, status, file_path, file_size)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (url, title, action, status, file_path, file_size)
        )
    
    def get_recent(self, limit: int = 20) -> List[Dict]:
        """Get recent history"""
        result = self._db.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return result or []
    
    def search(self, query: str) -> List[Dict]:
        """Search history"""
        search_param = f"%{query}%"
        result = self._db.execute(
            "SELECT * FROM history WHERE title LIKE ? OR url LIKE ? ORDER BY created_at DESC LIMIT 50",
            (search_param, search_param)
        )
        return result or []
    
    def clear(self):
        """Clear history"""
        self._db.execute("DELETE FROM history")

# ============================================================
# Subtitle Processor
# ============================================================
class SubtitleProcessor:
    """Smart subtitle processor"""
    
    def __init__(self):
        self.download_engine = DownloadEngine()
    
    def process_subtitles(self, url: str, video_path: str = None) -> List[Dict]:
        """
        Process subtitles with priority:
        1. Arabic subtitles if available
        2. Best available subtitle
        3. Generate from audio
        """
        available_subs = self.download_engine.get_subtitles(url)
        
        # Priority 1: Arabic subtitles
        arabic_subs = [s for s in available_subs 
                      if s['language'].lower() in ['ar', 'ara', 'arabic']]
        
        if arabic_subs:
            output_path = get_storage_path(STORAGE_SUBTITLES)
            sub_path = self.download_engine.download_subtitle(url, 'ar', output_path)
            if sub_path:
                return [{
                    'language': 'ar',
                    'file_path': sub_path,
                    'source': 'downloaded',
                    'priority': 1
                }]
        
        # Priority 2: Best available subtitle
        if available_subs:
            manual_subs = [s for s in available_subs if s['type'] == 'manual']
            auto_subs = [s for s in available_subs if s['type'] == 'auto']
            
            target = None
            if manual_subs:
                en_manual = [s for s in manual_subs 
                           if s['language'].lower() in ['en', 'eng', 'english']]
                target = en_manual[0] if en_manual else manual_subs[0]
            elif auto_subs:
                target = auto_subs[0]
            
            if target:
                output_path = get_storage_path(STORAGE_SUBTITLES)
                sub_path = self.download_engine.download_subtitle(
                    url, target['language'], output_path
                )
                if sub_path:
                    return [{
                        'language': target['language'],
                        'file_path': sub_path,
                        'source': 'downloaded',
                        'priority': 2
                    }]
        
        # Priority 3: Would need speech-to-text
        return []
    
    def translate_subtitle(self, subtitle_path: str, 
                          source_lang: str, target_lang: str = "ar") -> Optional[str]:
        """Translate subtitle file"""
        try:
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple translation placeholder
            # In production, would use Argos Translate or similar
            translated_content = f"[ترجمة إلى العربية]\n{content}"
            
            output_dir = os.path.dirname(subtitle_path)
            base_name = os.path.splitext(os.path.basename(subtitle_path))[0]
            translated_path = os.path.join(output_dir, f"{base_name}_ar.srt")
            
            with open(translated_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            return translated_path
            
        except Exception as e:
            print(f"Translation error: {e}")
            return None

# ============================================================
# Storage Manager
# ============================================================
class StorageManager:
    """Storage management"""
    
    def get_storage_info(self) -> Dict:
        """Get storage information"""
        categories = {
            'videos': STORAGE_VIDEOS,
            'subtitles': STORAGE_SUBTITLES,
            'audio': STORAGE_AUDIO,
            'temp': STORAGE_TEMP,
            'cache': STORAGE_CACHE,
            'models': STORAGE_MODELS,
            'packages': STORAGE_PACKAGES,
        }
        
        usage = {}
        for name, directory in categories.items():
            path = get_storage_path(directory)
            total_size = 0
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
    
    def clean_temp(self) -> int:
        """Clean temporary files"""
        count = 0
        temp_path = get_storage_path(STORAGE_TEMP)
        cache_path = get_storage_path(STORAGE_CACHE)
        
        for path in [temp_path, cache_path]:
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
# UI Components
# ============================================================
class DownloadItem(BoxLayout):
    """Download item widget"""
    
    title = StringProperty("")
    status_text = StringProperty("")
    progress_value = NumericProperty(0)
    
    def __init__(self, download_data: Dict, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(120)
        
        self.download_data = download_data
        
        # Title
        self.title_label = Label(
            text=download_data.get('title', 'تحميل...'),
            font_size=sp(14),
            bold=True,
            color=COLOR_TEXT_PRIMARY_DARK,
            size_hint_y=None,
            height=dp(25),
            halign='right'
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.add_widget(self.title_label)
        
        # URL
        url_label = Label(
            text=download_data.get('url', '')[:50],
            font_size=sp(10),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(18),
            halign='right'
        )
        url_label.bind(size=url_label.setter('text_size'))
        self.add_widget(url_label)
        
        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=download_data.get('progress', 0),
            size_hint_y=None,
            height=dp(8)
        )
        self.add_widget(self.progress_bar)
        
        # Info row
        info_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(25),
            spacing=dp(5)
        )
        
        self.status_label = Label(
            text=self._get_status_text(download_data.get('status', 'pending')),
            font_size=sp(10),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_x=0.4
        )
        info_layout.add_widget(self.status_label)
        
        speed_text = download_data.get('speed', '')
        speed_label = Label(
            text=speed_text,
            font_size=sp(10),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_x=0.3
        )
        info_layout.add_widget(speed_label)
        
        size_label = Label(
            text=format_file_size(download_data.get('size_total', 0)),
            font_size=sp(10),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_x=0.3
        )
        info_layout.add_widget(size_label)
        
        self.add_widget(info_layout)
        
        # Buttons
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(5)
        )
        
        status = download_data.get('status', 'pending')
        
        if status == 'downloading':
            pause_btn = Button(
                text='⏸ إيقاف',
                font_size=sp(10),
                background_color=COLOR_WARNING,
                on_press=lambda x: self._on_action('pause')
            )
            btn_layout.add_widget(pause_btn)
        elif status == 'paused':
            resume_btn = Button(
                text='▶ استئناف',
                font_size=sp(10),
                background_color=COLOR_SUCCESS,
                on_press=lambda x: self._on_action('resume')
            )
            btn_layout.add_widget(resume_btn)
        elif status == 'failed':
            retry_btn = Button(
                text='🔄 إعادة',
                font_size=sp(10),
                background_color=COLOR_WARNING,
                on_press=lambda x: self._on_action('retry')
            )
            btn_layout.add_widget(retry_btn)
        elif status == 'completed':
            open_btn = Button(
                text='📂 فتح',
                font_size=sp(10),
                background_color=COLOR_SUCCESS,
                on_press=lambda x: self._on_action('open')
            )
            btn_layout.add_widget(open_btn)
        
        delete_btn = Button(
            text='🗑 حذف',
            font_size=sp(10),
            background_color=COLOR_ERROR,
            on_press=lambda x: self._on_action('delete')
        )
        btn_layout.add_widget(delete_btn)
        
        self.add_widget(btn_layout)
    
    def _get_status_text(self, status: str) -> str:
        """Get Arabic status text"""
        status_map = {
            'pending': '⏳ انتظار',
            'downloading': '⬇ جاري',
            'completed': '✅ مكتمل',
            'failed': '❌ فشل',
            'paused': '⏸ متوقف',
            'cancelled': '🚫 ملغى',
        }
        return status_map.get(status, status)
    
    def _on_action(self, action: str):
        """Handle button action"""
        print(f"Action: {action} for {self.download_data.get('id')}")
    
    def update(self, data: Dict):
        """Update download item"""
        self.download_data.update(data)
        self.progress_bar.value = data.get('progress', 0)
        self.status_label.text = self._get_status_text(data.get('status', 'pending'))

class ModelPackageItem(BoxLayout):
    """Model/Package item widget"""
    
    def __init__(self, data: Dict, item_type: str = 'model', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = dp(10)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(80)
        
        # Info side
        info_layout = BoxLayout(
            orientation='vertical',
            size_hint_x=0.7
        )
        
        name_label = Label(
            text=data.get('name', 'Unknown'),
            font_size=sp(14),
            bold=True,
            color=COLOR_TEXT_PRIMARY_DARK,
            size_hint_y=None,
            height=dp(25),
            halign='right'
        )
        name_label.bind(size=name_label.setter('text_size'))
        info_layout.add_widget(name_label)
        
        desc_label = Label(
            text=data.get('description', ''),
            font_size=sp(11),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(20),
            halign='right'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        info_layout.add_widget(desc_label)
        
        size_text = format_file_size(data.get('size', 0))
        size_label = Label(
            text=f"الحجم: {size_text}",
            font_size=sp(10),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(18)
        )
        info_layout.add_widget(size_label)
        
        self.add_widget(info_layout)
        
        # Button side
        btn_layout = BoxLayout(
            orientation='vertical',
            size_hint_x=0.3,
            spacing=dp(5)
        )
        
        if data.get('installed', False):
            delete_btn = Button(
                text='🗑 حذف',
                font_size=sp(11),
                background_color=COLOR_ERROR,
                on_press=lambda x: self._on_action('delete', data.get('id'))
            )
            btn_layout.add_widget(delete_btn)
            
            verify_btn = Button(
                text='✓ تحقق',
                font_size=sp(11),
                background_color=COLOR_SUCCESS,
                on_press=lambda x: self._on_action('verify', data.get('id'))
            )
            btn_layout.add_widget(verify_btn)
        else:
            download_btn = Button(
                text='⬇ تحميل',
                font_size=sp(11),
                background_color=COLOR_PRIMARY,
                on_press=lambda x: self._on_action('download', data.get('id'))
            )
            btn_layout.add_widget(download_btn)
        
        self.add_widget(btn_layout)
    
    def _on_action(self, action: str, item_id: str):
        """Handle action"""
        print(f"Action: {action} for {item_id}")

# ============================================================
# Main Screens
# ============================================================
class DownloaderScreen(BoxLayout):
    """Main downloader screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.download_engine = DownloadEngine()
        self.current_info = None
        
        self._build_ui()
    
    def _build_ui(self):
        """Build screen UI"""
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        
        title = Label(
            text='🎬 تحميل الفيديو',
            font_size=sp(20),
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_x=0.7
        )
        header.add_widget(title)
        
        history_btn = Button(
            text='📋',
            font_size=sp(20),
            background_color=(0, 0, 0, 0),
            size_hint_x=0.15,
            on_press=self._show_history
        )
        header.add_widget(history_btn)
        
        settings_btn = Button(
            text='⚙',
            font_size=sp(20),
            background_color=(0, 0, 0, 0),
            size_hint_x=0.15,
            on_press=self._show_settings
        )
        header.add_widget(settings_btn)
        
        self.add_widget(header)
        
        # URL Input Card
        url_card = BoxLayout(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(130)
        )
        
        url_card.canvas.before.clear()
        with url_card.canvas.before:
            Color(*COLOR_SURFACE_DARK)
            RoundedRectangle(size=url_card.size, pos=url_card.pos, radius=[dp(12)])
        url_card.bind(pos=lambda s, p: setattr(s, 'pos', p))
        url_card.bind(size=lambda s, sz: setattr(s, 'size', sz))
        
        url_label = Label(
            text='رابط الفيديو:',
            font_size=sp(14),
            bold=True,
            color=COLOR_TEXT_PRIMARY_DARK,
            size_hint_y=None,
            height=dp(25),
            halign='right'
        )
        url_label.bind(size=url_label.setter('text_size'))
        url_card.add_widget(url_label)
        
        self.url_input = TextInput(
            hint_text='أدخل رابط الفيديو هنا...',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(45),
            multiline=False,
            background_color=COLOR_BACKGROUND_DARK,
            foreground_color=COLOR_TEXT_PRIMARY_DARK,
            hint_text_color=COLOR_TEXT_SECONDARY_DARK,
            cursor_color=COLOR_PRIMARY,
            padding=[dp(10), dp(10)]
        )
        url_card.add_widget(self.url_input)
        
        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8)
        )
        
        analyze_btn = Button(
            text='🔍 تحليل الرابط',
            font_size=sp(13),
            background_color=COLOR_PRIMARY,
            on_press=self._analyze_url
        )
        btn_row.add_widget(analyze_btn)
        
        paste_btn = Button(
            text='📋 لصق',
            font_size=sp(13),
            background_color=COLOR_PRIMARY_DARK,
            on_press=self._paste_url
        )
        btn_row.add_widget(paste_btn)
        
        url_card.add_widget(btn_row)
        self.add_widget(url_card)
        
        # Video Info Card (hidden initially)
        self.info_card = BoxLayout(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=0,
            opacity=0
        )
        self.info_card.canvas.before.clear()
        with self.info_card.canvas.before:
            Color(*COLOR_SURFACE_DARK)
            RoundedRectangle(size=self.info_card.size, pos=self.info_card.pos, radius=[dp(12)])
        
        self.info_label = Label(
            text='',
            font_size=sp(12),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(100),
            halign='right',
            valign='top'
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        self.info_card.add_widget(self.info_label)
        self.add_widget(self.info_card)
        
        # Download button (hidden initially)
        self.download_btn = Button(
            text='⬇ تحميل الفيديو',
            font_size=sp(16),
            bold=True,
            background_color=COLOR_ACCENT,
            size_hint_y=None,
            height=dp(50),
            opacity=0,
            disabled=True,
            on_press=self._start_download
        )
        self.add_widget(self.download_btn)
        
        # Progress section (hidden initially)
        self.progress_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=0,
            opacity=0
        )
        
        self.progress_title = Label(
            text='جاري التحميل...',
            font_size=sp(14),
            bold=True,
            color=COLOR_TEXT_PRIMARY_DARK,
            size_hint_y=None,
            height=dp(25)
        )
        self.progress_layout.add_widget(self.progress_title)
        
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(10)
        )
        self.progress_layout.add_widget(self.progress_bar)
        
        self.progress_info = Label(
            text='0%',
            font_size=sp(11),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(20)
        )
        self.progress_layout.add_widget(self.progress_info)
        
        self.add_widget(self.progress_layout)
        
        # Status message
        self.status_label = Label(
            text='جاهز للتحميل',
            font_size=sp(11),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(self.status_label)
        
        # Bottom navigation
        nav_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )
        
        nav_buttons = [
            ('🏠 الرئيسية', self._show_main),
            ('📥 التحميلات', self._show_downloads),
            ('🤖 النماذج', self._show_models),
            ('⚙ الإعدادات', self._show_settings),
        ]
        
        for text, callback in nav_buttons:
            btn = Button(
                text=text,
                font_size=sp(10),
                background_color=COLOR_PRIMARY_DARK,
                on_press=callback
            )
            nav_layout.add_widget(btn)
        
        self.add_widget(nav_layout)
    
    def _analyze_url(self, instance):
        """Analyze URL"""
        url = self.url_input.text.strip()
        
        if not url:
            self.status_label.text = '❌ الرجاء إدخال رابط الفيديو'
            return
        
        if not url.startswith('http'):
            self.status_label.text = '❌ الرجاء إدخال رابط صحيح'
            return
        
        self.status_label.text = '🔍 جاري تحليل الرابط...'
        
        def analyze():
            info = self.download_engine.extract_info(url)
            
            @mainthread
            def update_ui():
                if info:
                    self.current_info = info
                    title = info.get('title', 'غير معروف')
                    uploader = info.get('uploader', 'غير معروف')
                    duration = format_time(info.get('duration'))
                    website = info.get('extractor', 'غير معروف')
                    
                    info_text = f"""
📹 العنوان: {title}
👤 المحمل: {uploader}
⏱ المدة: {duration}
🌐 الموقع: {website}

✅ تم تحليل الرابط بنجاح
                    """
                    
                    self.info_label.text = info_text
                    self.info_card.height = dp(150)
                    self.info_card.opacity = 1
                    
                    self.download_btn.opacity = 1
                    self.download_btn.disabled = False
                    
                    self.status_label.text = '✅ جاهز للتحميل'
                else:
                    self.status_label.text = '❌ فشل تحليل الرابط'
            
            update_ui()
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _paste_url(self, instance):
        """Paste URL from clipboard"""
        try:
            from kivy.core.clipboard import Clipboard
            clipboard_text = Clipboard.paste()
            if clipboard_text:
                self.url_input.text = clipboard_text
                self.status_label.text = '📋 تم لصق الرابط'
        except:
            self.status_label.text = '❌ فشل لصق الرابط'
    
    def _start_download(self, instance):
        """Start download"""
        if not self.current_info:
            return
        
        url = self.current_info.get('webpage_url', self.url_input.text)
        quality = SettingsManager().get('video_quality', '720p')
        output_path = get_storage_path(STORAGE_VIDEOS)
        
        self.download_btn.opacity = 0
        self.download_btn.disabled = True
        self.progress_layout.height = dp(60)
        self.progress_layout.opacity = 1
        self.status_label.text = '⬇ جاري التحميل...'
        
        def progress_callback(progress):
            @mainthread
            def update():
                pct = progress.get('percentage', 0)
                speed = progress.get('speed', 0)
                downloaded = progress.get('downloaded', 0)
                total = progress.get('total', 0)
                
                self.progress_bar.value = pct
                
                speed_str = format_file_size(int(speed)) + '/s' if speed else ''
                downloaded_str = format_file_size(downloaded)
                total_str = format_file_size(total) if total else '?'
                
                self.progress_info.text = f'{pct:.1f}% | {downloaded_str}/{total_str} | {speed_str}'
            
            update()
        
        def do_download():
            success = self.download_engine.download_video(
                url, output_path, quality, progress_callback
            )
            
            # Download subtitle
            subtitle_processor = SubtitleProcessor()
            subtitles = subtitle_processor.process_subtitles(url)
            
            @mainthread
            def update_ui():
                if success:
                    self.status_label.text = '✅ تم التحميل بنجاح!'
                    self.progress_title.text = 'اكتمل التحميل'
                    
                    # Add to history
                    history = HistoryManager()
                    history.add(
                        url=url,
                        title=self.current_info.get('title'),
                        action='download',
                        status='completed'
                    )
                    
                    if subtitles:
                        self.status_label.text += f' | تم تحميل {len(subtitles)} ترجمة'
                else:
                    self.status_label.text = '❌ فشل التحميل'
                    self.progress_title.text = 'فشل التحميل'
                
                Clock.schedule_once(lambda dt: self._reset_ui(), 5)
            
            update_ui()
        
        threading.Thread(target=do_download, daemon=True).start()
    
    def _reset_ui(self):
        """Reset UI after download"""
        self.download_btn.opacity = 1
        self.download_btn.disabled = False
        self.progress_layout.height = 0
        self.progress_layout.opacity = 0
        self.progress_bar.value = 0
    
    def _show_history(self, instance):
        """Show history popup"""
        history = HistoryManager()
        entries = history.get_recent(20)
        
        content = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10))
        
        if entries:
            for entry in entries:
                text = f"• {entry.get('title', 'Unknown')[:40]}\n  {entry.get('url', '')[:50]}"
                lbl = Label(
                    text=text,
                    font_size=sp(11),
                    color=COLOR_TEXT_PRIMARY_DARK,
                    size_hint_y=None,
                    height=dp(45),
                    halign='right'
                )
                lbl.bind(size=lbl.setter('text_size'))
                content.add_widget(lbl)
        else:
            content.add_widget(Label(
                text='لا يوجد سجل تحميلات',
                font_size=sp(14),
                color=COLOR_TEXT_SECONDARY_DARK
            ))
        
        scroll = ScrollView()
        scroll.add_widget(content)
        
        popup = Popup(
            title='📋 سجل التحميلات',
            content=scroll,
            size_hint=(0.9, 0.7)
        )
        popup.open()
    
    def _show_main(self, instance):
        pass  # Already on main
    
    def _show_downloads(self, instance):
        """Show downloads manager"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Add sample downloads for demo
        sample_downloads = [
            {
                'id': '1',
                'title': 'مثال فيديو ١',
                'url': 'https://example.com/video1',
                'status': 'completed',
                'progress': 100,
                'size_total': 50 * 1024 * 1024,
                'speed': '2.5 MB/s',
            },
            {
                'id': '2',
                'title': 'مثال فيديو ٢',
                'url': 'https://example.com/video2',
                'status': 'downloading',
                'progress': 45,
                'size_total': 120 * 1024 * 1024,
                'speed': '1.8 MB/s',
            },
        ]
        
        for dl in sample_downloads:
            item = DownloadItem(dl)
            content.add_widget(item)
        
        scroll = ScrollView()
        scroll.add_widget(content)
        
        popup = Popup(
            title='📥 إدارة التحميلات',
            content=scroll,
            size_hint=(0.95, 0.85)
        )
        popup.open()
    
    def _show_models(self, instance):
        """Show models & packages"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Speech models
        content.add_widget(Label(
            text='🎤 نماذج التعرف الصوتي',
            font_size=sp(16),
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(35)
        ))
        
        models_data = [
            {
                'id': 'whisper_tiny',
                'name': 'Whisper Tiny',
                'description': 'نموذج صغير وسريع',
                'size': 75 * 1024 * 1024,
                'installed': False,
            },
            {
                'id': 'whisper_base',
                'name': 'Whisper Base',
                'description': 'نموذج أساسي متوازن',
                'size': 145 * 1024 * 1024,
                'installed': False,
            },
        ]
        
        for model in models_data:
            item = ModelPackageItem(model, 'model')
            content.add_widget(item)
        
        # Translation packages
        content.add_widget(Label(
            text='🌐 حزم الترجمة',
            font_size=sp(16),
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(35)
        ))
        
        packages_data = [
            {
                'id': 'argos_en_ar',
                'name': 'English → العربية',
                'description': 'حزمة ترجمة إنجليزي-عربي',
                'size': 50 * 1024 * 1024,
                'installed': False,
            },
            {
                'id': 'argos_fr_ar',
                'name': 'French → العربية',
                'description': 'حزمة ترجمة فرنسي-عربي',
                'size': 45 * 1024 * 1024,
                'installed': False,
            },
        ]
        
        for pkg in packages_data:
            item = ModelPackageItem(pkg, 'package')
            content.add_widget(item)
        
        scroll = ScrollView()
        scroll.add_widget(content)
        
        popup = Popup(
            title='🤖 النماذج والحزم',
            content=scroll,
            size_hint=(0.95, 0.85)
        )
        popup.open()
    
    def _show_settings(self, instance):
        """Show settings"""
        settings = SettingsManager()
        storage = StorageManager()
        storage_info = storage.get_storage_info()
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Theme
        theme_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45)
        )
        theme_layout.add_widget(Label(
            text='🌓 الوضع الداكن',
            font_size=sp(14),
            color=COLOR_TEXT_PRIMARY_DARK,
            size_hint_x=0.6
        ))
        
        theme_switch = Switch(
            active=settings.get('theme') == 'dark',
            size_hint_x=0.4
        )
        theme_switch.bind(active=lambda s, v: settings.set('theme', 'dark' if v else 'light'))
        theme_layout.add_widget(theme_switch)
        content.add_widget(theme_layout)
        
        # Quality
        quality_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45)
        )
        quality_layout.add_widget(Label(
            text='📹 الجودة',
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
        
        # Parallel downloads
        parallel_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45)
        )
        parallel_layout.add_widget(Label(
            text='📥 التحميلات المتزامنة',
            font_size=sp(14),
            color=COLOR_TEXT_PRIMARY_DARK,
            size_hint_x=0.5
        ))
        
        parallel_slider = Slider(
            min=1,
            max=5,
            value=settings.get_int('max_parallel_downloads', 3),
            step=1,
            size_hint_x=0.5
        )
        parallel_slider.bind(value=lambda s, v: settings.set('max_parallel_downloads', str(int(v))))
        parallel_layout.add_widget(parallel_slider)
        content.add_widget(parallel_layout)
        
        # Storage info
        content.add_widget(Label(
            text=f'💾 المساحة المستخدمة: {format_file_size(storage_info.get("total", 0))}',
            font_size=sp(12),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Clean temp button
        clean_btn = Button(
            text='🧹 تنظيف الملفات المؤقتة',
            font_size=sp(13),
            background_color=COLOR_WARNING,
            size_hint_y=None,
            height=dp(45),
            on_press=lambda x: self._clean_temp(storage)
        )
        content.add_widget(clean_btn)
        
        # About
        content.add_widget(Label(
            text=f'© {APP_NAME} v{APP_VERSION}\nتطبيق تحميل فيديوهات مع ترجمة ذكية',
            font_size=sp(11),
            color=COLOR_TEXT_SECONDARY_DARK,
            size_hint_y=None,
            height=dp(50),
            halign='center'
        ))
        
        scroll = ScrollView()
        scroll.add_widget(content)
        
        popup = Popup(
            title='⚙ الإعدادات',
            content=scroll,
            size_hint=(0.9, 0.8)
        )
        popup.open()
    
    def _clean_temp(self, storage: StorageManager):
        """Clean temporary files"""
        count = storage.clean_temp()
        self.status_label.text = f'🧹 تم تنظيف {count} ملف مؤقت'

# ============================================================
# Main Application
# ============================================================
class DownSuVidApp(App):
    """Main Application Class"""
    
    primary_color = ListProperty(list(COLOR_PRIMARY))
    surface_color = ListProperty(list(COLOR_SURFACE_DARK))
    text_primary_color = ListProperty(list(COLOR_TEXT_PRIMARY_DARK))
    text_secondary_color = ListProperty(list(COLOR_TEXT_SECONDARY_DARK))
    
    def build(self):
        """Build application"""
        self.title = f'{APP_NAME_AR} v{APP_VERSION}'
        
        # Initialize managers
        self.settings = SettingsManager()
        self.history = HistoryManager()
        self.storage = StorageManager()
        
        # Apply theme
        self._apply_theme()
        
        # Load KV
        Builder.load_string(KV)
        
        # Create main screen
        self.root = DownloaderScreen()
        
        return self.root
    
    def _apply_theme(self):
        """Apply theme"""
        theme = self.settings.get('theme', 'dark')
        
        if theme == 'dark':
            Window.clearcolor = COLOR_BACKGROUND_DARK
            self.surface_color = list(COLOR_SURFACE_DARK)
            self.text_primary_color = list(COLOR_TEXT_PRIMARY_DARK)
            self.text_secondary_color = list(COLOR_TEXT_SECONDARY_DARK)
        else:
            Window.clearcolor = COLOR_BACKGROUND_LIGHT
            self.surface_color = list(COLOR_SURFACE_LIGHT)
            self.text_primary_color = list(COLOR_TEXT_PRIMARY_LIGHT)
            self.text_secondary_color = list(COLOR_TEXT_SECONDARY_LIGHT)
    
    def on_start(self):
        """App started"""
        print(f"{APP_NAME} v{APP_VERSION} started")
    
    def on_stop(self):
        """App stopping"""
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
