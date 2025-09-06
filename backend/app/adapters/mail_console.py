"""
Console mail service adapter for development.
"""

import logging
from typing import Dict, List, Optional

from ..core.interfaces import MailService

logger = logging.getLogger(__name__)


class ConsoleMailService:
    """Console-based mail service for development."""
    
    def __init__(self, from_email: str = "noreply@uehub.com", from_name: str = "UE Hub"):
        self.from_email = from_email
        self.from_name = from_name
    
    async def send(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None,
        attachments: Optional[List[Dict[str, any]]] = None,
    ) -> None:
        """Send an email (log to console)."""
        
        # Log email details
        logger.info("=" * 60)
        logger.info("📧 EMAIL SENT (Console Mode)")
        logger.info("=" * 60)
        logger.info(f"From: {self.from_name} <{self.from_email}>")
        logger.info(f"To: {to}")
        logger.info(f"Subject: {subject}")
        logger.info("-" * 60)
        
        if text:
            logger.info("TEXT CONTENT:")
            logger.info(text)
            logger.info("-" * 60)
        
        logger.info("HTML CONTENT:")
        logger.info(html)
        
        if attachments:
            logger.info("-" * 60)
            logger.info("ATTACHMENTS:")
            for attachment in attachments:
                logger.info(f"  - {attachment.get('filename', 'unknown')}")
        
        logger.info("=" * 60)
    
    async def send_template(
        self,
        to: str,
        template: str,
        data: Dict[str, any],
        attachments: Optional[List[Dict[str, any]]] = None,
    ) -> None:
        """Send an email using a template."""
        
        # Simple template rendering (in production, use a proper template engine)
        templates = {
            "welcome": {
                "subject": "Welcome to UE Hub!",
                "html": f"""
                <h1>Welcome to UE Hub, {data.get('name', 'User')}!</h1>
                <p>Your account has been created with the role: <strong>{data.get('role', 'worker')}</strong></p>
                <p>You can now log in to the system and start using UE Hub.</p>
                <p>Best regards,<br>The UE Hub Team</p>
                """,
                "text": f"""
                Welcome to UE Hub, {data.get('name', 'User')}!
                
                Your account has been created with the role: {data.get('role', 'worker')}
                
                You can now log in to the system and start using UE Hub.
                
                Best regards,
                The UE Hub Team
                """
            },
            "password_reset": {
                "subject": "Password Reset Request",
                "html": f"""
                <h1>Password Reset Request</h1>
                <p>Hello {data.get('name', 'User')},</p>
                <p>You requested a password reset for your UE Hub account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{data.get('reset_url', '#')}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this reset, please ignore this email.</p>
                <p>Best regards,<br>The UE Hub Team</p>
                """,
                "text": f"""
                Password Reset Request
                
                Hello {data.get('name', 'User')},
                
                You requested a password reset for your UE Hub account.
                
                Use this link to reset your password:
                {data.get('reset_url', '#')}
                
                This link will expire in 1 hour.
                
                If you didn't request this reset, please ignore this email.
                
                Best regards,
                The UE Hub Team
                """
            },
            "training_completed": {
                "subject": "Training Completed",
                "html": f"""
                <h1>Training Completed!</h1>
                <p>Congratulations {data.get('name', 'User')}!</p>
                <p>You have successfully completed the training module: <strong>{data.get('module_title', 'Training')}</strong></p>
                <p>Your score: <strong>{data.get('score', 0)}%</strong></p>
                {f'<p>Your certificate is available <a href="{data.get("certificate_url")}">here</a>.</p>' if data.get('certificate_url') else ''}
                <p>Best regards,<br>The UE Hub Team</p>
                """,
                "text": f"""
                Training Completed!
                
                Congratulations {data.get('name', 'User')}!
                
                You have successfully completed the training module: {data.get('module_title', 'Training')}
                
                Your score: {data.get('score', 0)}%
                
                {f'Your certificate is available at: {data.get("certificate_url")}' if data.get('certificate_url') else ''}
                
                Best regards,
                The UE Hub Team
                """
            },
            "low_stock_alert": {
                "subject": "Low Stock Alert",
                "html": f"""
                <h1>⚠️ Low Stock Alert</h1>
                <p>The following items are running low on stock:</p>
                <ul>
                {''.join([f'<li><strong>{item.get("name", "Unknown")}</strong> (SKU: {item.get("sku", "N/A")}) - Current: {item.get("current_qty", 0)}, Min: {item.get("min_qty", 0)}</li>' for item in data.get('items', [])])}
                </ul>
                <p>Please restock these items as soon as possible.</p>
                <p>Best regards,<br>UE Hub System</p>
                """,
                "text": f"""
                Low Stock Alert
                
                The following items are running low on stock:
                
                {chr(10).join([f'- {item.get("name", "Unknown")} (SKU: {item.get("sku", "N/A")}) - Current: {item.get("current_qty", 0)}, Min: {item.get("min_qty", 0)}' for item in data.get('items', [])])}
                
                Please restock these items as soon as possible.
                
                Best regards,
                UE Hub System
                """
            }
        }
        
        template_data = templates.get(template)
        if not template_data:
            logger.error(f"Unknown email template: {template}")
            return
        
        await self.send(
            to=to,
            subject=template_data["subject"],
            html=template_data["html"],
            text=template_data["text"],
            attachments=attachments
        )
