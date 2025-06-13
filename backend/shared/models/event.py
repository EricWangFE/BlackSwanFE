"""Event models for black swan detection"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class EventModel(BaseModel):
    """Base event model"""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field(..., description="Event source (twitter, reddit, news, etc)")
    content: Dict[str, Any] = Field(..., description="Raw event content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ProcessedEvent(EventModel):
    """Event with processing metadata"""
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    entities: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    language: str = Field(default="en")


class AlertEvent(ProcessedEvent):
    """Event that triggered an alert"""
    alert_id: UUID = Field(default_factory=uuid4)
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    confidence: float = Field(..., ge=0, le=1)
    risk_factors: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    affected_assets: List[str] = Field(default_factory=list)
    
    
class EventFilter(BaseModel):
    """Filter criteria for events"""
    sources: Optional[List[str]] = None
    severity: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assets: Optional[List[str]] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=1)