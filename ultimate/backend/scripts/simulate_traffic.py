import asyncio
import httpx
import json
import argparse
from datetime import datetime
import time

API_URL = "http://localhost:8000/api/v1/webhooks"

async def simulate_meta_lead(client: httpx.AsyncClient):
    payload = {
        "object": "page",
        "entry": [{
            "id": "1234567890",
            "time": int(time.time()),
            "changes": [{
                "field": "leadgen",
                "value": {
                    "lead_id": f"dummy_lead_{int(time.time())}",
                    "form_id": "987654321",
                    "created_time": int(time.time())
                }
            }]
        }]
    }
    # Provide a mock signature to pass the endpoint verification check
    # Normally this is generated securely via HMAC SHA256 using the App Secret
    headers = {
        "X-Hub-Signature-256": "sha256=mock_signature_for_testing",
        "x-tenant-id": "hq" # Important for the Budget Guard
    }
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Firing Meta Webhook...")
    response = await client.post(f"{API_URL}/meta", json=payload, headers=headers)
    print(f"   => Response: {response.status_code} | {response.text}")

async def simulate_google_lead(client: httpx.AsyncClient):
    payload = {
        "lead_id": f"g_lead_{int(time.time())}",
        "user_column_data": [
            {"column_id": "FULL_NAME", "string_value": "Faher Simulated"},
            {"column_id": "PHONE_NUMBER", "string_value": "+971501112233"}
        ],
        "api_version": "1.0",
        "form_id": 12345
    }
    headers = {"x-tenant-id": "hq"}
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Firing Google Ads Webhook...")
    # Add the query parameter key for verification
    response = await client.post(f"{API_URL}/google?google_key=astroflow_google_secure_key", json=payload, headers=headers)
    print(f"   => Response: {response.status_code} | {response.text}")


async def blast_traffic(burst_count: int = 10):
    async with httpx.AsyncClient() as client:
        print(f"💥 Initiating High-Volume Simulation (Burst: {burst_count} requests)")
        tasks = []
        for _ in range(burst_count):
            tasks.append(simulate_meta_lead(client))
            tasks.append(simulate_google_lead(client))
        await asyncio.gather(*tasks)
        print("💥 Burst Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AstroFlow Traffic Simulator")
    parser.add_argument("--burst", type=int, default=1, help="Number of concurrent webhook sets to fire")
    args = parser.parse_args()
    
    print("==================================================")
    print(" AstroFlow Real-Time Traffic Simulator Active ")
    print("==================================================")
    
    asyncio.run(blast_traffic(burst_count=args.burst))
