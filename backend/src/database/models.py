from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, ForeignKey, Text, LargeBinary
import os
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "sql_database"))
os.makedirs(BASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'agent.db')}"

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
    conversation_history = Column(Text, nullable=True)
    # Note: conversation_history kept for business audit trail, Mem0 memory used for AI intelligence
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

# Configuration Database Setup
DATABASE_URL_CONFIG = f"sqlite:///{os.path.join(BASE_DIR, 'configuration.db')}"
engine_config = create_engine(DATABASE_URL_CONFIG, connect_args={"check_same_thread": False})
SessionLocalConfig = sessionmaker(autocommit=False, autoflush=False, bind=engine_config)
BaseConfig = declarative_base()

class EnvConfig(BaseConfig):
    __tablename__ = 'env_config'
    id = Column(Integer, primary_key=True, index=True)
    telegram_bot_token = Column(String, nullable=True)
    client_secret_json = Column(Text, nullable=True) # Store as text, encryption needed for production
    tone_and_manner = Column(String, nullable=True) # Added new column

class KnowledgeBase(BaseConfig):
    __tablename__ = 'knowledge_base'
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    file_content = Column(LargeBinary, nullable=True) # Store raw binary
    created_at = Column(DateTime, default=func.now())
    file_hash = Column(String, nullable=True, index=True)  # SHA256 of content for dedupe
    study_status = Column(String, nullable=True, index=True, default='not_studied')  # not_studied|studied|error

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_config_db():
    db = SessionLocalConfig()
    try:
        yield db
    finally:
        db.close()

# Create tables if they don't exist for both databases
Base.metadata.create_all(bind=engine)
BaseConfig.metadata.create_all(bind=engine_config)

# Lightweight adaptive schema upgrade for newly added columns (SQLite only)
def _ensure_knowledge_base_columns():
    import sqlite3
    try:
        path = os.path.join(BASE_DIR, 'configuration.db')
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(knowledge_base)")
        existing = {row[1] for row in cur.fetchall()}
        # Columns we may have added after initial creation
        to_add = []
        if 'content_type' not in existing:
            to_add.append("ALTER TABLE knowledge_base ADD COLUMN content_type TEXT")
        if 'size_bytes' not in existing:
            to_add.append("ALTER TABLE knowledge_base ADD COLUMN size_bytes INTEGER")
        if 'created_at' not in existing:
            to_add.append("ALTER TABLE knowledge_base ADD COLUMN created_at DATETIME")
        if 'file_hash' not in existing:
            to_add.append("ALTER TABLE knowledge_base ADD COLUMN file_hash TEXT")
        if 'study_status' not in existing:
            to_add.append("ALTER TABLE knowledge_base ADD COLUMN study_status TEXT DEFAULT 'not_studied'")
        for stmt in to_add:
            try:
                cur.execute(stmt)
            except Exception:
                pass
        conn.commit()
        conn.close()
    except Exception:
        pass

_ensure_knowledge_base_columns()
