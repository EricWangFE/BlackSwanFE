#!/usr/bin/env python3
"""Check all imports and dependencies"""

import sys
import importlib

required_modules = [
    # Core
    'fastapi',
    'uvicorn',
    'pydantic',
    'pydantic_settings',
    
    # Database
    'sqlalchemy',
    'asyncpg',
    'redis',
    
    # AI/ML
    'anthropic',
    'openai',
    'sentence_transformers',
    'pinecone',
    'numpy',
    
    # Auth
    'jwt',
    'passlib',
    'bcrypt',
    
    # Utils
    'structlog',
    'prometheus_client',
    'tenacity',
    'psutil',
    
    # Async
    'celery',
    'httpx',
]

print("Checking required Python modules...")
missing = []

for module in required_modules:
    try:
        if module == 'redis':
            import redis.asyncio
        else:
            importlib.import_module(module)
        print(f"✓ {module}")
    except ImportError:
        print(f"✗ {module} - MISSING")
        missing.append(module)

if missing:
    print(f"\nMissing modules: {', '.join(missing)}")
    print("\nInstall with: pip install " + " ".join(missing))
    sys.exit(1)
else:
    print("\nAll required modules are installed!")

# Now check our app structure
print("\nChecking app imports...")
try:
    # Add current directory to path
    sys.path.insert(0, '.')
    
    # Test imports
    from config.settings import settings
    print("✓ Config settings")
    
    from shared.models.event import EventModel
    print("✓ Shared models")
    
    from shared.utils.logger import get_logger
    print("✓ Logger utils")
    
    from api.v1 import api_router
    print("✓ API routes")
    
    print("\nApp structure looks good!")
    
except Exception as e:
    print(f"\n✗ Import error: {e}")
    sys.exit(1)