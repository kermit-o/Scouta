# backend/services/call_log_service.py
import uuid
import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class CallLogService:
    @staticmethod
    async def log_call(
        db: AsyncSession,
        caller_number: str,
        intent_detected: Optional[str] = None,
        resolution_status: Optional[str] = None,
        call_duration: Optional[int] = None,
        recording_url: Optional[str] = None,
    ) -> None:
        """
        Inserta en call_logs. La tabla ya existe en db/init.sql.
        """
        try:
            await db.execute(
                text(
                    """
                    INSERT INTO call_logs (
                        id, caller_number, call_duration, intent_detected,
                        resolution_status, recording_url
                    )
                    VALUES (
                        :id, :caller_number, :call_duration, :intent_detected,
                        :resolution_status, :recording_url
                    )
                    """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "caller_number": caller_number,
                    "call_duration": call_duration,
                    "intent_detected": intent_detected,
                    "resolution_status": resolution_status,
                    "recording_url": recording_url,
                },
            )
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error("Failed to log call: %s", e)
