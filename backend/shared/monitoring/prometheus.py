# shared/monitoring/prometheus.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Response
import psutil

# Business metrics
alerts_sent = Counter('alerts_sent_total', 'Total alerts sent', ['severity', 'channel'])
analysis_accuracy = Gauge('analysis_accuracy_ratio', 'Current analysis accuracy')
active_users = Gauge('active_users_total', 'Currently active users')
revenue_mrr = Gauge('revenue_mrr_dollars', 'Monthly recurring revenue')

# System metrics
cpu_usage = Gauge('system_cpu_percent', 'CPU usage percentage')
memory_usage = Gauge('system_memory_percent', 'Memory usage percentage')
redis_queue_size = Gauge('redis_queue_size', 'Current Redis queue size', ['queue'])

def setup_monitoring(app: FastAPI):
    """Add Prometheus metrics endpoint"""
    
    @app.get("/metrics")
    async def metrics():
        # Update system metrics
        cpu_usage.set(psutil.cpu_percent())
        memory_usage.set(psutil.virtual_memory().percent)
        
        # Generate Prometheus format
        return Response(
            content=generate_latest(),
            media_type="text/plain"
        )