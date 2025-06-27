#!/usr/bin/env python3
"""
Test client for the GenAI Email Processing System.
"""

import asyncio
import json
import time
import httpx
from typing import Dict, Any


class EmailProcessorClient:
    """Client for testing the email processing API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = await self.client.get(f"{self.base_url}/health")
        return response.json()
    
    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single email."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/emails/process",
            json=email_data
        )
        response.raise_for_status()
        return response.json()
    
    async def classify_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify an email."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/emails/classify",
            json=email_data
        )
        response.raise_for_status()
        return response.json()
    
    async def search_emails(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search emails."""
        search_data = {"query": query, "limit": limit}
        response = await self.client.post(
            f"{self.base_url}/api/v1/search/",
            json=search_data
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()


async def test_email_processing():
    """Test email processing functionality."""
    client = EmailProcessorClient()
    
    try:
        # Health check
        print("1. Checking API health...")
        health = await client.health_check()
        print(f"   Status: {health.get('status')}")
        
        # Test email data
        test_email = {
            "subject": "URGENT: System Not Working",
            "body": "Our production system has crashed and is completely down. We need immediate assistance to resolve this critical issue. This is affecting all our customers.",
            "sender": "admin@testcompany.com",
            "attachments": ["error_log.txt"],
            "metadata": {"priority": "high", "source": "support_portal"}
        }
        
        print("\n2. Processing test email...")
        start_time = time.time()
        result = await client.process_email(test_email)
        processing_time = time.time() - start_time
        
        print(f"   Processing time: {processing_time:.2f} seconds")
        print(f"   Email ID: {result.get('email_id')}")
        print(f"   Category: {result.get('classification', {}).get('category')}")
        print(f"   Priority: {result.get('classification', {}).get('priority')}")
        print(f"   Sentiment: {result.get('classification', {}).get('sentiment')}")
        print(f"   Response tone: {result.get('response', {}).get('tone')}")
        
        # Test classification only
        print("\n3. Testing classification only...")
        classification = await client.classify_email(test_email)
        print(f"   Category: {classification.get('category')}")
        print(f"   Confidence: {classification.get('confidence')}")
        print(f"   Keywords: {classification.get('keywords')}")
        
        # Test search (might not work if no emails are indexed yet)
        print("\n4. Testing search...")
        try:
            search_results = await client.search_emails("system down", limit=5)
            print(f"   Found {len(search_results.get('results', []))} results")
        except Exception as e:
            print(f"   Search failed (expected if no emails indexed): {e}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        
    finally:
        await client.close()


async def load_test():
    """Perform a simple load test."""
    client = EmailProcessorClient()
    
    try:
        print("Starting load test with 10 concurrent requests...")
        
        test_email = {
            "subject": "Load Test Email",
            "body": "This is a test email for load testing the system.",
            "sender": "loadtest@example.com"
        }
        
        # Send 10 concurrent requests
        tasks = []
        for i in range(10):
            email_copy = test_email.copy()
            email_copy["subject"] = f"Load Test Email #{i+1}"
            tasks.append(client.process_email(email_copy))
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful
        
        print(f"\nLoad test results:")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Requests per second: {len(results) / total_time:.2f}")
        print(f"   Successful requests: {successful}")
        print(f"   Failed requests: {failed}")
        
        if failed > 0:
            print("\nErrors:")
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"   Request {i+1}: {result}")
        
    except Exception as e:
        print(f"Load test failed: {e}")
        
    finally:
        await client.close()


async def main():
    """Main function."""
    print("GenAI Email Processing System - Test Client")
    print("=" * 50)
    
    # Basic functionality test
    await test_email_processing()
    
    # Load test
    print("\n" + "=" * 50)
    await load_test()


if __name__ == "__main__":
    asyncio.run(main())
