"""
Certificate generation jobs.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from app.core.container import get_container
from app.core.db import get_db_session
from app.modules.training.repository import TrainingRepository
from app.modules.certs.repository import CertificateRepository

logger = logging.getLogger(__name__)


async def generate_certificate(attempt_id: str) -> Dict[str, Any]:
    """Generate a certificate for a training attempt."""
    logger.info(f"Generating certificate for attempt {attempt_id}")
    
    try:
        container = get_container()
        
        async with get_db_session() as db:
            # Get training attempt
            training_repo = TrainingRepository(db)
            attempt = await training_repo.get_attempt(attempt_id)
            
            if not attempt:
                raise ValueError(f"Training attempt {attempt_id} not found")
            
            if not attempt.passed:
                raise ValueError(f"Cannot generate certificate for failed attempt {attempt_id}")
            
            # Check if certificate already exists
            cert_repo = CertificateRepository(db)
            existing_cert = await cert_repo.get_by_attempt(attempt_id)
            
            if existing_cert:
                logger.info(f"Certificate already exists for attempt {attempt_id}")
                return {
                    "certificate_id": existing_cert.id,
                    "pdf_url": existing_cert.pdf_url,
                    "already_existed": True
                }
            
            # Get training module and user details
            module = await training_repo.get_module(attempt.module_id)
            user = await training_repo.get_user(attempt.user_id)  # Assuming this method exists
            
            # Prepare certificate data
            cert_data = {
                "user_name": user.name,
                "user_email": user.email,
                "module_title": module.title,
                "completion_date": attempt.completed_at.strftime("%B %d, %Y"),
                "score": attempt.score,
                "duration": module.duration_min,
                "certificate_id": f"UE-{attempt_id[:8].upper()}",
            }
            
            # Generate PDF
            pdf_service = container.pdf_service
            pdf_bytes = await pdf_service.render_certificate("certificate", cert_data)
            
            # Store PDF
            storage_service = container.storage_service
            pdf_key = f"certificates/{attempt_id}.pdf"
            pdf_url = await storage_service.upload(pdf_key, pdf_bytes, "application/pdf")
            
            # Create certificate record
            certificate = await cert_repo.create({
                "attempt_id": attempt_id,
                "pdf_url": pdf_url,
                "issued_at": datetime.utcnow(),
                "hash": _generate_certificate_hash(pdf_bytes),
            })
            
            logger.info(f"Certificate generated successfully: {certificate.id}")
            
            # Publish certificate issued event
            from app.core.events import CertificateIssuedEvent
            event = CertificateIssuedEvent(
                certificate_id=certificate.id,
                attempt_id=attempt_id,
                user_id=attempt.user_id,
                pdf_url=pdf_url
            )
            await event.publish()
            
            return {
                "certificate_id": certificate.id,
                "pdf_url": pdf_url,
                "issued_at": certificate.issued_at.isoformat(),
            }
    
    except Exception as e:
        logger.error(f"Error generating certificate for attempt {attempt_id}: {e}")
        raise


def _generate_certificate_hash(pdf_bytes: bytes) -> str:
    """Generate SHA-256 hash of certificate PDF for verification."""
    import hashlib
    return hashlib.sha256(pdf_bytes).hexdigest()


async def send_certificate_notification(certificate_id: str) -> None:
    """Send notification when certificate is issued."""
    logger.info(f"Sending certificate notification for {certificate_id}")
    
    try:
        container = get_container()
        
        async with get_db_session() as db:
            cert_repo = CertificateRepository(db)
            certificate = await cert_repo.get(certificate_id)
            
            if not certificate:
                raise ValueError(f"Certificate {certificate_id} not found")
            
            # Get training attempt and user details
            training_repo = TrainingRepository(db)
            attempt = await training_repo.get_attempt(certificate.attempt_id)
            user = await training_repo.get_user(attempt.user_id)
            module = await training_repo.get_module(attempt.module_id)
            
            # Send email notification
            mail_service = container.mail_service
            await mail_service.send_template(
                to=user.email,
                template="training_completed",
                data={
                    "name": user.name,
                    "module_title": module.title,
                    "score": attempt.score,
                    "certificate_url": certificate.pdf_url,
                }
            )
            
            logger.info(f"Certificate notification sent to {user.email}")
    
    except Exception as e:
        logger.error(f"Error sending certificate notification: {e}")
        raise


async def cleanup_expired_certificates() -> Dict[str, int]:
    """Clean up expired or invalid certificates (maintenance job)."""
    logger.info("Starting certificate cleanup job")
    
    try:
        container = get_container()
        cleaned_count = 0
        
        async with get_db_session() as db:
            cert_repo = CertificateRepository(db)
            
            # Get certificates older than 5 years (example policy)
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=5*365)
            
            old_certificates = await cert_repo.get_certificates_before_date(cutoff_date)
            
            for cert in old_certificates:
                try:
                    # Remove from storage
                    storage_service = container.storage_service
                    pdf_key = f"certificates/{cert.attempt_id}.pdf"
                    await storage_service.delete(pdf_key)
                    
                    # Mark as archived (don't delete record for audit)
                    await cert_repo.update(cert.id, {"archived": True})
                    cleaned_count += 1
                    
                except Exception as e:
                    logger.error(f"Error cleaning certificate {cert.id}: {e}")
        
        logger.info(f"Certificate cleanup completed: {cleaned_count} certificates archived")
        return {"cleaned_count": cleaned_count}
    
    except Exception as e:
        logger.error(f"Error in certificate cleanup job: {e}")
        raise
