"""
Core interfaces (ports) for the application.
These define contracts that adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping, Optional, Protocol, Sequence


class Repository(Protocol):
    """Base repository interface for data access."""
    
    async def get(self, id: str) -> Optional[Any]:
        """Get a single entity by ID."""
        ...
    
    async def list(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """List entities with pagination and filtering."""
        ...
    
    async def create(self, data: Dict[str, Any]) -> Any:
        """Create a new entity."""
        ...
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Any]:
        """Update an existing entity."""
        ...
    
    async def delete(self, id: str) -> bool:
        """Delete an entity by ID."""
        ...


class CacheService(Protocol):
    """Cache service interface."""
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from cache."""
        ...
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value in cache with optional TTL."""
        ...
    
    async def delete(self, key: str) -> None:
        """Delete a key from cache."""
        ...
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        ...


class StorageService(Protocol):
    """File storage service interface."""
    
    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        """Upload a file and return its URL."""
        ...
    
    async def download(self, key: str) -> bytes:
        """Download a file by key."""
        ...
    
    async def delete(self, key: str) -> None:
        """Delete a file by key."""
        ...
    
    async def exists(self, key: str) -> bool:
        """Check if a file exists."""
        ...
    
    async def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get a signed URL for a file."""
        ...


class PDFService(Protocol):
    """PDF generation service interface."""
    
    async def render_certificate(
        self, 
        template: str, 
        data: Dict[str, Any]
    ) -> bytes:
        """Render a certificate PDF from template and data."""
        ...
    
    async def render_report(
        self, 
        template: str, 
        data: Dict[str, Any]
    ) -> bytes:
        """Render a report PDF from template and data."""
        ...


class MailService(Protocol):
    """Email service interface."""
    
    async def send(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Send an email."""
        ...
    
    async def send_template(
        self,
        to: str,
        template: str,
        data: Dict[str, Any],
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Send an email using a template."""
        ...


class WebhookSender(Protocol):
    """Webhook sender interface."""
    
    async def send(
        self,
        url: str,
        payload: Dict[str, Any],
        secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Send a webhook payload to a URL."""
        ...
    
    async def send_signed(
        self,
        url: str,
        payload: Dict[str, Any],
        secret: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Send a signed webhook payload."""
        ...


class EventBus(Protocol):
    """Event bus interface for pub/sub messaging."""
    
    async def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        """Publish an event to a topic."""
        ...
    
    async def subscribe(
        self, 
        topic: str, 
        handler: callable,
        group: Optional[str] = None
    ) -> None:
        """Subscribe to a topic with a handler function."""
        ...
    
    async def unsubscribe(self, topic: str, handler: callable) -> None:
        """Unsubscribe a handler from a topic."""
        ...


class QueueService(Protocol):
    """Background job queue interface."""
    
    async def enqueue(
        self,
        func: str,
        *args,
        delay: Optional[int] = None,
        retry: bool = True,
        **kwargs
    ) -> str:
        """Enqueue a background job."""
        ...
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status by ID."""
        ...
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job by ID."""
        ...


class SearchService(Protocol):
    """Search service interface."""
    
    async def index_document(
        self, 
        index: str, 
        doc_id: str, 
        document: Dict[str, Any]
    ) -> None:
        """Index a document for search."""
        ...
    
    async def search(
        self,
        index: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Search for documents."""
        ...
    
    async def delete_document(self, index: str, doc_id: str) -> None:
        """Delete a document from the search index."""
        ...


# Domain-specific repository interfaces
class UserRepository(Repository, Protocol):
    """User repository interface."""
    
    async def get_by_email(self, email: str) -> Optional[Any]:
        """Get user by email address."""
        ...
    
    async def verify_password(self, user: Any, password: str) -> bool:
        """Verify user password."""
        ...


class InventoryRepository(Repository, Protocol):
    """Inventory repository interface."""
    
    async def get_by_sku(self, sku: str) -> Optional[Any]:
        """Get inventory item by SKU."""
        ...
    
    async def get_by_barcode(self, barcode: str) -> Optional[Any]:
        """Get inventory item by barcode."""
        ...
    
    async def get_low_stock_items(self, threshold: Optional[int] = None) -> List[Any]:
        """Get items with low stock."""
        ...
    
    async def update_quantity(self, item_id: str, delta: int, reason: str, actor_id: str) -> Any:
        """Update item quantity and log the change."""
        ...


class TrainingRepository(Repository, Protocol):
    """Training repository interface."""
    
    async def get_active_modules(self) -> List[Any]:
        """Get all active training modules."""
        ...
    
    async def get_user_attempts(self, user_id: str, module_id: Optional[str] = None) -> List[Any]:
        """Get training attempts for a user."""
        ...
    
    async def get_completion_stats(self, module_id: str) -> Dict[str, Any]:
        """Get completion statistics for a module."""
        ...


class CertificateRepository(Repository, Protocol):
    """Certificate repository interface."""
    
    async def get_by_attempt(self, attempt_id: str) -> Optional[Any]:
        """Get certificate by training attempt ID."""
        ...
    
    async def get_user_certificates(self, user_id: str) -> List[Any]:
        """Get all certificates for a user."""
        ...


class FeatureFlagRepository(Repository, Protocol):
    """Feature flag repository interface."""
    
    async def get_by_key(self, key: str) -> Optional[Any]:
        """Get feature flag by key."""
        ...
    
    async def get_all_enabled(self) -> List[Any]:
        """Get all enabled feature flags."""
        ...
    
    async def is_enabled(self, key: str) -> bool:
        """Check if a feature flag is enabled."""
        ...


class WebhookRepository(Repository, Protocol):
    """Webhook repository interface."""
    
    async def get_by_kind(self, kind: str) -> List[Any]:
        """Get webhooks by kind/event type."""
        ...
    
    async def get_active_webhooks(self) -> List[Any]:
        """Get all active webhooks."""
        ...
    
    async def log_delivery(
        self, 
        webhook_id: str, 
        payload: Dict[str, Any], 
        success: bool, 
        response: Optional[str] = None
    ) -> None:
        """Log webhook delivery attempt."""
        ...
