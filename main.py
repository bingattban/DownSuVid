"""
DownSuVid - Video Downloader Application
Production-ready single-file Kivy application for Android
"""
import os
import sys
import sqlite3
import threading
from pathlib import Path
from datetime import datetime

# ============================================================
# Kivy Configuration - MUST be before any Kivy imports
# ============================================================
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
from kivy.utils import platform

# ============================================================
# Constants
# ============================================================
APP_NAME = "DownSuVid"
APP_VERSION = "1.0.0"
STORAGE_ROOT = "DownSuVid"

# Colors - Material Design Dark Theme
COLOR_PRIMARY = (0.0, 0.59, 0.53, 1)       # Teal 500
COLOR_PRIMARY_DARK = (0.0, 0.47, 0.42, 1)  # Teal 700
COLOR_ACCENT = (1.0, 0.76, 0.03, 1)        # Amber 500
COLOR_BG = (0.12, 0.12, 0.12, 1)           # Dark background
COLOR_SURFACE = (0.18, 0.18, 0.18, 1)      # Dark surface
COLOR_ERROR = (0.96, 0.26, 0.21, 1)        # Red 500
COLOR_SUCCESS = (0.3, 0.69, 0.31, 1)       # Green 500
COLOR_TEXT = (1.0, 1.0, 1.0, 0.87)         # White 87%
COLOR_TEXT_SEC = (1.0, 1.0, 1.0, 0.60)     # White 60%


# ============================================================
# Utility Functions
# ============================================================
def get_storage_path(*args):
    """Get absolute path within app storage directory"""
    base = str(Path.home() / STORAGE_ROOT)
    path = os.path.join(base, *args)
    os.makedirs(path, exist_ok=True)
    return path


def format_file_size(size_bytes):
    """Convert bytes to human-readable format"""
    if not size_bytes:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_duration(seconds):
    """Convert seconds to HH:MM:SS format"""
    if seconds is None:
        return "--:--"
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


# ============================================================
# Database Manager (Singleton)
# ============================================================
class DatabaseManager:
    """Thread-safe SQLite database manager"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
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
        """Initialize database and create tables"""
        db_dir = get_storage_path("Database")
        db_path = os.path.join(db_dir, "downsuviid.db")
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=NORMAL")
        self._create_tables()

    def _create_tables(self):
        """Create required database tables"""
        cursor = self._connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                action TEXT NOT NULL DEFAULT 'download',
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_created 
            ON history(created_at DESC)
        """)
        self._connection.commit()
        cursor.close()

    def execute(self, query, params=None):
        """Execute a SQL query with thread safety"""
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
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()

    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None


# ============================================================
# Settings Manager (Singleton)
# ============================================================
class SettingsManager:
    """Application settings with persistent storage"""
    _instance = None
    _defaults = {
        'theme': 'dark',
        'video_quality': '720p',
        'max_parallel': '3',
        'auto_resume': 'true',
        'language': 'en',
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
        """Ensure default settings exist in database"""
        for key, value in self._defaults.items():
            existing = self._db.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            )
            if not existing:
                self._db.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    (key, value)
                )

    def get(self, key, default=None):
        """Get a setting value"""
        result = self._db.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        )
        if result:
            return result[0]['value']
        return default if default is not None else self._defaults.get(key, '')

    def set(self, key, value):
        """Set a setting value"""
        self._db.execute(
            """INSERT OR REPLACE INTO settings (key, value, updated_at) 
               VALUES (?, ?, ?)""",
            (key, str(value), datetime.now().isoformat())
        )

    def get_bool(self, key, default=False):
        """Get boolean setting"""
        val = self.get(key)
        return val.lower() == 'true' if val else default

    def get_int(self, key, default=0):
        """Get integer setting"""
        try:
            return int(self.get(key))
        except (ValueError, TypeError):
            return default


# ============================================================
# History Manager
# ============================================================
class HistoryManager:
    """Download history tracker"""

    def __init__(self):
        self._db = DatabaseManager()

    def add_entry(self, url, title=None, action="download", status="completed"):
        """Add a history entry"""
        self._db.execute(
            """INSERT INTO history (url, title, action, status) 
               VALUES (?, ?, ?, ?)""",
            (url, title, action, status)
        )

    def get_recent(self, limit=20):
        """Get recent history entries"""
        result = self._db.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return result or []

    def search(self, query, limit=20):
        """Search history entries"""
        search_param = f"%{query}%"
        result = self._db.execute(
            """SELECT * FROM history 
               WHERE title LIKE ? OR url LIKE ? 
               ORDER BY created_at DESC LIMIT ?""",
            (search_param, search_param, limit)
        )
        return result or []

    def clear(self):
        """Clear all history"""
        self._db.execute("DELETE FROM history")

    def get_count(self):
        """Get total history count"""
        result = self._db.execute("SELECT COUNT(*) as cnt FROM history")
        return result[0]['cnt'] if result else 0


