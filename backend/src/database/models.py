from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./src/database/sql_database/agent.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, index=True)
    issue = Column(String, nullable=False)
    priority = Column(String, default='medium')
    status = Column(String, default='open')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    assigned_to = Column(String, nullable=True)

    def __repr__(self):
        return f'<Ticket {self.id}>'

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, index=True)
    telegram_chat_id = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=True)
    company_id = Column(String, nullable=True)
    conversation_summary = Column(Text, nullable=True)
    conversation_history = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<Customer {self.id} ({self.name})>'

class IncomingMessage(Base):
    __tablename__ = 'incoming_messages'
    id = Column(Integer, primary_key=True, index=True)
    payload = Column(Text, nullable=False)
    status = Column(String, default='new', index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<IncomingMessage {self.id} ({self.status})>'

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)
