"""
HTTP webhook sender adapter.
"""

import hashlib
import hmac
import json
import logging
from typing import Dict, Optional

import httpx

from ..core.interfaces import WebhookSender

logger = logging.getLogger(__name__)


class HttpWebhookSender:
    """HTTP-based webhook sender implementation."""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC SHA-256 signature for webhook payload."""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    async def send(
        self,
        url: str,
        payload: Dict[str, any],
        secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Send a webhook payload to a URL."""
        
        # Prepare payload
        payload_json = json.dumps(payload, separators=(',', ':'))
        
        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "UE-Hub-Webhook/1.0",
            "X-UE-Timestamp": str(int(payload.get("timestamp", 0))),
        }
        
        if headers:
            request_headers.update(headers)
        
        # Add signature if secret provided
        if secret:
            signature = self._generate_signature(payload_json, secret)
            request_headers["X-UE-Signature"] = signature
        
        # Send webhook with retries
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url,
                        content=payload_json,
                        headers=request_headers
                    )
                
                # Log response
                logger.info(
                    f"Webhook sent to {url} - "
                    f"Status: {response.status_code}, "
                    f"Attempt: {attempt + 1}/{self.max_retries}"
                )
                
                # Consider 2xx status codes as success
                if 200 <= response.status_code < 300:
                    return True
                
                # Log error response
                logger.warning(
                    f"Webhook failed with status {response.status_code}: "
                    f"{response.text[:200]}"
                )
            
            except httpx.TimeoutException:
                logger.warning(f"Webhook timeout to {url} (attempt {attempt + 1})")
            
            except httpx.RequestError as e:
                logger.warning(f"Webhook request error to {url}: {e} (attempt {attempt + 1})")
            
            except Exception as e:
                logger.error(f"Unexpected webhook error to {url}: {e} (attempt {attempt + 1})")
            
            # Don't retry on last attempt
            if attempt < self.max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                import asyncio
                await asyncio.sleep(2 ** attempt)
        
        logger.error(f"Webhook failed after {self.max_retries} attempts to {url}")
        return False
    
    async def send_signed(
        self,
        url: str,
        payload: Dict[str, any],
        secret: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Send a signed webhook payload."""
        return await self.send(url, payload, secret, headers)
    
    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature."""
        if not signature.startswith("sha256="):
            return False
        
        expected_signature = self._generate_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    async def send_test_webhook(self, url: str, secret: Optional[str] = None) -> bool:
        """Send a test webhook to verify endpoint."""
        test_payload = {
            "event": "webhook.test",
            "timestamp": int(__import__('time').time()),
            "data": {
                "message": "This is a test webhook from UE Hub",
                "test": True
            }
        }
        
        return await self.send(url, test_payload, secret)
    
    async def send_batch(
        self,
        webhooks: list[Dict[str, any]],
        payload: Dict[str, any]
    ) -> Dict[str, bool]:
        """Send webhook to multiple endpoints."""
        results = {}
        
        # Send all webhooks concurrently
        import asyncio
        tasks = []
        
        for webhook in webhooks:
            task = self.send(
                url=webhook["url"],
                payload=payload,
                secret=webhook.get("secret"),
                headers=webhook.get("headers")
            )
            tasks.append((webhook["url"], task))
        
        # Wait for all to complete
        for url, task in tasks:
            try:
                success = await task
                results[url] = success
            except Exception as e:
                logger.error(f"Batch webhook error for {url}: {e}")
                results[url] = False
        
        return results
