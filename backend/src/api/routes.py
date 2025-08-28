# This file will contain the API routes for the backend.

from fastapi import APIRouter

router = APIRouter()

@router.post("/message")
def handle_message(message: dict):
    # TODO: Implement message handling logic
    return {"status": "message received"}
