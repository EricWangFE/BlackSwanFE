# services/llm_orchestrator/vector_store.py
import os
import hashlib
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone

import pinecone
import numpy as np
from sentence_transformers import SentenceTransformer
from tenacity import retry, stop_after_attempt

from shared.models.event import EventModel

class EventVectorStore:
    """Pinecone-based vector store for event similarity search"""
    
    def __init__(self, index_name: str = "blackswan-events"):
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENV")
        )
        
        self.index_name = index_name
        self.index = pinecone.Index(index_name)
        
        # Use financial-domain embeddings
        self.encoder = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.embedding_dim = 768
        
        # Create index if doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=self.embedding_dim,
                metric="cosine",
                pods=1,
                replicas=1,
                pod_type="p1.x1"
            )
    
    @retry(stop=stop_after_attempt(3))
    async def store_event(self, event: EventModel, analysis: Dict):
        """Store event with embeddings and metadata"""
        
        # Create text representation for embedding
        text_repr = self._create_text_representation(event, analysis)
        
        # Generate embedding
        embedding = self.encoder.encode(text_repr).tolist()
        
        # Prepare metadata
        metadata = {
            "event_id": str(event.id),
            "source": event.source,
            "timestamp": event.timestamp.isoformat(),
            "confidence_score": analysis.get("confidence_score", 0),
            "severity": analysis.get("severity", "low"),
            "asset": self._extract_asset(event),
            "sentiment": analysis.get("sentiment_score", 0)
        }
        
        # Upsert to Pinecone
        self.index.upsert(
            vectors=[(str(event.id), embedding, metadata)],
            namespace="events"
        )
    
    async def find_similar_events(
        self, 
        event: EventModel,
        k: int = 10,
        time_window_days: Optional[int] = 90
    ) -> List[Dict]:
        """Find similar historical events"""
        
        # Generate query embedding
        text_repr = self._create_text_representation(event, {})
        query_embedding = self.encoder.encode(text_repr).tolist()
        
        # Build filter
        filter_dict = {}
        if time_window_days:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=time_window_days)).isoformat()
            filter_dict["timestamp"] = {"$gte": cutoff}
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True,
            namespace="events",
            filter=filter_dict if filter_dict else None
        )
        
        # Format results
        similar_events = []
        for match in results.matches:
            similar_events.append({
                "event_id": match.metadata.get("event_id"),
                "similarity_score": match.score,
                "timestamp": match.metadata.get("timestamp"),
                "severity": match.metadata.get("severity"),
                "confidence_score": match.metadata.get("confidence_score"),
                "source": match.metadata.get("source")
            })
        
        return similar_events
    
    def _create_text_representation(self, event: EventModel, analysis: Dict) -> str:
        """Create rich text representation for embedding"""
        parts = [
            f"Source: {event.source}",
            f"Content: {event.content.get('title', '')} {event.content.get('text', '')}",
        ]
        
        if analysis:
            parts.extend([
                f"Severity: {analysis.get('severity', 'unknown')}",
                f"Risk factors: {' '.join(analysis.get('risk_factors', []))}"
            ])
        
        return " ".join(parts)
    
    def _extract_asset(self, event: EventModel) -> str:
        """Extract crypto asset from event content"""
        # Simple extraction - in production use NER
        content_text = f"{event.content.get('title', '')} {event.content.get('text', '')}"
        
        common_assets = ['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC', 'DOT']
        for asset in common_assets:
            if asset.lower() in content_text.lower():
                return asset
        
        return "UNKNOWN"