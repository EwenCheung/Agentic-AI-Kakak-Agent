import os
import asyncio
from typing import Optional
from anyio import to_thread
from strands import tool
from sqlalchemy.orm import Session
import telegram
# Removed from dotenv import load_dotenv
from datetime import datetime
from ....config.settings import settings

from ....database.models import Customer, get_db

async def _get_or_create_customer(db: Session, chat_id: int, name: Optional[str] = None) -> Customer:
    def _sync_get_or_create():
        customer = db.query(Customer).filter(Customer.telegram_chat_id == str(chat_id)).first()
        if not customer:
            customer = Customer(telegram_chat_id=str(chat_id), name=name)
            db.add(customer)
            db.commit()
            db.refresh(customer)
        return customer
    return await to_thread(_sync_get_or_create)

async def _log_agent_message_to_history(db: Session, customer_id: int, message_text: str):
    def _sync_log():
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            message_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            history_entry = f"[Agent at {message_time}]: {message_text}\n"
            
            if customer.conversation_history:
                customer.conversation_history += history_entry
            else:
                customer.conversation_history = history_entry
            db.commit()
    await to_thread(_sync_log)

@tool
async def send_message(chat_id: int, message: str) -> str:
    """
    Send a message to a specific chat using the Telegram Bot API.
    Args:
        chat_id: The ID of the chat.
        message: The message content to send.
    """
    bot_token = settings.get_telegram_bot_token()
    if not bot_token:
        return "Telegram bot not configured. Please configure the bot token in the dashboard."

    # Create a new Bot instance for each call to ensure connection is fresh.
    bot = telegram.Bot(token=bot_token)

    try:
        await bot.send_message(chat_id=chat_id, text=message)
        # Close the bot session to release connections
        await bot.shutdown()

        db: Session = next(get_db())
        customer = await _get_or_create_customer(db, chat_id)
        await _log_agent_message_to_history(db, customer.id, message)

        return "Message sent successfully."
    except telegram.error.TelegramError as e:
        return f"Failed to send message: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
