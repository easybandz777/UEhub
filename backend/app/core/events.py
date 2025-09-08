"""
Event system for decoupled module communication.
Supports both in-process and Redis-based pub/sub.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from .interfaces import EventBus
from .settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class InProcessEventBus:
    """In-process event bus for development and testing."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._running = False
    
    async def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        """Publish an event to all subscribers."""
        logger.info(f"Publishing event to topic '{topic}': {payload}")
        
        handlers = self._handlers.get(topic, [])
        if not handlers:
            logger.warning(f"No handlers registered for topic '{topic}'")
            return
        
        # Execute handlers concurrently
        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(payload))
                else:
                    # Run sync handlers in thread pool
                    tasks.append(asyncio.get_event_loop().run_in_executor(None, handler, payload))
            except Exception as e:
                logger.error(f"Error preparing handler {handler.__name__} for topic '{topic}': {e}")
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    handler_name = handlers[i].__name__
                    logger.error(f"Handler {handler_name} failed for topic '{topic}': {result}")
    
    async def subscribe(
        self, 
        topic: str, 
        handler: Callable,
        group: Optional[str] = None
    ) -> None:
        """Subscribe to a topic."""
        if topic not in self._handlers:
            self._handlers[topic] = []
        
        if handler not in self._handlers[topic]:
            self._handlers[topic].append(handler)
            logger.info(f"Subscribed {handler.__name__} to topic '{topic}'")
    
    async def unsubscribe(self, topic: str, handler: Callable) -> None:
        """Unsubscribe from a topic."""
        if topic in self._handlers and handler in self._handlers[topic]:
            self._handlers[topic].remove(handler)
            logger.info(f"Unsubscribed {handler.__name__} from topic '{topic}'")
            
            if not self._handlers[topic]:
                del self._handlers[topic]


class RedisEventBus:
    """Redis-based event bus for production."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis: Optional[Redis] = None
        self._handlers: Dict[str, List[Callable]] = {}
        self._subscriber_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
    
    async def _get_redis(self) -> Redis:
        """Get Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url)
        return self._redis
    
    async def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        """Publish an event to Redis."""
        redis_client = await self._get_redis()
        message = json.dumps(payload)
        
        logger.info(f"Publishing event to Redis topic '{topic}': {payload}")
        await redis_client.publish(topic, message)
    
    async def subscribe(
        self, 
        topic: str, 
        handler: Callable,
        group: Optional[str] = None
    ) -> None:
        """Subscribe to a Redis topic."""
        if topic not in self._handlers:
            self._handlers[topic] = []
        
        if handler not in self._handlers[topic]:
            self._handlers[topic].append(handler)
            logger.info(f"Subscribed {handler.__name__} to Redis topic '{topic}'")
        
        # Start subscriber task if not already running
        if topic not in self._subscriber_tasks:
            task = asyncio.create_task(self._subscribe_to_topic(topic))
            self._subscriber_tasks[topic] = task
    
    async def unsubscribe(self, topic: str, handler: Callable) -> None:
        """Unsubscribe from a Redis topic."""
        if topic in self._handlers and handler in self._handlers[topic]:
            self._handlers[topic].remove(handler)
            logger.info(f"Unsubscribed {handler.__name__} from Redis topic '{topic}'")
            
            # Stop subscriber task if no more handlers
            if not self._handlers[topic]:
                del self._handlers[topic]
                if topic in self._subscriber_tasks:
                    self._subscriber_tasks[topic].cancel()
                    del self._subscriber_tasks[topic]
    
    async def _subscribe_to_topic(self, topic: str) -> None:
        """Subscribe to a Redis topic and handle messages."""
        redis_client = await self._get_redis()
        pubsub = redis_client.pubsub()
        
        try:
            await pubsub.subscribe(topic)
            logger.info(f"Started Redis subscriber for topic '{topic}'")
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        payload = json.loads(message["data"])
                        await self._handle_message(topic, payload)
                    except Exception as e:
                        logger.error(f"Error handling Redis message for topic '{topic}': {e}")
        
        except asyncio.CancelledError:
            logger.info(f"Redis subscriber for topic '{topic}' cancelled")
        except Exception as e:
            logger.error(f"Redis subscriber error for topic '{topic}': {e}")
        finally:
            await pubsub.unsubscribe(topic)
            await pubsub.close()
    
    async def _handle_message(self, topic: str, payload: Dict[str, Any]) -> None:
        """Handle incoming Redis message."""
        handlers = self._handlers.get(topic, [])
        if not handlers:
            return
        
        logger.info(f"Handling Redis message for topic '{topic}': {payload}")
        
        # Execute handlers concurrently
        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(payload))
                else:
                    tasks.append(asyncio.get_event_loop().run_in_executor(None, handler, payload))
            except Exception as e:
                logger.error(f"Error preparing handler {handler.__name__} for topic '{topic}': {e}")
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    handler_name = handlers[i].__name__
                    logger.error(f"Handler {handler_name} failed for topic '{topic}': {result}")
    
    async def close(self) -> None:
        """Close Redis connections and cancel tasks."""
        # Cancel all subscriber tasks
        for task in self._subscriber_tasks.values():
            task.cancel()
        
        if self._subscriber_tasks:
            await asyncio.gather(*self._subscriber_tasks.values(), return_exceptions=True)
        
        if self._redis:
            await self._redis.close()


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    
    if _event_bus is None:
        # Always use in-process event bus for now to avoid Redis connection issues
        logger.info("Using in-process event bus")
        _event_bus = InProcessEventBus()
    
    return _event_bus


