"""
Tests for Subtitle Service
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.subtitle.subtitle_service import SubtitleService
from app.domain.entities.subtitle import Subtitle, SubtitleFormat, SubtitleSource
from app.domain.entities.download import SubtitleInfo, SubtitleStatus


@pytest.fixture
def subtitle_service():
    """Create subtitle service instance"""
    return SubtitleService()


@pytest.fixture
def sample_subtitle():
    """Create sample subtitle entity"""
    return Subtitle(
        language='en',
        language_name='English',
        format=SubtitleFormat.SRT,
        source=SubtitleSource.DOWNLOADED,
        content="""1
00:00:01,000 --> 00:00:04,000
Hello world

2
00:00:05,000 --> 00:00:08,000
This is a test subtitle
""",
        file_path='/tmp/test.srt'
    )


@pytest.mark.asyncio
async def test_subtitle_creation(subtitle_service):
    """Test subtitle entity creation"""
    subtitle = Subtitle(
        language='ar',
        language_name='العربية',
        format=SubtitleFormat.SRT,
    )
    
    assert subtitle.is_arabic() is True
    assert subtitle.needs_translation() is False


@pytest.mark.asyncio
async def test_subtitle_parsing(sample_subtitle):
    """Test subtitle content parsing"""
    entries = sample_subtitle.parse_content()
    
    assert len(entries) == 2
    assert entries[0]['text'] == 'Hello world'
    assert entries[1]['text'] == 'This is a test subtitle'
    assert entries[0]['start_time'] == 1.0
    assert entries[0]['end_time'] == 4.0


@pytest.mark.asyncio
async def test_srt_conversion(sample_subtitle):
    """Test subtitle to SRT conversion"""
    srt_content = sample_subtitle.to_srt_format()
    
    assert '00:00:01,000 --> 00:00:04,000' in srt_content
    assert 'Hello world' in srt_content


@pytest.mark.asyncio
async def test_time_conversion():
    """Test time string conversion"""
    from app.domain.entities.subtitle import Subtitle
    
    # Test HH:MM:SS,mmm format
    seconds = Subtitle._time_to_seconds('01:30:00,500')
    assert seconds == 5400.5
    
    # Test MM:SS.mmm format
    seconds = Subtitle._time_to_seconds('05:30.000')
    assert seconds == 330.0
    
    # Test seconds format
    seconds = Subtitle._time_to_seconds('10.5')
    assert seconds == 10.5


@pytest.mark.asyncio
async def test_subtitle_creation_from_text(subtitle_service):
    """Test creating subtitle from text segments"""
    segments = [
        {'text': 'Hello', 'start': 0.0, 'end': 2.0},
        {'text': 'World', 'start': 2.0, 'end': 4.0},
    ]
    
    srt_content = subtitle_service._create_srt_from_segments(segments)
    
    assert '1' in srt_content
    assert 'Hello' in srt_content
    assert 'World' in srt_content
    assert '00:00:00,000' in srt_content


@pytest.mark.asyncio
async def test_language_detection(subtitle_service):
    """Test language detection"""
    # Arabic text
    arabic_text = "مرحبا بالعالم هذا نص عربي"
    result = await subtitle_service._detect_language_simple(arabic_text)
    assert result == 'ar'
    
    # English text
    english_text = "Hello world this is English text"
    result = await subtitle_service._detect_language_simple(english_text)
    assert result == 'en'


@pytest.mark.asyncio
async def test_timestamp_formatting(subtitle_service):
    """Test timestamp formatting"""
    # Test exact second
    timestamp = subtitle_service._format_timestamp(5.0)
    assert timestamp == '00:00:05,000'
    
    # Test with milliseconds
    timestamp = subtitle_service._format_timestamp(5.5)
    assert timestamp == '00:00:05,500'
    
    # Test with hours
    timestamp = subtitle_service._format_timestamp(3661.5)
    assert timestamp == '01:01:01,500'


@pytest.mark.asyncio
async def test_subtitle_info_entity():
    """Test SubtitleInfo entity"""
    info = SubtitleInfo(
        language='en',
        language_name='English',
        format='srt',
        is_auto_generated=False,
    )
    
    assert info.language == 'en'
    assert info.status == SubtitleStatus.NONE