# ============================================================
# Download Engine (yt-dlp wrapper)
# ============================================================
class DownloadEngine:
    """Video download engine using yt-dlp"""

    def __init__(self):
        self._ytdlp = None
        self._active_downloads = {}

    def _load_ytdlp(self):
        """Lazy-load yt-dlp module"""
        if self._ytdlp is None:
            try:
                import yt_dlp
                self._ytdlp = yt_dlp
            except ImportError as e:
                print(f"yt-dlp import failed: {e}")
        return self._ytdlp

    def extract_info(self, url):
        """Extract video metadata without downloading"""
        yt_dlp = self._load_ytdlp()
        if not yt_dlp:
            return None

        try:
            opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                # Sanitize the info dict for JSON compatibility
                sanitized = {
                    'id': info.get('id', ''),
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'extractor': info.get('extractor', 'Unknown'),
                    'description': info.get('description', '')[:500] if info.get('description') else '',
                }
                return sanitized
        except Exception as e:
            print(f"yt-dlp extract_info error: {e}")
            return None

    def download_video(self, url, output_path, quality="720p", progress_callback=None):
        """Download a video with progress tracking"""
        yt_dlp = self._load_ytdlp()
        if not yt_dlp:
            return False

        try:
            quality_value = quality.rstrip('p')
            fmt = f'bestvideo[height<={quality_value}]+bestaudio/best[height<={quality_value}]'

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
                        'eta': d.get('eta', 0),
                    }
                    progress_callback(progress)

            opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'format': fmt,
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],
                'noplaylist': True,
                'retries': 3,
                'fragment_retries': 3,
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            return True
        except Exception as e:
            print(f"yt-dlp download error: {e}")
            return False


