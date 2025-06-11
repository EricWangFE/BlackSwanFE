"""Analysis result models"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import UUID


class RiskAssessment(BaseModel):
    """Risk assessment details"""
    category: str = Field(..., description="Risk category")
    probability: float = Field(..., ge=0, le=1)
    impact: float = Field(..., ge=0, le=1)
    description: str
    mitigation: Optional[str] = None


class AnalysisResult(BaseModel):
    """Complete analysis result from LLM orchestrator"""
    event_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: float = Field(..., ge=0, le=1)
    confidence_variance: float = Field(default=0.0, ge=0)
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    risk_factors: List[str] = Field(default_factory=list)
    reasoning: Dict[str, any] = Field(default_factory=dict)
    recommended_actions: List[str] = Field(default_factory=list)
    requires_human_review: bool = Field(default=False)
    
    # Additional analysis metadata
    sentiment_analysis: Optional[Dict[str, any]] = None
    market_impact: Optional[Dict[str, any]] = None
    historical_similarity: Optional[Dict[str, any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketContext(BaseModel):
    """Market context for analysis"""
    btc_price: float
    eth_price: Optional[float] = None
    total_market_cap: float
    btc_dominance: Optional[float] = None
    fear_greed_index: Optional[int] = Field(None, ge=0, le=100)
    volume_24h: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnalysisRequest(BaseModel):
    """Request for event analysis"""
    event: Dict[str, any]
    market_context: Optional[MarketContext] = None
    include_historical: bool = Field(default=True)
    max_similar_events: int = Field(default=10, ge=1, le=50)
    urgency: str = Field(default="normal", regex="^(low|normal|high|critical)$")