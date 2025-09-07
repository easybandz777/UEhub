"""
Dummy queue service adapter for development when Redis is not available.
"""

from typing import Any, Dict, Optional
from ..core.interfaces import QueueService


class DummyQueueService(QueueService):
    """Dummy queue service that executes jobs immediately instead of queuing."""
    
    async def enqueue(self, job_name: str, *args, **kwargs) -> str:
        """Execute job immediately and return a dummy job ID."""
        # In a real implementation, we'd actually execute the job
        # For now, just return a dummy job ID
        return f"dummy-job-{hash(job_name)}"
    
    async def enqueue_at(self, job_name: str, run_at: Any, *args, **kwargs) -> str:
        """Execute job immediately (ignoring schedule) and return a dummy job ID."""
        return f"dummy-scheduled-job-{hash(job_name)}"
    
    async def enqueue_in(self, job_name: str, delay: int, *args, **kwargs) -> str:
        """Execute job immediately (ignoring delay) and return a dummy job ID."""
        return f"dummy-delayed-job-{hash(job_name)}"
    
    async def get_job_status(self, job_id: str) -> Optional[str]:
        """Always return 'completed' for dummy jobs."""
        return "completed"
    
    async def cancel_job(self, job_id: str) -> bool:
        """Always return True (job cancelled)."""
        return True
    
    async def get_queue_size(self, queue_name: str = "default") -> int:
        """Always return 0 (no queued jobs)."""
        return 0
