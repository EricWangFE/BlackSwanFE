// edge-functions/alert-aggregator.ts
import { Redis } from '@vercel/kv';

export const config = {
  runtime: 'edge',
};

interface AlertMetrics {
  total: number;
  critical: number;
  byAsset: Record<string, number>;
  sentiment: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

export default async function handler(request: Request) {
  const redis = new Redis({
    url: process.env.KV_REST_API_URL!,
    token: process.env.KV_REST_API_TOKEN!,
  });

  // Aggregate alerts from last hour
  const hourAgo = Date.now() - 3600000;
  const alerts = await redis.zrangebyscore(
    'alerts:timeline',
    hourAgo,
    '+inf',
    'WITHSCORES'
  );

  const metrics: AlertMetrics = {
    total: 0,
    critical: 0,
    byAsset: {},
    sentiment: { positive: 0, negative: 0, neutral: 0 },
  };

  // Process alerts in edge function for low latency
  for (let i = 0; i < alerts.length; i += 2) {
    const alert = JSON.parse(alerts[i] as string);
    metrics.total++;
    
    if (alert.level === 'critical') metrics.critical++;
    
    metrics.byAsset[alert.asset] = (metrics.byAsset[alert.asset] || 0) + 1;
    
    if (alert.sentiment > 0.3) metrics.sentiment.positive++;
    else if (alert.sentiment < -0.3) metrics.sentiment.negative++;
    else metrics.sentiment.neutral++;
  }

  // Cache for 30 seconds
  return new Response(JSON.stringify(metrics), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 's-maxage=30, stale-while-revalidate',
    },
  });
}