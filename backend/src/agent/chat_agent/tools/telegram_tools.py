import os
import asyncio
from typing import Optional
from strands import tool
from sqlalchemy.orm import Session
import telegram
from dotenv import load_dotenv
from datetime import datetime

from ....database.models import Customer, get_db
from ....config.settings import settings


bot: Optional[telegram.Bot] = None
if settings.TELEGRAM_BOT_TOKEN:
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)

async def _get_or_create_customer(db: Session, chat_id: int, name: Optional[str] = None) -> Customer:
    customer = db.query(Customer).filter(Customer.telegram_chat_id == str(chat_id)).first()
    if not customer:
        customer = Customer(telegram_chat_id=str(chat_id), name=name)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return customer

async def _log_agent_message_to_history(db: Session, customer_id: int, message_text: str):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        message_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history_entry = f"[Agent at {message_time}]: {message_text}\n"
        
        if customer.conversation_history:
            customer.conversation_history += history_entry
        else:
            customer.conversation_history = history_entry
        db.commit()

@tool
async def send_message(chat_id: int, message: str) -> str:
    """
    Send a message to a specific chat using the Telegram Bot API.
    Args:
        chat_id: The ID of the chat.
        message: The message content to send.
    """
    if not bot:
        return "Telegram bot not configured. Set the settings.TELEGRAM_BOT_TOKEN environment variable."

    try:
        await bot.send_message(chat_id=chat_id, text=message)

        db: Session = next(get_db())
        customer = await _get_or_create_customer(db, chat_id)
        await _log_agent_message_to_history(db, customer.id, message)

        return "Message sent successfully."
    except telegram.error.TelegramError as e:
        return f"Failed to send message: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"