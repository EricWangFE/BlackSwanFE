"""Celery configuration for async task processing"""

import os
from celery import Celery
from kombu import Exchange, Queue

# Redis URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create Celery instance
celery_app = Celery(
    "blackswan",
    broker=f"{REDIS_URL}/0",
    backend=f"{REDIS_URL}/1",
    include=[
        "services.ingestion_service.tasks",
        "services.sentiment_service.tasks",
        "services.alert_service.tasks",
        "services.trading_service.tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Performance settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Task routing
    task_routes={
        "ingestion.*": {"queue": "ingestion"},
        "sentiment.*": {"queue": "sentiment"},
        "alerts.*": {"queue": "alerts"},
        "trading.*": {"queue": "trading"},
        "analysis.*": {"queue": "analysis"}
    },
    
    # Queue configuration
    task_queues=(
        Queue("ingestion", Exchange("ingestion"), routing_key="ingestion.*"),
        Queue("sentiment", Exchange("sentiment"), routing_key="sentiment.*"),
        Queue("alerts", Exchange("alerts"), routing_key="alerts.*"),
        Queue("trading", Exchange("trading"), routing_key="trading.*"),
        Queue("analysis", Exchange("analysis"), routing_key="analysis.*"),
    ),
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "check-market-health": {
            "task": "services.ingestion_service.tasks.check_market_health",
            "schedule": 60.0,  # Every minute
        },
        "cleanup-old-events": {
            "task": "services.ingestion_service.tasks.cleanup_old_events",
            "schedule": 3600.0,  # Every hour
        },
        "generate-daily-report": {
            "task": "services.alert_service.tasks.generate_daily_report",
            "schedule": 86400.0,  # Daily
        }
    }
)


# Task decorators
def background_task(name=None, queue="default", max_retries=3):
    """Decorator for background tasks"""
    def decorator(func):
        return celery_app.task(
            name=name or func.__name__,
            queue=queue,
            max_retries=max_retries,
            bind=True
        )(func)
    return decorator


# Example task
@celery_app.task(bind=True, name="test.ping")
def ping(self):
    """Test task to verify Celery is working"""
    return "pong"