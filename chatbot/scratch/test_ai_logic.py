import asyncio
import sys
import os

# Add the project root to sys.path to import the backend
sys.path.append(os.getcwd())

from backend.services.ai_service import ai_service

async def test_queries():
    queries = [
        "why diabetes happen",
        "can thin people get diabetes",
        "is coffee safe for diabetics",
        "why am i always thirsty",
        "is diabetes permanent",
        "can children get diabetes",
        "what age can diabetes start"
    ]
    
    print("-" * 50)
    for q in queries:
        response = await ai_service.get_response(q)
        print(f"Q: {q}")
        print(f"A: {response}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_queries())
