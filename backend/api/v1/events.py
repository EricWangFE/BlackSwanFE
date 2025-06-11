"""Event API routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime

from shared.models.event import EventModel, ProcessedEvent, EventFilter, AlertEvent
from shared.middleware.auth import AuthMiddleware
from shared.utils.logger import get_logger
from config.redis import stream_manager
from config.settings import settings

logger = get_logger()
router = APIRouter(prefix="/events", tags=["events"])

# Initialize auth
auth = AuthMiddleware(secret_key=settings.jwt_secret_key)


@router.get("/", response_model=List[ProcessedEvent])
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source: Optional[str] = None,
    severity: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_data: dict = Depends(auth.verify_token)
):
    """List events with filtering"""
    try:
        # TODO: Implement database query
        # For now, return mock data
        return [
            ProcessedEvent(
                id="550e8400-e29b-41d4-a716-446655440000",
                source="twitter",
                content={"text": "Major crypto exchange halts withdrawals"},
                sentiment_score=-0.8,
                relevance_score=0.9,
                entities=["Binance", "BTC"],
                topics=["exchange", "liquidity"]
            )
        ]
    except Exception as e:
        logger.error("Failed to fetch events", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch events")


@router.get("/alerts", response_model=List[AlertEvent])
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[List[str]] = Query(None),
    unread_only: bool = Query(False),
    user_data: dict = Depends(auth.verify_token)
):
    """List alert events"""
    try:
        # TODO: Implement database query
        return [
            AlertEvent(
                id="660e8400-e29b-41d4-a716-446655440001",
                source="analysis",
                content={"title": "Critical Market Event Detected"},
                severity="high",
                confidence=0.85,
                risk_factors=["Exchange liquidity", "Market panic"],
                recommended_actions=["Monitor positions", "Consider hedging"],
                affected_assets=["BTC", "ETH"]
            )
        ]
    except Exception as e:
        logger.error("Failed to fetch alerts", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


@router.get("/{event_id}", response_model=ProcessedEvent)
async def get_event(
    event_id: str,
    user_data: dict = Depends(auth.verify_token)
):
    """Get specific event by ID"""
    try:
        # TODO: Implement database query
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        logger.error("Failed to fetch event", error=str(e), event_id=event_id)
        raise HTTPException(status_code=500, detail="Failed to fetch event")


@router.post("/{event_id}/acknowledge")
async def acknowledge_event(
    event_id: str,
    user_data: dict = Depends(auth.verify_token)
):
    """Mark event as acknowledged/read"""
    try:
        # TODO: Update database
        return {"status": "acknowledged", "event_id": event_id}
    except Exception as e:
        logger.error("Failed to acknowledge event", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to acknowledge event")


@router.post("/stream")
async def create_event_stream(
    event: EventModel,
    user_data: dict = Depends(auth.verify_token)
):
    """Create new event in the stream (internal use)"""
    try:
        # Publish to Redis stream
        await stream_manager.publish_event(
            stream_manager.config.event_stream_key,
            event.model_dump()
        )
        return {"status": "published", "event_id": str(event.id)}
    except Exception as e:
        logger.error("Failed to publish event", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to publish event")