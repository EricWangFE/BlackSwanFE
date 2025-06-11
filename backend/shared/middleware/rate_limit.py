# shared/middleware/rate_limit.py
import time
from typing import Dict, Tuple
from fastapi import HTTPException, Request
from redis import asyncio as aioredis

class RateLimitMiddleware:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.limits = {
            "api": (100, 60),  # 100 requests per 60 seconds
            "llm": (10, 60),   # 10 LLM calls per 60 seconds
            "trading": (5, 60)  # 5 trading actions per 60 seconds
        }
    
    async def check_rate_limit(
        self, 
        request: Request, 
        user_id: str,
        limit_type: str = "api"
    ):
        redis = await aioredis.from_url(self.redis_url)
        
        try:
            limit, window = self.limits.get(limit_type, (100, 60))
            key = f"rate_limit:{limit_type}:{user_id}"
            
            current = await redis.incr(key)
            
            if current == 1:
                await redis.expire(key, window)
            
            if current > limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {window} seconds."
                )
            
            # Add headers
            request.state.rate_limit_remaining = limit - current
            request.state.rate_limit_reset = int(time.time()) + window
            
        finally:
            await redis.close()