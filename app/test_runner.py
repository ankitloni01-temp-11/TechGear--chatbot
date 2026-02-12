import pytest
import os
import httpx
import asyncio
from app.testing_agent import EvaluatorAgent

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_chatbot_scenarios():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.fail("GEMINI_API_KEY is not set in the environment. Please check your GitHub Secrets.")
        
    tester = EvaluatorAgent()
    scenarios = tester.get_test_scenarios()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for scenario in scenarios:
            print(f"\nRunning Scenario: {scenario['name']}")
            
            # 1. Get Chatbot Response
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json={"message": scenario["query"]}
            )
            assert response.status_code == 200
            data = response.json()
            chatbot_response = data["response"]
            category = data["category"]
            
            # 2. Verify Intent/Category
            assert category == scenario["expected_intent"]
            
            # 3. LLM-Based Evaluation
            evaluation = await tester.evaluate_response(
                query=scenario["query"],
                response=chatbot_response
            )
            
            print(f"Score: {evaluation['score']}/5")
            print(f"Passed: {evaluation['passed']}")
            print(f"Reasons: {', '.join(evaluation['reasons'])}")
            
            assert evaluation["passed"] is True, f"LLM evaluation failed for: {scenario['name']}"

if __name__ == "__main__":
    # This allows running the tests directly with python if needed
    asyncio.run(test_chatbot_scenarios())
