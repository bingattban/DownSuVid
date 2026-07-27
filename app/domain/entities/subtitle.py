"""
Subtitle Entity Module
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class SubtitleFormat(Enum):
    """Subtitle format enumeration"""
    SRT = "srt"
    VTT = "vtt"
    ASS = "ass"
    SSA = "ssa"
    SUB = "sub"


class SubtitleSource(Enum):
    """Subtitle source enumeration"""
    DOWNLOADED = "downloaded"
    EXTRACTED = "extracted"
    GENERATED = "generated"
    TRANSLATED = "translated"
    EMBEDDED = "embedded"


class SubtitlePriority(Enum):
    """Subtitle priority enumeration"""
    ARABIC_ORIGINAL = 1
    OTHER_TRANSLATED = 2
    GENERATED = 3


@dataclass
class Subtitle:
    """Subtitle entity"""
    id: Optional[str] = None
    language: str = ""
    language_name: str = ""
    format: SubtitleFormat = SubtitleFormat.SRT
    source: SubtitleSource = SubtitleSource.DOWNLOADED
    priority: SubtitlePriority = SubtitlePriority.OTHER_TRANSLATED
    
    # Content
    file_path: Optional[str] = None
    content: Optional[str] = None
    original_content: Optional[str] = None
    
    # Metadata
    is_auto_generated: bool = False
    confidence_score: Optional[float] = None
    word_count: int = 0
    character_count: int = 0
    
    # Translation info
    original_language: Optional[str] = None
    translated_from: Optional[str] = None
    translation_engine: Optional[str] = None
    
    # Timing
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    # Quality
    has_timing_errors: bool = False
    has_encoding_errors: bool = False
    quality_score: Optional[float] = None
    
    # Video reference
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def is_arabic(self) -> bool:
        """Check if subtitle is Arabic"""
        return self.language.lower() in ['ar', 'ara', 'arabic', 'العربية']
    
    def needs_translation(self) -> bool:
        """Check if subtitle needs translation to Arabic"""
        return not self.is_arabic()
    
    def get_file_extension(self) -> str:
        """Get file extension based on format"""
        return self.format.value
    
    def parse_content(self) -> List[Dict]:
        """
        Parse subtitle content into entries
        
        Returns:
            List of subtitle entries with start_time, end_time, text
        """
        if not self.content:
            return []
        
        entries = []
        try:
            if self.format == SubtitleFormat.SRT:
                entries = self._parse_srt(self.content)
            elif self.format == SubtitleFormat.VTT:
                entries = self._parse_vtt(self.content)
            elif self.format == SubtitleFormat.ASS:
                entries = self._parse_ass(self.content)
        except Exception:
            pass
        
        return entries
    
    def _parse_srt(self, content: str) -> List[Dict]:
        """Parse SRT format"""
        entries = []
        blocks = content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    times = lines[1].split(' --> ')
                    start = self._time_to_seconds(times[0])
                    end = self._time_to_seconds(times[1])
                    text = '\n'.join(lines[2:])
                    
                    entries.append({
                        'start_time': start,
                        'end_time': end,
                        'text': text
                    })
                except Exception:
                    continue
        
        return entries
    
    def _parse_vtt(self, content: str) -> List[Dict]:
        """Parse VTT format"""
        entries = []
        lines = content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            if '-->' in lines[i]:
                try:
                    times = lines[i].split(' --> ')
                    start = self._time_to_seconds(times[0])
                    end = self._time_to_seconds(times[1])
                    
                    i += 1
                    text_lines = []
                    while i < len(lines) and lines[i].strip():
                        text_lines.append(lines[i])
                        i += 1
                    
                    text = '\n'.join(text_lines)
                    entries.append({
                        'start_time': start,
                        'end_time': end,
                        'text': text
                    })
                except Exception:
                    i += 1
            else:
                i += 1
        
        return entries
    
    def _parse_ass(self, content: str) -> List[Dict]:
        """Parse ASS format"""
        entries = []
        in_events = False
        
        for line in content.split('\n'):
            if '[Events]' in line:
                in_events = True
                continue
            
            if in_events and line.startswith('Dialogue:'):
                try:
                    parts = line.split(',', 9)
                    if len(parts) >= 9:
                        start = self._time_to_seconds(parts[1])
                        end = self._time_to_seconds(parts[2])
                        text = parts[9].strip()
                        
                        entries.append({
                            'start_time': start,
                            'end_time': end,
                            'text': text
                        })
                except Exception:
                    continue
        
        return entries
    
    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        """
        Convert time string to seconds
        
        Args:
            time_str: Time string (HH:MM:SS,mmm or MM:SS.mmm)
            
        Returns:
            Time in seconds
        """
        time_str = time_str.strip().replace(',', '.')
        
        parts = time_str.split(':')
        if len(parts) == 3:
            return (int(parts[0]) * 3600 + 
                   int(parts[1]) * 60 + 
                   float(parts[2]))
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        else:
            return float(parts[0])
    
    def to_srt_format(self) -> str:
        """
        Convert subtitle to SRT format
        
        Returns:
            SRT formatted string
        """
        if not self.content:
            return ""
        
        entries = self.parse_content()
        srt_content = []
        
        for i, entry in enumerate(entries, 1):
            start = self._seconds_to_time(entry['start_time'])
            end = self._seconds_to_time(entry['end_time'])
            text = entry['text']
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start} --> {end}")
            srt_content.append(text)
            srt_content.append("")
        
        return '\n'.join(srt_content)
    
    @staticmethod
    def _seconds_to_time(seconds: float) -> str:
        """
        Convert seconds to time string
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Time string in SRT format
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')