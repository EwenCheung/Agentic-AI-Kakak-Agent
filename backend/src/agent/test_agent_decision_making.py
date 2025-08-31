# cd /Users/ewencheung/Documents/GitHub/Agentic-AI-Kakak-Agent/backend
# python3 -m src.agent.test_agent_decision_making

import sys
sys.path.append('.')

from src.agent.orchestrator_agent.orchestrator_agent import orchestrator_assistant

def test_orchestrator_decision_making():
    """Tests the orchestrator's decision-making process."""

    # Test case 1: Scheduling a meeting
    user_query_1 = "I want to book a meeting for tomorrow at 10am."
    response_1 = orchestrator_assistant(
        query=user_query_1,
        company_name="Test Company",
        tone_and_manner="professional",
        phone_number="1234567890"
    )
    print(f"Query: {user_query_1}\nResponse: {response_1}\n")
    # In a real test, we would mock the sub-agents and assert that the scheduler_assistant is called.

    # Test case 2: Creating a ticket
    user_query_2 = "I'm having trouble with my account."
    response_2 = orchestrator_assistant(
        query=user_query_2,
        company_name="Test Company",
        tone_and_manner="professional",
        phone_number="1234567890"
    )
    print(f"Query: {user_query_2}\nResponse: {response_2}\n")
    # In a real test, we would mock the sub-agents and assert that the ticketing_assistant is called.

    # Test case 3: Asking a general question
    user_query_3 = "What is your return policy?"
    response_3 = orchestrator_assistant(
        query=user_query_3,
        company_name="Test Company",
        tone_and_manner="professional",
        phone_number="1234567890"
    )
    print(f"Query: {user_query_3}\nResponse: {response_3}\n")
    # In a real test, we would mock the sub-agents and assert that the chat_assistant is called.

if __name__ == "__main__":
    test_orchestrator_decision_making()