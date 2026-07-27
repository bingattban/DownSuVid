"""
Network Utilities Module
"""

import asyncio
import socket
from typing import Optional, Tuple
from urllib.parse import urlparse

from app.utils.logger import LoggerMixin


class NetworkUtils(LoggerMixin):
    """Network utility functions"""
    
    @staticmethod
    async def check_internet_connection(timeout: int = 5) -> bool:
        """
        Check if internet is available
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connected
        """
        try:
            # Try to connect to common DNS server
            loop = asyncio.get_event_loop()
            
            # Test with Google DNS
            result = await loop.run_in_executor(
                None,
                NetworkUtils._test_connection,
                '8.8.8.8',
                53,
                timeout
            )
            
            if result:
                return True
            
            # Fallback test with Cloudflare DNS
            result = await loop.run_in_executor(
                None,
                NetworkUtils._test_connection,
                '1.1.1.1',
                53,
                timeout
            )
            
            return result
            
        except Exception as e:
            NetworkUtils.logger.error(f"Connection check failed: {e}")
            return False
    
    @staticmethod
    def _test_connection(host: str, port: int, timeout: int) -> bool:
        """Test connection to host"""
        try:
            socket.setdefaulttimeout(timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.close()
            return True
        except Exception:
            return False
    
    @staticmethod
    def parse_url(url: str) -> Optional[dict]:
        """
        Parse URL into components
        
        Args:
            url: URL to parse
            
        Returns:
            Dictionary with URL components
        """
        try:
            parsed = urlparse(url)
            
            return {
                'scheme': parsed.scheme,
                'host': parsed.hostname,
                'port': parsed.port,
                'path': parsed.path,
                'query': parsed.query,
                'fragment': parsed.fragment,
                'full_url': url,
            }
            
        except Exception as e:
            NetworkUtils.logger.error(f"URL parsing failed: {e}")
            return None
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """
        Extract domain from URL
        
        Args:
            url: URL
            
        Returns:
            Domain name
        """
        try:
            parsed = urlparse(url)
            domain = parsed.hostname
            
            if domain:
                # Remove www prefix
                if domain.startswith('www.'):
                    domain = domain[4:]
            
            return domain
            
        except Exception:
            return None
    
    @staticmethod
    def is_streaming_url(url: str) -> bool:
        """
        Check if URL is a streaming URL
        
        Args:
            url: URL
            
        Returns:
            True if streaming URL
        """
        streaming_patterns = [
            'youtube.com/watch',
            'youtu.be/',
            'vimeo.com/',
            'dailymotion.com/video',
            'twitch.tv/videos',
            'facebook.com/watch',
            'tiktok.com/',
            'instagram.com/reel',
        ]
        
        url_lower = url.lower()
        for pattern in streaming_patterns:
            if pattern in url_lower:
                return True
        
        return False
    
    @staticmethod
    async def get_file_size_from_url(url: str) -> Optional[int]:
        """
        Get file size from URL headers
        
        Args:
            url: File URL
            
        Returns:
            File size in bytes or None
        """
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.head(url, follow_redirects=True, timeout=10)
                
                content_length = response.headers.get('content-length')
                if content_length:
                    return int(content_length)
            
            return None
            
        except Exception as e:
            NetworkUtils.logger.debug(f"Failed to get file size: {e}")
            return None
    
    @staticmethod
    async def validate_url_reachable(url: str, timeout: int = 10) -> bool:
        """
        Check if URL is reachable
        
        Args:
            url: URL to check
            timeout: Timeout in seconds
            
        Returns:
            True if reachable
        """
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.head(
                    url,
                    follow_redirects=True,
                    timeout=timeout
                )
                
                return response.status_code < 400
                
        except Exception:
            return False