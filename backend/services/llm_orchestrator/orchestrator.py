# services/llm_orchestrator/orchestrator.py
import asyncio
import json
import os
from typing import Dict, List
from datetime import datetime, timezone

from anthropic import AsyncAnthropic
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
import numpy as np
from prometheus_client import Counter, Histogram

from shared.models.analysis import AnalysisResult
from shared.utils.cache import TTLCache
from shared.utils.logger import get_logger

logger = get_logger()

# Metrics
llm_calls = Counter('llm_calls_total', 'Total LLM API calls', ['model', 'status'])
llm_latency = Histogram('llm_latency_seconds', 'LLM response time', ['model'])
consensus_scores = Histogram('llm_consensus_scores', 'Agreement between models')

class LLMOrchestrator:
    """Multi-agent LLM orchestration with chain-of-thought reasoning"""
    
    def __init__(self):
        self.claude = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cache = TTLCache(ttl_seconds=3600)  # 1 hour cache
        
        # Model configurations for different analysis types
        self.model_configs = {
            "primary_analysis": {
                "model": "claude-3-opus-20240229",
                "temperature": 0.3,
                "max_tokens": 1000
            },
            "verification": {
                "model": "gpt-4-0125-preview", 
                "temperature": 0.1,
                "max_tokens": 500
            },
            "sentiment_deep": {
                "model": "claude-3-opus-20240229",
                "temperature": 0.5,
                "max_tokens": 800
            }
        }
    
    async def analyze_event(
        self, 
        event_data: Dict,
        market_data: Dict,
        similar_events: List[Dict]
    ) -> AnalysisResult:
        """Orchestrate multi-agent analysis of potential black swan event"""
        
        # Check cache first
        cache_key = self._generate_cache_key(event_data, market_data)
        cached = self.cache.get(cache_key)
        if cached:
            return AnalysisResult.model_validate(cached)
        
        # Run parallel analysis with different agents
        tasks = [
            self._primary_analysis(event_data, market_data),
            self._sentiment_analysis(event_data),
            self._historical_comparison(event_data, similar_events),
            self._market_impact_analysis(market_data)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle failures gracefully
        valid_results = [r for r in results if not isinstance(r, Exception)]
        if len(valid_results) < 2:
            logger.error("Insufficient LLM responses", failures=len(results) - len(valid_results))
            raise Exception("Multi-agent analysis failed")
        
        # Synthesize results
        final_analysis = await self._synthesize_results(valid_results, event_data)
        
        # Cache result
        self.cache.set(cache_key, final_analysis.model_dump())
        
        return final_analysis
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _primary_analysis(
        self, 
        event_data: Dict, 
        market_data: Dict
    ) -> Dict:
        """Primary analysis using Claude Opus with chain-of-thought"""
        
        prompt = f"""You are a senior crypto risk analyst examining a potential black swan event.
        
CONTEXT:
- Current UTC time: {datetime.now(timezone.utc).isoformat()}
- Event source: {event_data.get('source')}
- Market conditions: {json.dumps(market_data, indent=2)}

EVENT DATA:
{json.dumps(event_data, indent=2)}

Perform a step-by-step analysis:

1. PATTERN RECOGNITION: Identify any patterns similar to previous crypto black swans (Terra/Luna, FTX, Mt. Gox, etc.)

2. SENTIMENT ANALYSIS: Evaluate the sentiment severity and velocity of change

3. MARKET CORRELATION: Assess how this event correlates with current market movements

4. RISK FACTORS: List specific risk factors that make this event notable

5. CONFIDENCE ASSESSMENT: Provide a confidence score (0-1) that this represents a genuine black swan

6. RECOMMENDED ACTIONS: Suggest specific portfolio protection strategies

Think through this systematically. Show your reasoning at each step.

Output as JSON with these fields:
- reasoning: Your step-by-step analysis
- risk_factors: List of identified risks
- confidence_score: 0-1 float
- severity: "low", "medium", "high", "critical"
- recommended_actions: List of specific actions
- similar_events: Historical parallels if any
"""
        
        with llm_latency.labels(model="claude-opus").time():
            response = await self.claude.messages.create(
                model=self.model_configs["primary_analysis"]["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.model_configs["primary_analysis"]["temperature"],
                max_tokens=self.model_configs["primary_analysis"]["max_tokens"]
            )
        
        llm_calls.labels(model="claude-opus", status="success").inc()
        
        try:
            # Extract JSON from response
            content = response.content[0].text
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            return json.loads(content[json_start:json_end])
        except Exception as e:
            logger.error("Failed to parse LLM response", error=str(e))
            llm_calls.labels(model="claude-opus", status="parse_error").inc()
            raise
    
    async def _synthesize_results(
        self, 
        results: List[Dict], 
        event_data: Dict
    ) -> AnalysisResult:
        """Synthesize multiple agent outputs into final assessment"""
        
        # Calculate consensus metrics
        confidence_scores = [r.get('confidence_score', 0) for r in results]
        mean_confidence = np.mean(confidence_scores)
        confidence_std = np.std(confidence_scores)
        
        consensus_scores.observe(1 - confidence_std)  # Higher score = more agreement
        
        # Aggregate risk factors
        all_risk_factors = []
        for r in results:
            all_risk_factors.extend(r.get('risk_factors', []))
        
        # Determine final severity based on consensus
        severities = [r.get('severity', 'low') for r in results]
        severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        avg_severity = np.mean([severity_map.get(s, 1) for s in severities])
        
        final_severity = 'low'
        if avg_severity >= 3.5:
            final_severity = 'critical'
        elif avg_severity >= 2.5:
            final_severity = 'high'
        elif avg_severity >= 1.5:
            final_severity = 'medium'
        
        # Create structured result
        return AnalysisResult(
            event_id=event_data.get('id'),
            timestamp=datetime.now(timezone.utc),
            confidence_score=float(mean_confidence),
            confidence_variance=float(confidence_std),
            severity=final_severity,
            risk_factors=list(set(all_risk_factors)),  # Deduplicate
            reasoning={
                'agent_count': len(results),
                'consensus_level': 'high' if confidence_std < 0.1 else 'medium' if confidence_std < 0.2 else 'low',
                'primary_analysis': results[0] if results else {}
            },
            recommended_actions=self._aggregate_recommendations(results),
            requires_human_review=confidence_std > 0.3 or mean_confidence < 0.5
        )
    
    def _aggregate_recommendations(self, results: List[Dict]) -> List[str]:
        """Aggregate and prioritize recommendations from multiple agents"""
        all_actions = []
        for r in results:
            all_actions.extend(r.get('recommended_actions', []))
        
        # Count frequency and prioritize
        action_counts = {}
        for action in all_actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Return actions mentioned by multiple agents first
        sorted_actions = sorted(
            action_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [action for action, count in sorted_actions[:5]]  # Top 5
    
    def _generate_cache_key(self, event_data: Dict, market_data: Dict) -> str:
        """Generate cache key from event and market data"""
        key_data = {
            'event_id': event_data.get('id'),
            'source': event_data.get('source'),
            'market_snapshot': {
                'btc_price': market_data.get('btc_price'),
                'total_market_cap': market_data.get('total_market_cap')
            }
        }
        return json.dumps(key_data, sort_keys=True)
    
    async def _sentiment_analysis(self, event_data: Dict) -> Dict:
        """Deep sentiment analysis using Claude"""
        prompt = f"""Analyze the sentiment and emotional impact of this crypto event:

EVENT: {json.dumps(event_data, indent=2)}

Consider:
1. Sentiment velocity (how fast is sentiment changing?)
2. Sentiment magnitude (how extreme is the sentiment?)
3. Community panic indicators
4. FUD (Fear, Uncertainty, Doubt) levels
5. Social media virality potential

Output as JSON with fields:
- sentiment_score: -1 to 1 (negative to positive)
- velocity: "slow", "moderate", "rapid", "explosive"
- panic_level: 0-10
- virality_score: 0-1
- key_emotions: List of dominant emotions
- risk_factors: Sentiment-based risks
"""
        
        response = await self.claude.messages.create(
            model=self.model_configs["sentiment_deep"]["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=self.model_configs["sentiment_deep"]["temperature"],
            max_tokens=self.model_configs["sentiment_deep"]["max_tokens"]
        )
        
        content = response.content[0].text
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        return json.loads(content[json_start:json_end])
    
    async def _historical_comparison(self, event_data: Dict, similar_events: List[Dict]) -> Dict:
        """Compare with historical black swan events"""
        prompt = f"""Compare this event with historical crypto black swans:

CURRENT EVENT: {json.dumps(event_data, indent=2)}

SIMILAR HISTORICAL EVENTS: {json.dumps(similar_events[:5], indent=2)}

Analyze:
1. Pattern similarity scores
2. Market conditions comparison
3. Outcome predictions based on history
4. Key differences that might change outcomes

Output as JSON:
- similarity_scores: Dict of event_id to similarity score (0-1)
- most_similar_event: Event ID of closest match
- predicted_impact: Based on historical patterns
- risk_factors: Unique risks not seen before
- confidence_score: 0-1
"""
        
        response = await self.openai.chat.completions.create(
            model=self.model_configs["verification"]["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=self.model_configs["verification"]["temperature"],
            max_tokens=self.model_configs["verification"]["max_tokens"]
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _market_impact_analysis(self, market_data: Dict) -> Dict:
        """Analyze potential market impact"""
        prompt = f"""Analyze market vulnerability to black swan events:

MARKET DATA: {json.dumps(market_data, indent=2)}

Assess:
1. Market liquidity conditions
2. Leverage indicators
3. Correlation breakdown risks
4. Cascade failure potential
5. Key support levels at risk

Output as JSON:
- liquidity_risk: "low", "medium", "high", "critical"
- leverage_concern: 0-10
- cascade_probability: 0-1
- support_levels: List of price levels
- risk_factors: Market structure risks
- recommended_actions: Protective measures
"""
        
        response = await self.openai.chat.completions.create(
            model=self.model_configs["verification"]["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=self.model_configs["verification"]["temperature"],
            max_tokens=self.model_configs["verification"]["max_tokens"]
        )
        
        return json.loads(response.choices[0].message.content)