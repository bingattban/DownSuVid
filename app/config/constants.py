"""
Application Constants
"""

# Application Info
APP_NAME = "DownSuVid"
APP_NAME_AR = "تحميل الفيديو والترجمه"
APP_VERSION = "1.0.0"
APP_AUTHOR = "DownSuVid Team"
APP_DESCRIPTION = "تحميل الفيديوهات مع ترجمة ذكية"

# Package Info
PACKAGE_NAME = "com.downsuviid"
PACKAGE_DOMAIN = "com.downsuviid"

# Database
DATABASE_NAME = "downsuviid.db"
DATABASE_VERSION = 1

# Storage Paths
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

# Model Paths
MODEL_PATH_WHISPER = "Models/Whisper"
MODEL_PATH_ARGOS = "Packages/Argos"

# Download Settings
MAX_PARALLEL_DOWNLOADS = 3
MAX_RETRY_COUNT = 3
RETRY_DELAY = 5  # seconds
DOWNLOAD_CHUNK_SIZE = 8192  # bytes
DEFAULT_TIMEOUT = 30  # seconds

# Subtitle Settings
SUBTITLE_FORMATS = ["srt", "vtt", "ass"]
PREFERRED_SUBTITLE_FORMAT = "srt"
SUBTITLE_PRIORITY_LANGUAGES = ["ar", "arabic"]

# Video Settings
SUPPORTED_VIDEO_QUALITIES = ["1080p", "720p", "480p", "360p"]
DEFAULT_VIDEO_QUALITY = "720p"

# Audio Settings
AUDIO_FORMAT = "wav"
AUDIO_SAMPLE_RATE = 16000

# Speech Recognition
SPEECH_RECOGNITION_TIMEOUT = 300  # seconds
MIN_CONFIDENCE_SCORE = 0.7

# Translation
TRANSLATION_BATCH_SIZE = 32
MAX_TRANSLATION_LENGTH = 5000

# UI Constants
WINDOW_WIDTH = 360
WINDOW_HEIGHT = 640
FONT_SIZE_SMALL = 12
FONT_SIZE_MEDIUM = 14
FONT_SIZE_LARGE = 16
FONT_SIZE_XLARGE = 18

# Colors (Dark Theme)
COLOR_PRIMARY = (0.0, 0.59, 0.53, 1)  # Teal 500
COLOR_PRIMARY_DARK = (0.0, 0.47, 0.42, 1)  # Teal 700
COLOR_PRIMARY_LIGHT = (0.3, 0.69, 0.64, 1)  # Teal 300
COLOR_ACCENT = (1.0, 0.76, 0.03, 1)  # Amber 500
COLOR_BACKGROUND_DARK = (0.12, 0.12, 0.12, 1)
COLOR_BACKGROUND_LIGHT = (0.95, 0.95, 0.95, 1)
COLOR_SURFACE_DARK = (0.18, 0.18, 0.18, 1)
COLOR_SURFACE_LIGHT = (1.0, 1.0, 1.0, 1)
COLOR_ERROR = (0.96, 0.26, 0.21, 1)  # Red 500
COLOR_SUCCESS = (0.3, 0.69, 0.31, 1)  # Green 500
COLOR_WARNING = (1.0, 0.76, 0.03, 1)  # Amber 500

# Animation
ANIMATION_DURATION = 0.3
ANIMATION_TRANSITION = "in_out_cubic"

# Notification
NOTIFICATION_CHANNEL_ID = "downsuviid_channel"
NOTIFICATION_CHANNEL_NAME = "DownSuVid"
NOTIFICATION_ID_DOWNLOAD = 1000
NOTIFICATION_ID_MODEL = 2000

# URLs
GITHUB_REPO = "https://github.com/downsuviid/downsuviid"
WEBSITE_URL = "https://downsuviid.com"
UPDATE_CHECK_URL = "https://api.github.com/repos/downsuviid/downsuviid/releases/latest"

# Limits
MAX_FILE_SIZE = 1024 * 1024 * 1024 * 4  # 4GB
MIN_FREE_SPACE = 1024 * 1024 * 100  # 100MB
MAX_QUEUE_SIZE = 100
MAX_LOG_SIZE = 1024 * 1024 * 10  # 10MB