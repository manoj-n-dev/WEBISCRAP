import asyncio
import time
from typing import Any, Dict, Optional
from pydantic import BaseModel
from loguru import logger
import urllib.parse
import socket
import ipaddress

def validate_resolved_ip(ip_str: str) -> bool:
    """
    Check whether a resolved IP address (IPv4 or IPv6) is safe (public, non-internal).
    Reusable by both the initial URL check, browser subresource interceptor, and per-redirect hops.
    """
    if not ip_str:
        return False
    try:
        ip = ipaddress.ip_address(ip_str.strip("[]"))

        # Handle IPv6-mapped IPv4 addresses (e.g. ::ffff:127.0.0.1 or ::ffff:169.254.169.254)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped

        # C3 & H-12: Block loopback, private RFC1918/RFC4193, multicast, reserved,
        # link-local (169.254.x.x / fe80:: - cloud metadata!), and unspecified (0.0.0.0 / ::)
        if (ip.is_loopback or ip.is_private or ip.is_multicast or
                ip.is_reserved or ip.is_link_local or ip.is_unspecified):
            return False

        # Additional 6to4 prefix check if embedding private IPv4
        if isinstance(ip, ipaddress.IPv6Address) and ip.sixtofour:
            if not validate_resolved_ip(str(ip.sixtofour)):
                return False

        return True
    except (ValueError, AttributeError):
        return False

def validate_target_url(url: str) -> bool:
    """
    H-12 SSRF protection: validate URL scheme and resolve IP via getaddrinfo
    to comprehensively validate ALL returned IPv4 and IPv6 addresses.
    Fails closed on resolution errors or private address resolution.
    """
    if not url:
        return False
        
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False
            
        hostname = parsed.hostname
        if not hostname:
            return False

        # If hostname is already an IP address string
        try:
            ip_direct = ipaddress.ip_address(hostname.strip("[]"))
            return validate_resolved_ip(str(ip_direct))
        except ValueError:
            pass  # It's a domain name, resolve via DNS
            
        # H-12: Resolve hostname to ALL IP addresses (both IPv4 and IPv6)
        addr_infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        if not addr_infos:
            return False

        # Every resolved IP must be validated. If ANY address is private/internal, reject!
        for addr_info in addr_infos:
            sockaddr = addr_info[4]
            ip_candidate: str = str(sockaddr[0])  # typeshed types sockaddr[0] as str|int; str() is safe
            if not validate_resolved_ip(ip_candidate):
                logger.warning(f"SSRF block: Hostname {hostname} resolved to unsafe IP {ip_candidate}")
                return False
                
        return True
    except Exception as e:
        logger.warning(f"URL validation failed for {url}: {e}")
        return False

MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # H-13: 10 MB maximum response size cap

async def ssrf_safe_fetch(
    url: str,
    max_redirects: int = 5,
    max_bytes: int = MAX_RESPONSE_BYTES
) -> Optional[str]:
    """
    C4 & H-13: Redirect-aware, IP-validated, resource-bounded HTTP fetcher.
    Follows redirects manually (up to max_redirects hops), re-validating
    the target URL against SSRF checks on every hop.
    Reads response in bounded streaming chunks up to max_bytes.
    Returns the final response text, or None on failure.
    """
    import httpx
    
    current_url = url
    for hop in range(max_redirects + 1):
        if not validate_target_url(current_url):
            logger.warning(f"SSRF blocked redirect hop {hop}: {current_url}")
            return None
        
        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=False,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            ) as client:
                async with client.stream("GET", current_url) as response:
                    if response.is_redirect:
                        location = response.headers.get("location", "")
                        if not location:
                            return None
                        # Resolve relative redirects
                        current_url = str(response.url.join(location))
                        continue
                    
                    response.raise_for_status()

                    # H-13: Early exit if Content-Length header exceeds limit
                    content_length = response.headers.get("content-length")
                    if content_length:
                        try:
                            if int(content_length) > max_bytes:
                                logger.warning(
                                    f"Response Content-Length {content_length} exceeds limit {max_bytes} for {current_url}"
                                )
                                return None
                        except ValueError:
                            pass

                    # H-13: Content-Type validation
                    content_type = response.headers.get("content-type", "").lower()
                    allowed_types = ("text/", "application/json", "application/xml", "application/xhtml", "application/javascript")
                    if content_type and not any(allowed in content_type for allowed in allowed_types):
                        logger.warning(f"Disallowed Content-Type '{content_type}' for scraping: {current_url}")
                        return None

                    # H-13: Read in bounded streaming chunks to prevent memory exhaustion
                    chunks = []
                    bytes_read = 0
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        bytes_read += len(chunk)
                        if bytes_read > max_bytes:
                            logger.warning(f"Response exceeded maximum allowed size of {max_bytes} bytes for {current_url}")
                            return None
                        chunks.append(chunk)

                    raw_bytes = b"".join(chunks)
                    encoding = response.encoding or "utf-8"
                    return raw_bytes.decode(encoding, errors="replace")

        except Exception as e:
            logger.warning(f"SSRF-safe fetch failed at hop {hop} for {current_url}: {e}")
            return None
    
    logger.warning(f"SSRF-safe fetch: too many redirects (>{max_redirects}) for {url}")
    return None

class BaseAgent:
    """Base class for all AI agents in the WEBISCRAP pipeline."""
    
    def __init__(self, name: str):
        self.name = name
        
    async def run(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        Includes logging, timing, and error handling.
        """
        start_time = time.time()
        logger.info(f"[{session_id}] Agent {self.name} started execution.")
        
        try:
            # Emit progress event (this could later hook into SSE stream)
            self._emit_progress(session_id, "started")
            
            result = await self._execute(input_data, session_id)
            
            self._emit_progress(session_id, "completed")
            return result
            
        except Exception as e:
            logger.error(f"[{session_id}] Agent {self.name} failed: {str(e)}")
            self._emit_progress(session_id, "failed", error=str(e))
            raise e
            
        finally:
            elapsed = time.time() - start_time
            logger.info(f"[{session_id}] Agent {self.name} finished in {elapsed:.2f}s.")
            
    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        To be implemented by child classes. Contains the actual agent logic.
        """
        raise NotImplementedError(f"Agent {self.name} must implement _execute method")
        
    def _emit_progress(self, session_id: str, status: str, error: Optional[str] = None):
        """
        Emit an agent-level progress event for local debug logging.
        Note: Pipeline-level progress tracking for frontend polling is managed directly
        by orchestrator.py via redis_store.set_pipeline_progress().
        """
        event = {
            "agent": self.name,
            "status": status,
            "timestamp": time.time(),
        }
        if error:
            event["error"] = error
            
        logger.debug(f"Progress Event [{session_id}]: {event}")
