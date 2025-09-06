"""Sentry configuration for error tracking and performance monitoring."""

import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry() -> None:
    """Initialize Sentry for error tracking and performance monitoring."""
    
    dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")
    
    if not dsn:
        print("Sentry DSN not configured, skipping Sentry initialization")
        return
    
    # Configure integrations
    integrations = [
        FastApiIntegration(
            transaction_style="endpoint",
        ),
        SqlalchemyIntegration(),
        RedisIntegration(),
        LoggingIntegration(
            level=None,  # Capture all log levels
            event_level=None,  # Don't send logs as events
        ),
    ]
    
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=integrations,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of the transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.1 if environment == "production" else 1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=0.1 if environment == "production" else 1.0,
        # Capture 100% of the errors
        sample_rate=1.0,
        # Release tracking
        release=os.getenv("SENTRY_RELEASE"),
        # Additional options
        attach_stacktrace=True,
        send_default_pii=False,  # Don't send personally identifiable information
        max_breadcrumbs=50,
        before_send=_before_send,
    )
    
    print(f"Sentry initialized for environment: {environment}")


def _before_send(event, hint):
    """Filter events before sending to Sentry."""
    
    # Don't send events in development
    if os.getenv("ENVIRONMENT") == "development":
        print(f"Sentry Event (dev): {event.get('message', 'No message')}")
        return None
    
    # Filter out health check errors
    if event.get("request", {}).get("url", "").endswith("/health"):
        return None
    
    return event


def capture_exception(exception: Exception, **kwargs) -> None:
    """Capture an exception with Sentry."""
    sentry_sdk.capture_exception(exception, **kwargs)


def capture_message(message: str, level: str = "info", **kwargs) -> None:
    """Capture a message with Sentry."""
    sentry_sdk.capture_message(message, level=level, **kwargs)


def set_user(user_id: str, email: str = None, **kwargs) -> None:
    """Set user context for Sentry."""
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        **kwargs
    })


def set_tag(key: str, value: str) -> None:
    """Set a tag for Sentry."""
    sentry_sdk.set_tag(key, value)


def set_context(key: str, context: dict) -> None:
    """Set context for Sentry."""
    sentry_sdk.set_context(key, context)
