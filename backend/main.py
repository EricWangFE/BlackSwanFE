"""Main FastAPI application for Black Swan Event Detection System"""

from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import structlog
from redis import asyncio as aioredis

from services.llm_orchestrator import LLMOrchestrator, EventVectorStore
from shared.models.event import EventModel
from shared.models.analysis import AnalysisResult
from shared.utils.logger import setup_logger
from api.v1 import api_router
from config.settings import settings

# Setup structured logging
logger = setup_logger()

# Global instances
redis_client = None
llm_orchestrator = None
vector_store = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global redis_client, llm_orchestrator, vector_store
    
    # Startup
    logger.info("Starting Black Swan Detection System")
    
    # Initialize Redis (Railway provides REDIS_URL automatically)
    redis_client = await aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )
    
    # Initialize services
    llm_orchestrator = LLMOrchestrator()
    vector_store = EventVectorStore()
    
    logger.info("All services initialized successfully")
    
    yield
    
    # Shutdown
    await redis_client.close()
    logger.info("Shutting down Black Swan Detection System")


# Create FastAPI app
app = FastAPI(
    title="Black Swan Event Detection API",
    description="Real-time crypto market black swan event detection and analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include API routes
app.include_router(api_router)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    try:
        # Check Redis connection
        await redis_client.ping()
        return {"status": "healthy", "service": "black-swan-api"}
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_event(event: EventModel) -> AnalysisResult:
    """Analyze a potential black swan event"""
    try:
        logger.info("Analyzing event", event_id=str(event.id), source=event.source)
        
        # Find similar historical events
        similar_events = await vector_store.find_similar_events(event)
        
        # Get current market data (mock for now)
        market_data = {
            "btc_price": 45000,
            "total_market_cap": 1.7e12,
            "fear_greed_index": 35
        }
        
        # Run LLM analysis
        analysis = await llm_orchestrator.analyze_event(
            event_data=event.model_dump(),
            market_data=market_data,
            similar_events=similar_events
        )
        
        # Store event and analysis for future reference
        await vector_store.store_event(event, analysis.model_dump())
        
        # Publish to Redis stream for real-time subscribers
        await redis_client.xadd(
            "events:analyzed",
            {
                "event_id": str(event.id),
                "severity": analysis.severity,
                "confidence": str(analysis.confidence_score)
            }
        )
        
        logger.info(
            "Event analysis complete",
            event_id=str(event.id),
            severity=analysis.severity,
            confidence=analysis.confidence_score
        )
        
        return analysis
        
    except Exception as e:
        logger.error("Analysis failed", error=str(e), event_id=str(event.id))
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.get("/api/v1/events/similar/{event_id}")
async def get_similar_events(event_id: str, limit: int = 10):
    """Get similar historical events"""
    try:
        # This would fetch the event from database
        # For now, returning mock response
        return {
            "event_id": event_id,
            "similar_events": [],
            "message": "Feature under development"
        }
    except Exception as e:
        logger.error("Failed to fetch similar events", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch similar events")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development",
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
        }
    )