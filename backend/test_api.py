"""Simple test script to verify API is working"""

import asyncio
import httpx
import json


async def test_api():
    """Test basic API functionality"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        print("Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"Health check: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Health check failed: {e}")
            return
        
        # Test auth endpoints
        print("\nTesting authentication...")
        try:
            # Register
            register_data = {
                "email": "test@example.com",
                "password": "testpassword123",
                "name": "Test User"
            }
            response = await client.post(
                f"{base_url}/api/v1/auth/register",
                json=register_data
            )
            print(f"Registration: {response.status_code}")
            if response.status_code == 200:
                token_data = response.json()
                token = token_data["access_token"]
                print(f"Got token: {token[:20]}...")
                
                # Test authenticated endpoint
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{base_url}/api/v1/auth/me",
                    headers=headers
                )
                print(f"User info: {response.json()}")
                
                # Test events endpoint
                response = await client.get(
                    f"{base_url}/api/v1/events",
                    headers=headers
                )
                print(f"\nEvents: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                
        except Exception as e:
            print(f"Auth test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_api())