from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./src/database/sql_database/tickets.db"

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()