"""
Background worker for UE Hub.
Processes jobs from Redis queue using RQ.
"""

import logging
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import redis
from rq import Worker, Queue, Connection

from app.core.settings import get_settings
from jobs import certs, reports, notifications

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def main():
    """Main worker function."""
    settings = get_settings()
    
    # Connect to Redis
    redis_conn = redis.from_url(settings.redis.url)
    
    # Define queues to listen to
    queues = [
        Queue('default', connection=redis_conn),
        Queue('certificates', connection=redis_conn),
        Queue('reports', connection=redis_conn),
        Queue('notifications', connection=redis_conn),
        Queue('webhooks', connection=redis_conn),
    ]
    
    logger.info(f"Starting worker listening to queues: {[q.name for q in queues]}")
    
    # Start worker
    with Connection(redis_conn):
        worker = Worker(
            queues,
            name=f"ue-hub-worker-{os.getpid()}",
            connection=redis_conn
        )
        
        try:
            worker.work(with_scheduler=True)
        except KeyboardInterrupt:
            logger.info("Worker interrupted, shutting down...")
        except Exception as e:
            logger.error(f"Worker error: {e}")
            raise

if __name__ == "__main__":
    main()
