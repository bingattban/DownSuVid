"""
Tests for Storage Service
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.storage.storage_service import StorageService
from app.utils.file_utils import FileUtils


@pytest.fixture
def storage_service():
    """Create storage service instance"""
    return StorageService()


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.mark.asyncio
async def test_initialize_storage(storage_service):
    """Test storage initialization"""
    result = await storage_service.initialize()
    assert result is True


@pytest.mark.asyncio
async def test_get_disk_usage(storage_service):
    """Test getting disk usage"""
    usage = await storage_service.get_disk_usage()
    
    assert isinstance(usage, dict)
    assert 'total' in usage
    assert 'videos' in usage
    assert 'subtitles' in usage


@pytest.mark.asyncio
async def test_get_free_space(storage_service):
    """Test getting free space"""
    free_space = await storage_service.get_free_space()
    assert free_space >= 0


@pytest.mark.asyncio
async def test_has_enough_space(storage_service):
    """Test space check"""
    # Check for 1 byte (should be enough)
    has_space = await storage_service.has_enough_space(1)
    assert isinstance(has_space, bool)
    
    # Check for extremely large amount (should fail)
    has_space = await storage_service.has_enough_space(10**15)
    assert has_space is False


@pytest.mark.asyncio
async def test_delete_file(storage_service, temp_dir):
    """Test file deletion"""
    # Create test file
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, 'w') as f:
        f.write("test")
    
    # Delete file
    result = await storage_service.delete_file(test_file)
    assert result is True
    assert not os.path.exists(test_file)


@pytest.mark.asyncio
async def test_get_storage_stats(storage_service):
    """Test getting storage statistics"""
    stats = await storage_service.get_storage_stats()
    
    assert isinstance(stats, dict)
    assert 'total_space' in stats
    assert 'used_space' in stats
    assert 'free_space' in stats
    assert 'usage_percentage' in stats


@pytest.mark.asyncio
async def test_file_size_formatting():
    """Test file size formatting"""
    assert FileUtils.format_file_size(0) == "0.0 B"
    assert FileUtils.format_file_size(1024) == "1.0 KB"
    assert FileUtils.format_file_size(1024 * 1024) == "1.0 MB"
    assert FileUtils.format_file_size(1024 * 1024 * 1024) == "1.0 GB"


@pytest.mark.asyncio
async def test_sanitize_filename():
    """Test filename sanitization"""
    # Test invalid characters
    sanitized = FileUtils.sanitize_filename('file<name>.txt')
    assert '<' not in sanitized
    assert '>' not in sanitized
    
    # Test long filename
    long_name = 'a' * 300 + '.txt'
    sanitized = FileUtils.sanitize_filename(long_name)
    assert len(sanitized) <= 200 + 4  # max length + extension
    
    # Test empty filename
    sanitized = FileUtils.sanitize_filename('')
    assert sanitized == 'unnamed'