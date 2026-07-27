# وثائق API الداخلية

## DownloadService

### `create_download(url: str) -> Optional[Download]`
إنشاء تحميل جديد

### `analyze_url(url: str) -> Optional[VideoInfo]`
تحليل رابط الفيديو

### `start_download(download_id: str, quality: str) -> bool`
بدء التحميل

## SubtitleService

### `process_subtitles(url: str, video_path: str) -> List[Subtitle]`
معالجة الترجمة حسب الأولوية

## SpeechService

### `transcribe_audio(audio_path: str, language: str) -> Optional[Dict]`
تحويل الصوت إلى نص

## TranslationService

### `translate_text(text: str, source_lang: str, target_lang: str) -> Optional[str]`
ترجمة النص

## StorageService

### `get_storage_stats() -> Dict`
إحصائيات التخزين

### `clean_all_temp() -> Dict`
تنظيف الملفات المؤقتة