# Event decorators for easy subscription
def event_handler(topic: str, group: Optional[str] = None):
    """Decorator to register an event handler."""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        # Register the handler
        event_bus = get_event_bus()
        asyncio.create_task(event_bus.subscribe(topic, wrapper, group))
        
        return wrapper
    return decorator


# Domain events
class DomainEvent:
    """Base class for domain events."""
    
    def __init__(self, event_type: str, payload: Dict[str, Any]):
        self.event_type = event_type
        self.payload = payload
    
    async def publish(self) -> None:
        """Publish this domain event."""
        event_bus = get_event_bus()
        await event_bus.publish(self.event_type, self.payload)


# Common domain events
class UserCreatedEvent(DomainEvent):
    def __init__(self, user_id: str, email: str, role: str):
        super().__init__("user.created", {
            "user_id": user_id,
            "email": email,
            "role": role
        })


class InventoryUpdatedEvent(DomainEvent):
    def __init__(self, item_id: str, sku: str, old_qty: int, new_qty: int, reason: str, actor_id: str):
        super().__init__("inventory.updated", {
            "item_id": item_id,
            "sku": sku,
            "old_qty": old_qty,
            "new_qty": new_qty,
            "delta": new_qty - old_qty,
            "reason": reason,
            "actor_id": actor_id
        })


class TrainingAttemptStartedEvent(DomainEvent):
    def __init__(self, attempt_id: str, user_id: str, module_id: str):
        super().__init__("training.attempt.started", {
            "attempt_id": attempt_id,
            "user_id": user_id,
            "module_id": module_id
        })


class TrainingAttemptCompletedEvent(DomainEvent):
    def __init__(self, attempt_id: str, user_id: str, module_id: str, score: float, passed: bool):
        super().__init__("training.attempt.completed", {
            "attempt_id": attempt_id,
            "user_id": user_id,
            "module_id": module_id,
            "score": score,
            "passed": passed
        })


class CertificateIssuedEvent(DomainEvent):
    def __init__(self, certificate_id: str, attempt_id: str, user_id: str, pdf_url: str):
        super().__init__("certificate.issued", {
            "certificate_id": certificate_id,
            "attempt_id": attempt_id,
            "user_id": user_id,
            "pdf_url": pdf_url
        })


class WebhookDeliveredEvent(DomainEvent):
    def __init__(self, webhook_id: str, event_type: str, success: bool, response_code: Optional[int] = None):
        super().__init__("webhook.delivered", {
            "webhook_id": webhook_id,
            "event_type": event_type,
            "success": success,
            "response_code": response_code
        })