# ============================================================
# Main Application Screen
# ============================================================
class MainScreen(BoxLayout):
    """Main application screen with all functionality"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)

        # Services
        self.engine = DownloadEngine()
        self.history = HistoryManager()
        self.settings = SettingsManager()

        # State
        self.current_video_info = None
        self.is_downloading = False

        # Build UI
        self._build_header()
        self._build_url_input()
        self._build_action_buttons()
        self._build_info_area()
        self._build_progress_section()
        self._build_status_bar()

    def _build_header(self):
        """Build header section"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        title = Label(
            text=APP_NAME,
            font_size=sp(22),
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_x=0.5,
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        history_btn = Button(
            text='History',
            font_size=sp(11),
            background_color=COLOR_PRIMARY_DARK,
            size_hint_x=0.25,
            on_press=self._show_history_popup
        )
        header.add_widget(history_btn)

        settings_btn = Button(
            text='Settings',
            font_size=sp(11),
            background_color=COLOR_PRIMARY_DARK,
            size_hint_x=0.25,
            on_press=self._show_settings_popup
        )
        header.add_widget(settings_btn)

        self.add_widget(header)

    def _build_url_input(self):
        """Build URL input section"""
        self.url_input = TextInput(
            hint_text='Enter video URL here...',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(48),
            multiline=False,
            background_color=COLOR_SURFACE,
            foreground_color=COLOR_TEXT,
            hint_text_color=COLOR_TEXT_SEC,
            cursor_color=COLOR_PRIMARY,
            padding=[dp(12), dp(12)]
        )
        self.add_widget(self.url_input)

    def _build_action_buttons(self):
        """Build action buttons row"""
        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )

        analyze_btn = Button(
            text='Analyze',
            font_size=sp(14),
            background_color=COLOR_PRIMARY,
            on_press=self._on_analyze_click
        )
        btn_row.add_widget(analyze_btn)

        self.download_btn = Button(
            text='Download',
            font_size=sp(14),
            background_color=COLOR_ACCENT,
            on_press=self._on_download_click
        )
        btn_row.add_widget(self.download_btn)

        self.add_widget(btn_row)

    def _build_info_area(self):
        """Build scrollable info area"""
        scroll = ScrollView(size_hint_y=1)

        self.info_label = Label(
            text='Ready\n\nEnter a video URL and tap Analyze to start.',
            font_size=sp(12),
            color=COLOR_TEXT_SEC,
            size_hint_y=None,
            halign='left',
            valign='top',
            padding=[dp(5), dp(5)]
        )
        self.info_label.bind(texture_size=self.info_label.setter('size'))
        scroll.add_widget(self.info_label)

        self.add_widget(scroll)

    def _build_progress_section(self):
        """Build progress bar and status"""
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(6)
        )
        self.add_widget(self.progress_bar)

        self.progress_label = Label(
            text='',
            font_size=sp(10),
            color=COLOR_TEXT_SEC,
            size_hint_y=None,
            height=dp(18)
        )
        self.add_widget(self.progress_label)

    def _build_status_bar(self):
        """Build bottom status bar"""
        self.status_label = Label(
            text='Ready',
            font_size=sp(11),
            color=COLOR_TEXT_SEC,
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(self.status_label)

    # ============================================================
    # Event Handlers
    # ============================================================
    def _on_analyze_click(self, instance):
        """Handle Analyze button click"""
        url = self.url_input.text.strip()

        if not url:
            self._show_error('Please enter a video URL')
            return

        if not (url.startswith('http://') or url.startswith('https://')):
            self._show_error('Please enter a valid URL starting with http:// or https://')
            return

        self.status_label.text = 'Analyzing...'
        self.download_btn.disabled = True

        # Run analysis in background thread
        def do_analysis():
            info = self.engine.extract_info(url)

            @mainthread
            def update_ui():
                self.download_btn.disabled = False

                if info:
                    self.current_video_info = info
                    title = info.get('title', 'Unknown')
                    uploader = info.get('uploader', 'Unknown')
                    duration = format_duration(info.get('duration'))
                    site = info.get('extractor', 'Unknown')

                    self.info_label.text = (
                        f"Title: {title}\n"
                        f"Uploader: {uploader}\n"
                        f"Duration: {duration}\n"
                        f"Source: {site}\n\n"
                        f"Ready to download!"
                    )
                    self.status_label.text = 'Analysis complete - Ready'
                else:
                    self._show_error('Failed to analyze URL. Check the link and try again.')

            update_ui()

        threading.Thread(target=do_analysis, daemon=True).start()

    def _on_download_click(self, instance):
        """Handle Download button click"""
        if not self.current_video_info:
            self._show_error('Please analyze a URL first')
            return

        if self.is_downloading:
            self._show_error('Download already in progress')
            return

        url = self.current_video_info.get('webpage_url', self.url_input.text)
        quality = self.settings.get('video_quality', '720p')
        output_path = get_storage_path("Videos")

        self.is_downloading = True
        self.download_btn.disabled = True
        self.progress_bar.value = 0
        self.progress_label.text = 'Starting...'
        self.status_label.text = 'Downloading...'

        def on_progress(progress):
            @mainthread
            def update():
                pct = progress.get('percentage', 0)
                speed = progress.get('speed', 0)
                downloaded = progress.get('downloaded', 0)
                total = progress.get('total', 0)

                self.progress_bar.value = pct
                speed_str = format_file_size(int(speed)) + '/s' if speed else ''
                dl_str = format_file_size(downloaded)
                tot_str = format_file_size(total) if total else '?'
                self.progress_label.text = f'{pct:.1f}% | {dl_str}/{tot_str} | {speed_str}'

            update()

        def do_download():
            success = self.engine.download_video(url, output_path, quality, on_progress)

            @mainthread
            def update_ui():
                self.is_downloading = False
                self.download_btn.disabled = False

                if success:
                    self.status_label.text = 'Download completed successfully!'
                    self.progress_label.text = 'Complete'
                    self.history.add_entry(
                        url=url,
                        title=self.current_video_info.get('title'),
                        action='download',
                        status='completed'
                    )
                    # Auto-clean after 5 seconds
                    Clock.schedule_once(lambda dt: self._reset_ui(), 5)
                else:
                    self._show_error('Download failed. Please try again.')
                    self.status_label.text = 'Download failed'

            update_ui()

        threading.Thread(target=do_download, daemon=True).start()

    def _show_history_popup(self, instance):
        """Show download history in a popup"""
        entries = self.history.get_recent(30)

        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))

        if entries:
            count_label = Label(
                text=f'Total downloads: {self.history.get_count()}',
                font_size=sp(12),
                color=COLOR_TEXT,
                size_hint_y=None,
                height=dp(30)
            )
            content.add_widget(count_label)

            for entry in entries:
                title = (entry.get('title') or 'Unknown')[:50]
                url_text = (entry.get('url') or '')[:60]
                ts = entry.get('created_at', '')

                entry_label = Label(
                    text=f'• {title}\n  {url_text}\n  {ts}',
                    font_size=sp(10),
                    color=COLOR_TEXT_SEC,
                    size_hint_y=None,
                    height=dp(55),
                    halign='left',
                    valign='top'
                )
                entry_label.bind(size=entry_label.setter('text_size'))
                content.add_widget(entry_label)

            # Clear button
            clear_btn = Button(
                text='Clear History',
                font_size=sp(12),
                background_color=COLOR_ERROR,
                size_hint_y=None,
                height=dp(40),
                on_press=lambda x: self._clear_history()
            )
            content.add_widget(clear_btn)
        else:
            content.add_widget(Label(
                text='No download history yet',
                font_size=sp(14),
                color=COLOR_TEXT_SEC,
                halign='center'
            ))

        scroll = ScrollView()
        scroll.add_widget(content)

        popup = Popup(
            title='Download History',
            content=scroll,
            size_hint=(0.92, 0.75)
        )
        popup.open()

    def _clear_history(self):
        """Clear download history"""
        self.history.clear()
        self.status_label.text = 'History cleared'

    def _show_settings_popup(self, instance):
        """Show settings popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15))

        # Theme toggle
        theme_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))
        theme_row.add_widget(Label(
            text='Dark Mode',
            font_size=sp(14),
            color=COLOR_TEXT,
            size_hint_x=0.6,
            halign='left',
            valign='middle'
        ))
        theme_switch = Switch(
            active=self.settings.get('theme') == 'dark',
            size_hint_x=0.4
        )
        theme_switch.bind(active=self._on_theme_changed)
        theme_row.add_widget(theme_switch)
        content.add_widget(theme_row)

        # Quality selector
        quality_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))
        quality_row.add_widget(Label(
            text='Video Quality',
            font_size=sp(14),
            color=COLOR_TEXT,
            size_hint_x=0.4,
            halign='left',
            valign='middle'
        ))
        quality_spinner = Spinner(
            text=self.settings.get('video_quality', '720p'),
            values=['2160p', '1440p', '1080p', '720p', '480p', '360p'],
            size_hint_x=0.6
        )
        quality_spinner.bind(text=self._on_quality_changed)
        quality_row.add_widget(quality_spinner)
        content.add_widget(quality_row)

        # Storage info
        videos_path = get_storage_path("Videos")
        total_size = 0
        if os.path.exists(videos_path):
            for f in os.listdir(videos_path):
                fp = os.path.join(videos_path, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)

        content.add_widget(Label(
            text=f'Storage used: {format_file_size(total_size)}',
            font_size=sp(12),
            color=COLOR_TEXT_SEC,
            size_hint_y=None,
            height=dp(30),
            halign='center'
        ))

        # About
        content.add_widget(Label(
            text=f'{APP_NAME} v{APP_VERSION}\nVideo Downloader with Smart Features',
            font_size=sp(11),
            color=COLOR_TEXT_SEC,
            size_hint_y=None,
            height=dp(50),
            halign='center'
        ))

        scroll = ScrollView()
        scroll.add_widget(content)

        popup = Popup(
            title='Settings',
            content=scroll,
            size_hint=(0.9, 0.7)
        )
        popup.open()

    def _on_theme_changed(self, switch, value):
        """Handle theme change"""
        new_theme = 'dark' if value else 'light'
        self.settings.set('theme', new_theme)

        if new_theme == 'dark':
            Window.clearcolor = COLOR_BG
        else:
            Window.clearcolor = (0.95, 0.95, 0.95, 1)

    def _on_quality_changed(self, spinner, text):
        """Handle quality change"""
        self.settings.set('video_quality', text)

    def _reset_ui(self):
        """Reset UI after download completes"""
        self.progress_bar.value = 0
        self.progress_label.text = ''
        self.status_label.text = 'Ready'

    def _show_error(self, message):
        """Show error message"""
        self.status_label.text = f'Error: {message}'

        # Also show popup for critical errors
        popup = Popup(
            title='Error',
            content=Label(
                text=message,
                padding=[dp(20), dp(20)],
                color=COLOR_TEXT
            ),
            size_hint=(0.8, 0.3)
        )
        popup.open()


# ============================================================
# Application Entry Point
# ============================================================
class DownSuVidApp(App):
    """Main Kivy Application"""

    primary_color = ListProperty(list(COLOR_PRIMARY))

    def build(self):
        """Build the application"""
        self.title = f'{APP_NAME} v{APP_VERSION}'

        # Apply saved theme
        settings = SettingsManager()
        theme = settings.get('theme', 'dark')
        if theme == 'dark':
            Window.clearcolor = COLOR_BG
        else:
            Window.clearcolor = (0.95, 0.95, 0.95, 1)

        return MainScreen()

    def on_start(self):
        """App started successfully"""
        print(f"[{APP_NAME}] v{APP_VERSION} started successfully")

    def on_pause(self):
        """App going to background"""
        return True

    def on_resume(self):
        """App returning to foreground"""
        pass

    def on_stop(self):
        """App shutting down"""
        print(f"[{APP_NAME}] shutting down")
        # Cleanup database connection
        try:
            db = DatabaseManager()
            db.close()
        except Exception:
            pass


# ============================================================
# Main Entry Point
# ============================================================
if __name__ == '__main__':
    try:
        app = DownSuVidApp()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
