import asyncio
import sys
import os

# Add the project root to sys.path to import the backend
sys.path.append(os.getcwd())

from backend.services.ai_service import ai_service

async def test_queries():
    test_cases = [
        # Causes
        ("why diabetes happen", "Diabetes may happen due to genetics"),
        ("why diabetes came for me", "Diabetes may happen due to genetics"),
        ("how i got diabetes", "Diabetes may happen due to genetics"),
        ("what made me diabetic", "Diabetes may happen due to genetics"),
        ("why this sugar problem came", "Diabetes may happen due to genetics"),
        
        # Symptoms
        ("how know diabetes", "Common symptoms include thirst"),
        ("signs of sugar problem", "Common symptoms include thirst"),
        ("how diabetes symptoms look", "Common symptoms include thirst"),
        
        # Low Sugar
        ("how i can face low sugar", "Mild low sugar is often treated"),
        ("what to do if sugar drops", "Mild low sugar is often treated"),
        ("low sugar solution", "Mild low sugar is often treated"),
        
        # Diet
        ("what should i eat", "A healthy diabetic diet focuses"),
        ("best food for sugar patient", "A healthy diabetic diet focuses"),
        ("food for sugar control", "A healthy diabetic diet focuses"),
        
        # Hydration
        ("how much water take", "Staying hydrated is crucial"),
        ("water needed for sugar", "Staying hydrated is crucial"),
        ("should i drink more water", "Staying hydrated is crucial")
    ]
    
    print("-" * 80)
    print(f"{'QUERY':<35} | {'MATCHED?':<10} | {'RESPONSE PREVIEW'}")
    print("-" * 80)
    
    passed = 0
    for q, expected_snippet in test_cases:
        response = await ai_service.get_response(q)
        is_match = expected_snippet.lower() in response.lower()
        if is_match: passed += 1
        
        print(f"{q:<35} | {'YES' if is_match else 'NO':<10} | {response[:40]}...")
    
    print("-" * 80)
    print(f"TOTAL PASSED: {passed}/{len(test_cases)}")
    print("-" * 80)

if __name__ == "__main__":
    asyncio.run(test_queries())
