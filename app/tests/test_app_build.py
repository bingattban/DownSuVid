"""
Build Validation Test
Ensures application can be imported and initialized without errors
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_import_main_modules():
    """Test that all main modules can be imported"""
    modules = [
        'app.config.constants',
        'app.config.app_config',
        'app.utils.logger',
        'app.utils.file_utils',
        'app.utils.validators',
        'app.utils.network_utils',
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ Successfully imported: {module}")
        except Exception as e:
            print(f"✗ Failed to import {module}: {e}")
            raise


def test_import_domain_entities():
    """Test domain entities imports"""
    entities = [
        'app.domain.entities.download',
        'app.domain.entities.model',
        'app.domain.entities.package',
        'app.domain.entities.subtitle',
    ]
    
    for entity in entities:
        try:
            __import__(entity)
            print(f"✓ Successfully imported: {entity}")
        except Exception as e:
            print(f"✗ Failed to import {entity}: {e}")
            raise


def test_import_services():
    """Test service imports"""
    services = [
        'app.services.download.download_service',
        'app.services.storage.storage_service',
        'app.services.settings.settings_service',
        'app.services.history.history_service',
        'app.services.queue.queue_service',
    ]
    
    for service in services:
        try:
            __import__(service)
            print(f"✓ Successfully imported: {service}")
        except Exception as e:
            print(f"✗ Failed to import {service}: {e}")
            raise


def test_import_providers():
    """Test provider imports"""
    providers = [
        'app.providers.downloader.ytdlp_provider',
        'app.providers.ffmpeg.ffmpeg_provider',
        'app.providers.speech.speech_provider',
        'app.providers.translation.translation_provider',
    ]
    
    for provider in providers:
        try:
            __import__(provider)
            print(f"✓ Successfully imported: {provider}")
        except Exception as e:
            print(f"✗ Failed to import {provider}: {e}")
            raise


def test_import_repositories():
    """Test repository imports"""
    repos = [
        'app.repositories.download_repository_impl',
        'app.repositories.settings_repository_impl',
        'app.repositories.model_repository_impl',
        'app.repositories.package_repository_impl',
        'app.repositories.subtitle_repository_impl',
    ]
    
    for repo in repos:
        try:
            __import__(repo)
            print(f"✓ Successfully imported: {repo}")
        except Exception as e:
            print(f"✗ Failed to import {repo}: {e}")
            raise


def test_import_database():
    """Test database imports"""
    db_modules = [
        'app.database.database_manager',
        'app.database.dao.download_dao',
        'app.database.dao.settings_dao',
        'app.database.dao.history_dao',
        'app.database.dao.model_dao',
        'app.database.dao.package_dao',
    ]
    
    for module in db_modules:
        try:
            __import__(module)
            print(f"✓ Successfully imported: {module}")
        except Exception as e:
            print(f"✗ Failed to import {module}: {e}")
            raise


def test_dependency_injection():
    """Test DI container"""
    try:
        from app.dependency_injection import DIContainer
        
        container = DIContainer()
        container.initialize_all()
        
        # Verify core services
        assert container.get_service('database') is not None
        assert container.get_service('config') is not None
        assert container.get_service('download') is not None
        assert container.get_service('settings') is not None
        
        print("✓ Dependency injection working correctly")
        
    except Exception as e:
        print(f"✗ Dependency injection failed: {e}")
        raise


def test_constants():
    """Test constants are properly defined"""
    from app.config.constants import (
        APP_NAME,
        APP_VERSION,
        DATABASE_NAME,
        STORAGE_ROOT,
    )
    
    assert APP_NAME == "DownSuVid"
    assert APP_VERSION == "1.0.0"
    assert DATABASE_NAME == "downsuviid.db"
    assert STORAGE_ROOT == "DownSuVid"
    
    print("✓ Constants properly defined")


if __name__ == '__main__':
    print("Running build validation tests...\n")
    
    test_constants()
    test_import_main_modules()
    test_import_domain_entities()
    test_import_services()
    test_import_providers()
    test_import_repositories()
    test_import_database()
    test_dependency_injection()
    
    print("\n✓ All build validation tests passed!")
    print("Application is ready for Buildozer compilation.")