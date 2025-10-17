from fastapi import FastAPI, Request
import logging
from fastapi.middleware.cors import CORSMiddleware # Added this import

from .api.routes import router as api_router
from .database.models import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SuperConfig API")

# Set up CORS middleware
origins = [
    "http://localhost",
    "http://localhost:3000",  # React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes 
app.include_router(api_router)

@app.get("/")
async def root(request: Request):
    return {"message": "SuperConfig API is running"}