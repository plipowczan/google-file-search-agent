from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models import Store
from app.schemas import StoreCreate, StoreResponse, StoreListResponse, ErrorResponse
from app.services.google_file_search_service import get_google_file_search_service

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post(
    "/",
    response_model=StoreResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse, "description": "Store with this name already exists"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Google API error"},
    }
)
async def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new Store (knowledge base) and FileSearchStore in Google Cloud.
    
    US1: Zarządzanie Store'ami
    - [Pozytywny] Utworzenie nowego FileSearchStore w Google + rekord w SQLite
    - [Negatywny] Zwraca błąd 409 jeśli display_name już istnieje lokalnie
    """
    # Check if display_name already exists locally
    existing = db.query(Store).filter(Store.display_name == store_data.display_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nazwa musi być unikalna"
        )
    
    try:
        # Create FileSearchStore in Google Cloud
        google_service = get_google_file_search_service()
        google_store_name, display_name = google_service.create_file_search_store(store_data.display_name)
        
        #Create local record
        new_store = Store(
            display_name=display_name,
            google_store_name=google_store_name
        )
        
        db.add(new_store)
        db.commit()
        db.refresh(new_store)
        
        return new_store
    
    except Exception as e:
        db.rollback()
        # If Google API failed, try to cleanup
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Wystąpił błąd podczas tworzenia Store'a: {str(e)}"
        )


@router.get(
    "/",
    response_model=StoreListResponse,
    responses={
        200: {"model": StoreListResponse, "description": "List of all stores"},
    }
)
async def list_stores(db: Session = Depends(get_db)):
    """
    Get list of all Stores.
    
    Returns all available stores in the system.
    """
    stores = db.query(Store).order_by(Store.created_at.desc()).all()
    
    return StoreListResponse(
        stores=stores,
        total=len(stores)
    )


@router.get(
    "/{store_id}",
    response_model=StoreResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Store not found"},
    }
)
async def get_store(store_id: int, db: Session = Depends(get_db)):
    """
    Get a specific Store by ID.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store o ID {store_id} nie został znaleziony"
        )
    
    return store


@router.delete(
    "/{store_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Store not found"},
        500: {"model": ErrorResponse, "description": "Failed to delete from Google Cloud"},
    }
)
async def delete_store(store_id: int, db: Session = Depends(get_db)):
    """
    Delete a Store by ID.
    
    US1: [Brzegowy] Usunięcie Store'a usuwa zarówno lokalny rekord jak i FileSearchStore w Google Cloud
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store o ID {store_id} nie został znaleziony"
        )
    
    try:
        # Delete from Google Cloud first
        google_service = get_google_file_search_service()
        google_service.delete_file_search_store(store.google_store_name)
        
        # Then delete from local DB
        db.delete(store)
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Wystąpił błąd podczas usuwania Store'a: {str(e)}"
        )
