from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import current_time, use_llm
import logging
import os

from ...config.settings import settings
from ..orchestrator_agent.orchestrator_system_prompt import ORCHESTRATOR_SYSTEM_PROMPT
from ..scheduler_agent.scheduler_agent import scheduler_assistant
from ..ticketing_agent.ticketing_agent import ticketing_assistant
from .tools.knowledge_base_tools import knowledge_base_search
from .tools.message_tools import send_message

logger = logging.getLogger(__name__)

class MemoryAwareOrchestratorAgent:
    """Orchestrator agent with Mem0 memory capabilities using Strands."""
    
    def __init__(self):
        model = BedrockModel(
            model_id=settings.BEDROCK_MODEL_ID,
            boto_session=settings.SESSION,
        )
        
        # Initialize Mem0 client
        self.memory_client = None
        try:
            # Use local Mem0 with Bedrock configuration
            import os
            from mem0 import Memory
            from mem0.configs.base import MemoryConfig
            
            # Set AWS credentials as environment variables for Mem0
            os.environ["AWS_ACCESS_KEY_ID"] = settings.AWS_ACCESS_KEY_ID or ""
            os.environ["AWS_SECRET_ACCESS_KEY"] = settings.AWS_SECRET_ACCESS_KEY or ""
            os.environ["AWS_DEFAULT_REGION"] = settings.AWS_REGION or "us-east-1"
            
            config_dict = settings.get_mem0_config()
            config = MemoryConfig(**config_dict)
            self.memory_client = Memory(config=config)
            logger.info("Successfully initialized Mem0 local client with AWS Bedrock configuration")
                
        except Exception as e:
            logger.error(f"Failed to initialize Mem0: {e}")
            logger.info("Continuing without memory system - memory tools will return appropriate messages")
            self.memory_client = None

        
        # Create custom memory tools that use the Mem0 client
        @tool
        def get_user_memories(user_id: str, query: str = "") -> str:
            """Retrieve relevant memories for a user. Use empty query to get all memories."""
            if self.memory_client is None:
                return "Memory system is not available. Please configure Mem0 properly."
            
            try:
                if query:
                    # Search for specific query
                    result = self.memory_client.search(query=query, user_id=user_id)
                else:
                    # Get all memories for user
                    result = self.memory_client.get_all(user_id=user_id)
                
                # Extract results from the dictionary
                memories = result.get('results', []) if isinstance(result, dict) else result
                
                if memories and len(memories) > 0:
                    memory_texts = []
                    for memory_item in memories[:5]:  # Limit to 5 memories
                        if isinstance(memory_item, dict):
                            memory_text = memory_item.get('memory', memory_item.get('text', str(memory_item)))
                        else:
                            memory_text = str(memory_item)
                        memory_texts.append(memory_text)
                    return f"Found {len(memories)} memories:\n" + "\n".join(memory_texts)
                else:
                    return "No memories found for this user."
                    
            except Exception as e:
                logger.error(f"Error retrieving memories: {e}")
                return f"Error retrieving memories: {str(e)}"

        @tool  
        def store_user_memory(user_id: str, content: str) -> str:
            """Store important information about a user."""
            if self.memory_client is None:
                return "Memory system is not available. Please configure Mem0 properly."
            
            try:
                messages = [{"role": "user", "content": content}]
                result = self.memory_client.add(messages=messages, user_id=user_id)
                
                # Check if memory was stored successfully
                if isinstance(result, dict) and 'results' in result:
                    return f"Successfully stored memory for user {user_id}: {content[:100]}{'...' if len(content) > 100 else ''}"
                else:
                    return f"Memory storage completed for user {user_id}: {content[:100]}{'...' if len(content) > 100 else ''}"
                    
            except Exception as e:
                logger.error(f"Error storing memory: {e}")
                return f"Error storing memory: {str(e)}"
            

        self.agent = Agent(
            model=model,
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=[
                current_time,
                get_user_memories,
                store_user_memory,
                send_message,
                knowledge_base_search,
                scheduler_assistant,
                ticketing_assistant
            ]
        )
    
    async def process_message(self, message: str, chat_id: str) -> str:
        """Process message with automatic memory integration."""
        
        # Enhanced message with user_id for memory operations
        enhanced_message = f"""
USER_ID: {chat_id}
MESSAGE: {message}

Instructions:
1. Use get_user_memories(user_id="{chat_id}", query="") to retrieve context
2. Process the message with memory context
3. Route to specialist agents if needed, passing memory context
4. Store important new information using store_user_memory(user_id="{chat_id}", content="...")
5. Provide personalized response based on memory context
"""
        
        try:
            result = await self.agent.invoke_async(enhanced_message)
            response = str(result)
            logger.info(f"Processed message for chat_id {chat_id}")
            return response
        except Exception as e:
            logger.error(f"Error processing message for chat_id {chat_id}: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    

# Create global instance
memory_orchestrator = MemoryAwareOrchestratorAgent()


