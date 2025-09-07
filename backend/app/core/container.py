"""
Dependency injection container.
Wires concrete adapters to interface ports based on configuration.
"""

import logging
from functools import lru_cache
from typing import Optional

from .events import get_event_bus
from .interfaces import (
    CacheService,
    EventBus,
    MailService,
    PDFService,
    QueueService,
    StorageService,
    WebhookSender,
)
from .settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class Container:
    """Dependency injection container."""
    
    def __init__(self):
        self._cache_service: Optional[CacheService] = None
        self._storage_service: Optional[StorageService] = None
        self._pdf_service: Optional[PDFService] = None
        self._mail_service: Optional[MailService] = None
        self._webhook_sender: Optional[WebhookSender] = None
        self._queue_service: Optional[QueueService] = None
        self._event_bus: Optional[EventBus] = None
    
    @property
    def cache_service(self) -> CacheService:
        """Get cache service adapter."""
        if self._cache_service is None:
            try:
                from ..adapters.cache_redis import RedisCacheService
                self._cache_service = RedisCacheService(settings.redis.url)
                logger.info("Initialized Redis cache service")
            except Exception as e:
                logger.warning(f"Redis cache service failed to initialize: {e}. Using dummy cache.")
                # Create a dummy cache service that doesn't actually cache
                from ..adapters.cache_dummy import DummyCacheService
                self._cache_service = DummyCacheService()
        return self._cache_service
    
    @property
    def storage_service(self) -> StorageService:
        """Get storage service adapter."""
        if self._storage_service is None:
            if settings.storage.backend == "s3":
                from ..adapters.storage_s3 import S3StorageService
                self._storage_service = S3StorageService(
                    bucket=settings.storage.s3_bucket,
                    region=settings.storage.s3_region,
                    access_key=settings.storage.s3_access_key,
                    secret_key=settings.storage.s3_secret_key,
                    endpoint_url=settings.storage.s3_endpoint_url,
                )
                logger.info(f"Initialized S3 storage service (bucket: {settings.storage.s3_bucket})")
            else:
                from ..adapters.storage_local import LocalStorageService
                self._storage_service = LocalStorageService(settings.storage.local_path)
                logger.info(f"Initialized local storage service (path: {settings.storage.local_path})")
        return self._storage_service
    
    @property
    def pdf_service(self) -> PDFService:
        """Get PDF service adapter."""
        if self._pdf_service is None:
            from ..adapters.pdf_weasyprint import WeasyPrintPDFService
            self._pdf_service = WeasyPrintPDFService()
            logger.info("Initialized WeasyPrint PDF service")
        return self._pdf_service
    
    @property
    def mail_service(self) -> MailService:
        """Get mail service adapter."""
        if self._mail_service is None:
            if settings.mail.backend == "resend":
                from ..adapters.mail_resend import ResendMailService
                self._mail_service = ResendMailService(
                    api_key=settings.mail.resend_api_key,
                    from_email=settings.mail.from_email,
                    from_name=settings.mail.from_name,
                )
                logger.info("Initialized Resend mail service")
            else:
                from ..adapters.mail_console import ConsoleMailService
                self._mail_service = ConsoleMailService(
                    from_email=settings.mail.from_email,
                    from_name=settings.mail.from_name,
                )
                logger.info("Initialized console mail service")
        return self._mail_service
    
    @property
    def webhook_sender(self) -> WebhookSender:
        """Get webhook sender adapter."""
        if self._webhook_sender is None:
            from ..adapters.webhook_http import HttpWebhookSender
            self._webhook_sender = HttpWebhookSender()
            logger.info("Initialized HTTP webhook sender")
        return self._webhook_sender
    
    @property
    def queue_service(self) -> QueueService:
        """Get queue service adapter."""
        if self._queue_service is None:
            try:
                from ..adapters.queue_rq import RQQueueService
                self._queue_service = RQQueueService(settings.redis.url)
                logger.info("Initialized RQ queue service")
            except Exception as e:
                logger.warning(f"RQ queue service failed to initialize: {e}. Using dummy queue.")
                # Create a dummy queue service for development
                from ..adapters.queue_dummy import DummyQueueService
                self._queue_service = DummyQueueService()
        return self._queue_service
    
    @property
    def event_bus(self) -> EventBus:
        """Get event bus."""
        if self._event_bus is None:
            self._event_bus = get_event_bus()
            logger.info(f"Initialized event bus: {type(self._event_bus).__name__}")
        return self._event_bus


# Global container instance
_container: Optional[Container] = None


@lru_cache()
def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container


# FastAPI dependencies
def get_cache_service() -> CacheService:
    """FastAPI dependency for cache service."""
    return get_container().cache_service


def get_storage_service() -> StorageService:
    """FastAPI dependency for storage service."""
    return get_container().storage_service


def get_pdf_service() -> PDFService:
    """FastAPI dependency for PDF service."""
    return get_container().pdf_service


def get_mail_service() -> MailService:
    """FastAPI dependency for mail service."""
    return get_container().mail_service


def get_webhook_sender() -> WebhookSender:
    """FastAPI dependency for webhook sender."""
    return get_container().webhook_sender


def get_queue_service() -> QueueService:
    """FastAPI dependency for queue service."""
    return get_container().queue_service


def get_event_bus_dep() -> EventBus:
    """FastAPI dependency for event bus."""
    return get_container().event_bus
