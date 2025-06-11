"""Redis configuration for event streaming"""

import os
from typing import Optional
from redis import asyncio as aioredis
from dataclasses import dataclass

@dataclass
class RedisConfig:
    """Redis configuration settings"""
    url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    max_connections: int = 50
    decode_responses: bool = True
    encoding: str = "utf-8"
    
    # Stream settings
    stream_max_len: int = 10000  # Max events per stream
    consumer_group: str = "blackswan-consumers"
    
    # Key prefixes
    event_stream_key: str = "events:raw"
    analyzed_stream_key: str = "events:analyzed"
    alert_stream_key: str = "alerts:dispatch"


class RedisStreamManager:
    """Manages Redis Streams for event processing"""
    
    def __init__(self, config: RedisConfig):
        self.config = config
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Establish Redis connection"""
        self.redis = await aioredis.from_url(
            self.config.url,
            max_connections=self.config.max_connections,
            decode_responses=self.config.decode_responses,
            encoding=self.config.encoding
        )
        
        # Create consumer groups if they don't exist
        await self._create_consumer_groups()
    
    async def _create_consumer_groups(self):
        """Create consumer groups for streams"""
        streams = [
            self.config.event_stream_key,
            self.config.analyzed_stream_key,
            self.config.alert_stream_key
        ]
        
        for stream in streams:
            try:
                await self.redis.xgroup_create(
                    stream, 
                    self.config.consumer_group,
                    id="0",
                    mkstream=True
                )
            except Exception:
                # Group already exists
                pass
    
    async def publish_event(self, stream_key: str, data: dict) -> str:
        """Publish event to stream"""
        event_id = await self.redis.xadd(
            stream_key,
            data,
            maxlen=self.config.stream_max_len,
            approximate=True
        )
        return event_id
    
    async def consume_events(
        self, 
        stream_key: str, 
        consumer_name: str,
        count: int = 10,
        block: int = 1000
    ):
        """Consume events from stream"""
        result = await self.redis.xreadgroup(
            self.config.consumer_group,
            consumer_name,
            {stream_key: ">"},
            count=count,
            block=block
        )
        
        if result:
            stream, messages = result[0]
            return messages
        return []
    
    async def ack_message(self, stream_key: str, message_id: str):
        """Acknowledge message processing"""
        await self.redis.xack(
            stream_key,
            self.config.consumer_group,
            message_id
        )
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()


# Global instance
redis_config = RedisConfig()
stream_manager = RedisStreamManager(redis_config)