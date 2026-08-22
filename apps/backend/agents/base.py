import asyncio
import time
from typing import Any, Dict, Optional
from pydantic import BaseModel
from loguru import logger
import urllib.parse
import socket
import ipaddress

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
            
        # Resolve hostname to IP
        ip_addr = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_addr)
        
        # Block internal/private IPs
        if ip.is_loopback or ip.is_private or ip.is_multicast or ip.is_reserved:
            return False
            
        return True
    except Exception as e:
        logger.warning(f"URL validation failed for {url}: {e}")
        return False

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
