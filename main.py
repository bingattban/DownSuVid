# DownSuVid - Video Downloader Application
import os
import sys
import sqlite3
import threading
from pathlib import Path
from datetime import datetime

from kivy.config import Config
Config.set('kivy', 'log_level', 'info')
Config.set('kivy', 'exit_on_escape', 0)
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.clock import Clock, mainthread
from kivy.properties import ListProperty

APP_NAME = "DownSuVid"
APP_VERSION = "1.0.0"
STORAGE_ROOT = "DownSuVid"

COLOR_PRIMARY = (0.0, 0.59, 0.53, 1)
COLOR_PRIMARY_DARK = (0.0, 0.47, 0.42, 1)
COLOR_ACCENT = (1.0, 0.76, 0.03, 1)
COLOR_BG_DARK = (0.12, 0.12, 0.12, 1)
COLOR_BG_LIGHT = (0.95, 0.95, 0.95, 1)
COLOR_SURFACE_DARK = (0.18, 0.18, 0.18, 1)
COLOR_ERROR = (0.96, 0.26, 0.21, 1)
COLOR_SUCCESS = (0.3, 0.69, 0.31, 1)
COLOR_WARNING = (1.0, 0.76, 0.03, 1)
COLOR_TEXT_PRIMARY = (1.0, 1.0, 1.0, 0.87)
COLOR_TEXT_SECONDARY = (1.0, 1.0, 1.0, 0.60)

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
        db_dir = get_storage_path("Database")
        db_path = os.path.join(db_dir, "downsuviid.db")
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        cursor = self._connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                action TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
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

class SettingsManager:
    _instance = None
    _defaults = {'theme': 'dark', 'video_quality': '720p'}
    
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
        for key, value in self._defaults.items():
            existing = self._db.execute("SELECT value FROM settings WHERE key = ?", (key,))
            if not existing:
                self._db.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
    
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

class HistoryManager:
    def __init__(self):
        self._db = DatabaseManager()
    
    def add(self, url, title=None, action="download"):
        self._db.execute(
            "INSERT INTO history (url, title, action) VALUES (?, ?, ?)",
            (url, title, action)
        )
    
    def get_recent(self, limit=20):
        result = self._db.execute("SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,))
        return result or []

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
            options = {'quiet': True, 'no_warnings': True, 'skip_download': True}
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
        title = Label(
            text='DownSuVid',
            font_size=sp(22),
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(title)
        
        self.url_input = TextInput(
            hint_text='Enter video URL...',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(45),
            multiline=False,
            background_color=COLOR_SURFACE_DARK,
            foreground_color=COLOR_TEXT_PRIMARY,
            padding=[dp(10), dp(10)]
        )
        self.add_widget(self.url_input)
        
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(8))
        
        analyze_btn = Button(
            text='Analyze',
            background_color=COLOR_PRIMARY,
            on_press=self._analyze_url
        )
        btn_row.add_widget(analyze_btn)
        
        download_btn = Button(
            text='Download',
            background_color=COLOR_ACCENT,
            on_press=self._start_download
        )
        btn_row.add_widget(download_btn)
        
        settings_btn = Button(
            text='Settings',
            background_color=COLOR_PRIMARY_DARK,
            on_press=self._show_settings
        )
        btn_row.add_widget(settings_btn)
        
        self.add_widget(btn_row)
        
        scroll = ScrollView(size_hint_y=1)
        self.info_label = Label(
            text='Ready\n\nEnter a URL and click Analyze',
            font_size=sp(12),
            color=COLOR_TEXT_SECONDARY,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.info_label.bind(texture_size=self.info_label.setter('size'))
        scroll.add_widget(self.info_label)
        self.add_widget(scroll)
        
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(8))
        self.add_widget(self.progress_bar)
        
        self.status_label = Label(
            text='Ready',
            font_size=sp(11),
            color=COLOR_TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(self.status_label)
    
    def _analyze_url(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'Please enter a URL'
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
                    
                    self.info_label.text = f"Title: {title}\nUploader: {uploader}\nDuration: {duration}\n\nReady to download!"
                    self.status_label.text = 'Ready to download'
                else:
                    self.status_label.text = 'Failed to analyze'
            
            update_ui()
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _start_download(self, instance):
        if not self.current_info:
            self.status_label.text = 'Analyze URL first'
            return
        
        url = self.current_info.get('webpage_url', self.url_input.text)
        quality = SettingsManager().get('video_quality', '720p')
        output_path = get_storage_path("Videos")
        
        self.status_label.text = 'Downloading...'
        
        def progress_callback(progress):
            @mainthread
            def update():
                pct = progress.get('percentage', 0)
                speed = progress.get('speed', 0)
                self.progress_bar.value = pct
                speed_str = format_file_size(int(speed)) + '/s' if speed else ''
                self.status_label.text = f'{pct:.1f}% | {speed_str}'
            update()
        
        def do_download():
            success = self.download_engine.download_video(url, output_path, quality, progress_callback)
            
            @mainthread
            def update_ui():
                if success:
                    self.status_label.text = 'Download completed!'
                    HistoryManager().add(url=url, title=self.current_info.get('title'))
                else:
                    self.status_label.text = 'Download failed'
            update_ui()
        
        threading.Thread(target=do_download, daemon=True).start()
    
    def _show_settings(self, instance):
        settings = SettingsManager()
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        theme_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))
        theme_layout.add_widget(Label(text='Dark Mode', color=COLOR_TEXT_PRIMARY, size_hint_x=0.6))
        theme_switch = Switch(active=settings.get('theme') == 'dark', size_hint_x=0.4)
        theme_switch.bind(active=lambda s, v: settings.set('theme', 'dark' if v else 'light'))
        theme_layout.add_widget(theme_switch)
        content.add_widget(theme_layout)
        
        quality_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))
        quality_layout.add_widget(Label(text='Quality', color=COLOR_TEXT_PRIMARY, size_hint_x=0.4))
        quality_spinner = Spinner(
            text=settings.get('video_quality', '720p'),
            values=['1080p', '720p', '480p', '360p'],
            size_hint_x=0.6
        )
        quality_spinner.bind(text=lambda s, v: settings.set('video_quality', v))
        quality_layout.add_widget(quality_spinner)
        content.add_widget(quality_layout)
        
        content.add_widget(Label(
            text=f'DownSuVid v{APP_VERSION}',
            font_size=sp(11),
            color=COLOR_TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(40),
            halign='center'
        ))
        
        scroll = ScrollView()
        scroll.add_widget(content)
        
        popup = Popup(title='Settings', content=scroll, size_hint=(0.9, 0.7))
        popup.open()

class DownSuVidApp(App):
    primary_color = ListProperty(list(COLOR_PRIMARY))
    surface_color = ListProperty(list(COLOR_SURFACE_DARK))
    
    def build(self):
        self.title = f'{APP_NAME} v{APP_VERSION}'
        Window.clearcolor = COLOR_BG_DARK
        return MainScreen()

if __name__ == '__main__':
    try:
        DownSuVidApp().run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
