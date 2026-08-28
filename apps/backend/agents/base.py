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
    Check whether a resolved IP address is safe (public, non-internal).
    Reusable by both the initial URL check and per-redirect-hop checks.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        # C3: Block link-local (169.254.x.x — cloud metadata!) and unspecified (0.0.0.0)
        if (ip.is_loopback or ip.is_private or ip.is_multicast or
                ip.is_reserved or ip.is_link_local or ip.is_unspecified):
            return False
        return True
    except ValueError:
        return False

def validate_target_url(url: str) -> bool:
    """SSRF protection: validate URL scheme and resolve IP to block private/internal addresses."""
    if not url:
        return False
        
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False
            
        hostname = parsed.hostname
        if not hostname:
            return False
            
        # Resolve hostname to IP (IPv4)
        ip_addr = socket.gethostbyname(hostname)
        
        if not validate_resolved_ip(ip_addr):
            return False
            
        return True
    except Exception as e:
        logger.warning(f"URL validation failed for {url}: {e}")
        return False

async def ssrf_safe_fetch(url: str, max_redirects: int = 5) -> Optional[str]:
    """
    C4: Redirect-aware, IP-validated HTTP fetcher.
    Follows redirects manually (up to max_redirects hops), re-validating
    the target URL against SSRF checks on every hop.
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
                response = await client.get(current_url)
                
                if response.is_redirect:
                    location = response.headers.get("location", "")
                    if not location:
                        return None
                    # Resolve relative redirects
                    current_url = str(response.url.join(location))
                    continue
                
                response.raise_for_status()
                return response.text
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
        Emit a progress event. In a full implementation, this would push to a Redis PubSub channel
        or a queue that the SSE endpoint listens to, allowing the frontend to show live progress.
        """
        event = {
            "agent": self.name,
            "status": status,
            "timestamp": time.time(),
        }
        if error:
            event["error"] = error
            
        # TODO: Push event to Redis PubSub or Memory cache for SSE streaming
        logger.debug(f"Progress Event [{session_id}]: {event}")
