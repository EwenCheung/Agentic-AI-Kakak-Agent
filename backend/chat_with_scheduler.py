#!/usr/bin/env python3
"""
Interactive chat interface for the Scheduler Agent
Run this to have a conversation with your AI scheduler assistant.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from src.agent.scheduler_agent.scheduler_agent import scheduler_assistant
        
        print("🤖 Scheduler Agent Chat Interface")
        print("=" * 50)
        print("Connected to your Google Calendar-enabled AI scheduler!")
        print("You can ask me about:")
        print("  • Your calendar events")
        print("  • Availability checking")
        print("  • Scheduling meetings")
        print("  • Finding free time slots")
        print("  • Managing your calendars")
        print("\nType 'quit', 'exit', or 'bye' to end the conversation.")
        print("=" * 50)
        
        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Goodbye! Your scheduler agent is always here when you need it.")
                    break
                
                if not user_input:
                    continue
                
                # Get response from scheduler agent
                print("\n🤖 Scheduler Agent: ", end="", flush=True)
                response = scheduler_assistant(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'quit' to exit.")
                
    except ImportError as e:
        print(f"❌ Failed to import scheduler agent: {e}")
        print("Make sure you're running this from the backend directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
