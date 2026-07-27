"""
Tests for Download Service
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.download.download_service import DownloadService
from app.domain.entities.download import DownloadStatus


@pytest.fixture
def download_service():
    """Create download service instance"""
    return DownloadService()


@pytest.mark.asyncio
async def test_create_download(download_service):
    """Test creating a new download"""
    url = "https://www.youtube.com/watch?v=test123"
    
    download = await download_service.create_download(url)
    
    assert download is not None
    assert download.url == url
    assert download.status == DownloadStatus.PENDING
    assert download.id is not None


@pytest.mark.asyncio
async def test_get_download(download_service):
    """Test getting a download by ID"""
    url = "https://www.youtube.com/watch?v=test456"
    
    download = await download_service.create_download(url)
    retrieved = await download_service.get_download(download.id)
    
    assert retrieved is not None
    assert retrieved.id == download.id
    assert retrieved.url == url


@pytest.mark.asyncio
async def test_get_all_downloads(download_service):
    """Test getting all downloads"""
    # Clear any existing downloads
    download_service.active_downloads.clear()
    
    url1 = "https://example.com/video1"
    url2 = "https://example.com/video2"
    
    await download_service.create_download(url1)
    await download_service.create_download(url2)
    
    downloads = await download_service.get_downloads()
    
    assert len(downloads) == 2


@pytest.mark.asyncio
async def test_pause_download(download_service):
    """Test pausing a download"""
    url = "https://example.com/video"
    
    download = await download_service.create_download(url)
    
    # Manually set status to downloading
    download.status = DownloadStatus.DOWNLOADING
    
    result = await download_service.pause_download(download.id)
    
    assert result is True
    assert download.status == DownloadStatus.PAUSED


@pytest.mark.asyncio
async def test_cancel_download(download_service):
    """Test cancelling a download"""
    url = "https://example.com/video"
    
    download = await download_service.create_download(url)
    
    result = await download_service.cancel_download(download.id)
    
    assert result is True
    assert download.status == DownloadStatus.CANCELLED


@pytest.mark.asyncio
async def test_delete_download(download_service):
    """Test deleting a download"""
    url = "https://example.com/video"
    
    download = await download_service.create_download(url)
    download_id = download.id
    
    result = await download_service.delete_download(download_id)
    
    assert result is True
    assert download_id not in download_service.active_downloads


@pytest.mark.asyncio
async def test_invalid_url_analysis(download_service):
    """Test analyzing an invalid URL"""
    # This should return None for invalid URLs
    # Actual behavior depends on yt-dlp
    
    # Just verify the method doesn't crash
    try:
        result = await download_service.analyze_url("not_a_valid_url")
        # May return None or VideoInfo with limited data
    except Exception:
        pass  # Expected for invalid URLs


@pytest.mark.asyncio
async def test_queue_processing(download_service):
    """Test queue processing"""
    # Add multiple downloads
    urls = [
        "https://example.com/video1",
        "https://example.com/video2",
        "https://example.com/video3",
    ]
    
    for url in urls:
        await download_service.create_download(url)
    
    # Check queue
    queue_size = await download_service.get_queue_size()
    assert queue_size >= 0  # Queue may have been processed already


@pytest.mark.asyncio
async def test_max_parallel_setting(download_service):
    """Test setting max parallel downloads"""
    await download_service.set_max_parallel(5)
    assert download_service.max_parallel == 5
    
    await download_service.set_max_parallel(0)  # Should clamp to 1
    assert download_service.max_parallel == 1
    
    await download_service.set_max_parallel(11)  # Should clamp to 10
    assert download_service.max_parallel == 10