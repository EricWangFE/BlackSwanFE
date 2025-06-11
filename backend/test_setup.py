#!/usr/bin/env python3
"""Test basic setup and imports"""

import sys
import asyncio

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        # FastAPI
        from fastapi import FastAPI
        print("✓ FastAPI")
        
        # Main app
        from main import app
        print("✓ Main app")
        
        # Config
        from config.settings import settings
        print("✓ Settings")
        
        # Models
        from shared.models.event import EventModel
        from shared.models.analysis import AnalysisResult
        print("✓ Models")
        
        # Services
        from services.llm_orchestrator import LLMOrchestrator
        print("✓ LLM Orchestrator")
        
        # API routes
        from api.v1 import api_router
        print("✓ API routes")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from config.settings import settings
        
        print(f"✓ Port: {settings.port}")
        print(f"✓ Environment: {settings.environment}")
        print(f"✓ Redis URL: {settings.redis_url}")
        print(f"✓ JWT configured: {'jwt_secret_key' in settings.__dict__}")
        
        # Check for required API keys
        missing = []
        if not settings.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not settings.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not settings.pinecone_api_key:
            missing.append("PINECONE_API_KEY")
            
        if missing:
            print(f"\n⚠️  Missing API keys: {', '.join(missing)}")
            print("  Add these to your .env file for full functionality")
        else:
            print("\n✅ All API keys configured!")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Config error: {e}")
        return False

async def test_api():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✓ Health endpoint")
        else:
            print(f"✗ Health endpoint: {response.status_code}")
            
        # Test auth endpoint
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User"
        })
        if response.status_code == 200:
            print("✓ Auth endpoint")
        else:
            print(f"✗ Auth endpoint: {response.status_code}")
            
        print("\n✅ API tests complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ API test error: {e}")
        return False

if __name__ == "__main__":
    print("Black Swan Backend Setup Test\n" + "="*40)
    
    # Run tests
    imports_ok = test_imports()
    config_ok = test_config()
    
    if imports_ok and config_ok:
        # Run async API tests
        asyncio.run(test_api())
        
        print("\n" + "="*40)
        print("✅ Setup looks good!")
        print("\nNext steps:")
        print("1. Add your API keys to .env")
        print("2. Run: python -m uvicorn main:app --reload")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("\n" + "="*40)
        print("❌ Setup issues detected. Check errors above.")
        sys.exit(1)