import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from app.prompt_loader import load_prompt
from langchain_core.output_parsers import JsonOutputParser

class EvaluatorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        self.critic_prompt = load_prompt("critic")
        self.parser = JsonOutputParser()

    async def evaluate_response(self, query: str, response: str, context: str = ""):
        """Evaluates a chatbot response using the Critic LLM."""
        chain = self.critic_prompt | self.llm | self.parser
        evaluation = await chain.ainvoke({
            "query": query,
            "response": response,
            "context": context
        })
        return evaluation

    def get_test_scenarios(self):
        """Returns a list of predefined test scenarios."""
        return [
            {
                "name": "Technical Inquiry - SmartWatch GPS",
                "query": "Does the SmartWatch have GPS?",
                "expected_intent": "technical"
            },
            {
                "name": "Return Policy Inquiry",
                "query": "What is your return policy?",
                "expected_intent": "returns"
            },
            {
                "name": "Greeting / General",
                "query": "Hello, how are you?",
                "expected_intent": "general"
            },
            {
                "name": "Technical - USB-C Power Bank",
                "query": "Which power banks have USB-C?",
                "expected_intent": "technical"
            }
        ]
