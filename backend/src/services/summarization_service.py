from sqlalchemy.orm import Session
from ..database.models import Customer, get_db
from ..config.settings import settings
from strands.models import BedrockModel



class SummarizationService:
    def __init__(self):
        self.model = BedrockModel(
            model_id=settings.BEDROCK_MODEL_ID,
            boto_session=settings.SESSION,
        )

    def summarize_and_update_customer_conversation(self, customer_id: int) -> str:
        db: Session = next(get_db())
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return "Customer not found."

        # Combine existing summary with recent history for a complete picture
        full_history = ""
        if customer.conversation_summary:
            full_history += f"Previous summary:\n{customer.conversation_summary}\n\n"
        if customer.conversation_history:
            full_history += f"Recent conversation:\n{customer.conversation_history}"

        if not full_history.strip():
            return "No conversation history to summarize."

        prompt = f"Update and summarize the following conversation history. Condense it into a concise summary.\n\n{full_history}\n\nUpdated Summary:"

        try:
            summary_response = self.model(prompt)
            new_summary = summary_response.content[0].text.strip()
            
            # Update customer record
            customer.conversation_summary = new_summary
            customer.conversation_history = ""  # Clear the recent history
            db.commit()
            
            return new_summary
        except Exception as e:
            db.rollback()
            return f"Error summarizing conversation: {e}"

summarization_service = SummarizationService()