# geo_service.py
# Professional GeoIP service with caching, fallback APIs, retry mechanism, and logging

import logging
import time
import requests
from functools import wraps
from typing import Optional, Dict, Tuple, List

# Setup logger
logger = logging.getLogger(__name__)

def retry(max_retries: int = 2, delay: float = 1.0):
    """Decorator to retry a function on exception."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise
                    logger.warning(f"Retry {attempt+1}/{max_retries} for {func.__name__}: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


class GeoLocationService:
    """
    Service to retrieve country name from an IP address.
    Features:
    - In-memory caching with TTL
    - Multiple API providers with automatic fallback
    - Retry logic for transient failures
    - Detailed logging
    """

    def __init__(self, cache_ttl: int = 3600):
        self.cache: Dict[str, Tuple[str, float]] = {}  # ip -> (country, timestamp)
        self.cache_ttl = cache_ttl
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'TorBridgeManager/2.0'})

        # API list in priority order (first successful wins)
        self.apis: List[dict] = [
            {
                'name': 'ipwho.is',
                'url': 'http://ipwho.is/{}',
                'extract': lambda data: data.get('country', 'Unknown'),
                'timeout': 5,
            },  
            {
                'name': 'ip-api',
                'url': 'http://ip-api.com/json/{}',
                'extract': lambda data: data.get('country', data.get('countryCode', 'Unknown')),
                'timeout': 3,
            },
            {
                'name': 'ipapi.co',
                'url': 'https://ipapi.co/{}/json/',
                'extract': lambda data: data.get('country_name', 'Unknown'),
                'timeout': 3,
            },
            {
                'name': 'ipinfo.io',
                'url': 'https://ipinfo.io/{}/json',
                'extract': lambda data: data.get('country', 'Unknown'),
                'timeout': 3,
            },
        ]

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached entry is still valid based on TTL."""
        return (time.time() - timestamp) < self.cache_ttl

    @retry(max_retries=1, delay=0.5)
    def _fetch_from_api(self, api: dict, ip: str) -> Optional[str]:
        """Call a single API and extract country name. Returns None on failure."""
        url = api['url'].format(ip)
        try:
            resp = self.session.get(url, timeout=api['timeout'])
            if resp.status_code == 200:
                data = resp.json()
                country = api['extract'](data)
                if country and country != 'Unknown':
                    logger.debug(f"API {api['name']} succeeded for {ip}: {country}")
                    return country
                else:
                    logger.warning(f"API {api['name']} returned 'Unknown' for {ip}")
            elif resp.status_code == 429:
                logger.warning(f"API {api['name']} rate limited (429) for {ip}")
            else:
                logger.warning(f"API {api['name']} returned HTTP {resp.status_code} for {ip}")
        except Exception as e:
            logger.error(f"Exception calling {api['name']} for {ip}: {e}")
        return None

    def get_country(self, ip: str) -> str:
        """
        Get country name for an IP address.
        First checks cache, then tries APIs in order.
        Returns country name or 'Unknown'.
        """
        # Check cache first
        if ip in self.cache:
            country, timestamp = self.cache[ip]
            if self._is_cache_valid(timestamp):
                logger.debug(f"Cache hit for {ip}: {country}")
                return country
            else:
                # Cache expired, remove entry
                del self.cache[ip]

        # Try each API in sequence
        for api in self.apis:
            try:
                country = self._fetch_from_api(api, ip)
                if country:
                    # Store in cache
                    self.cache[ip] = (country, time.time())
                    return country
            except Exception as e:
                logger.error(f"Unexpected error with API {api['name']} for {ip}: {e}")
                continue

        # All APIs failed
        logger.error(f"All APIs failed for IP {ip}")
        return "Unknown"