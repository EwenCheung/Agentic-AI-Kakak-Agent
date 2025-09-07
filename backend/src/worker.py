import asyncio
import json
from datetime import datetime

from sqlalchemy.orm import Session

from .database.models import get_db, IncomingMessage, Customer
from .agent.orchestrator_agent.orchestrator_agent import memory_orchestrator

async def process_message(db: Session, message: IncomingMessage):
    """The core logic to process a single message from the queue."""
    print(f"Processing message id: {message.id}")
    
    payload = json.loads(message.payload)
    
    if "message" not in payload or "text" not in payload["message"]:
        print(f"Message {message.id} is not a text message, skipping.")
        return

    tg_message = payload["message"]
    chat_id = tg_message["chat"]["id"]
    text = tg_message["text"]
    first_name = tg_message["from"].get("first_name", "User")
    message_time = datetime.fromtimestamp(tg_message["date"]).strftime('%Y-%m-%d %H:%M:%S')

    # 1. Get or create customer
    customer = db.query(Customer).filter(Customer.telegram_chat_id == str(chat_id)).first()
    if not customer:
        customer = Customer(telegram_chat_id=str(chat_id), name=first_name)
        db.add(customer)
        db.commit()
        db.refresh(customer)

    # 2. Log message to conversation_history for business audit trail
    new_history_entry = f"[{first_name} at {message_time}]: {text}\n"
    if customer.conversation_history:
        customer.conversation_history += new_history_entry
    else:
        customer.conversation_history = new_history_entry
    db.commit()

    # 3. Process message with memory-aware orchestrator (Mem0 for AI intelligence)
    # Using chat_id as user_id for memory isolation
    orchestrator_query = f"""A new message has been received from a customer.

## Customer Details:
- Name: {customer.name}
- Telegram Chat ID: {customer.telegram_chat_id}
- Message: [{first_name} at {message_time}]: {text}

Please analyze this message and determine the appropriate next action. Use memory to maintain context."""

    # 4. Trigger memory-aware orchestrator with chat_id as user_id
    try:
        result = await memory_orchestrator.process_message(
            message=orchestrator_query,
            chat_id=str(chat_id)  # Using chat_id for memory isolation
        )
        print(f"Orchestrator result: {result}")
    except Exception as e:
        print(f"Error processing message {message.id} with orchestrator: {e}")
        message.status = 'failed'
        db.commit()
        return

    print(f"Finished processing message id: {message.id}")


async def main():
    """The main worker loop."""
    print("Starting worker...")
    while True:
        db: Session = next(get_db())
        message_to_process = None
        message_id_to_process = None
        try:
            # Find a new message and lock it in a single atomic transaction
            message_to_process = db.query(IncomingMessage).filter(IncomingMessage.status == 'new').order_by(IncomingMessage.created_at).first()
            if message_to_process:
                message_id_to_process = message_to_process.id
                message_to_process.status = 'processing'
                message_to_process.updated_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            print(f"Error fetching/locking message: {e}")
            db.rollback()
        finally:
            db.close()

        if message_id_to_process:
            # Re-query the message within the new processing_db session
            processing_db: Session = next(get_db())
            try:
                # Re-attach the message to the new session
                re_attached_message = processing_db.get(IncomingMessage, message_id_to_process)
                if re_attached_message:
                    await process_message(processing_db, re_attached_message)
                    # If successful, delete the message using the same session
                    processing_db.delete(re_attached_message)
                    processing_db.commit()
                else:
                    print(f"Error: Message {message_id_to_process} not found in new session.")
            except Exception as e:
                print(f"Failed to process message {message_id_to_process}: {e}")
                # Re-query the object in this session to update it
                failed_message = processing_db.query(IncomingMessage).filter(IncomingMessage.id == message_id_to_process).first()
                if failed_message:
                    failed_message.status = 'failed'
                    processing_db.commit()
            finally:
                processing_db.close()
        else:
            # No new messages, wait for a bit
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())