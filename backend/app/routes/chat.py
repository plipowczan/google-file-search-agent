from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Store
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.schemas import ErrorResponse
from app.services.google_file_search_service import get_google_file_search_service

import logging

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=ChatResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Store not found"},
        500: {"model": ErrorResponse, "description": "Google API error"},
    }
)
async def chat_with_store(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with a specific Store using Google File Search.
    
    US4: Czat z Agentem (Kontekstowy)
    """
    logger.debug(f"Chat request received: store_id={chat_request.store_id}, message_length={len(chat_request.message)}")
    
    # Check if store exists
    store = db.query(Store).filter(Store.id == chat_request.store_id).first()
    if not store:
        logger.warning(f"Store not found: id={chat_request.store_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store o ID {chat_request.store_id} nie został znaleziony"
        )
    
    logger.debug(f"Store found: id={store.id}, name='{store.display_name}', google_name='{store.google_store_name}'")
    
    try:
        google_service = get_google_file_search_service()
        
        response_text = google_service.chat_with_store(
            google_store_name=store.google_store_name,
            message=chat_request.message,
            model_name=chat_request.model
        )
        
        logger.debug(f"Response generated successfully, length={len(response_text)}")
        
        return ChatResponse(
            response=response_text,
            citations=[] # Citations are usually embedded in text or need extra parsing
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas generowania odpowiedzi: {str(e)}"
        )
