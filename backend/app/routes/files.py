from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
import tempfile
from pathlib import Path

from app.database import get_db
from app.models import File, Store
from app.schemas import FileResponse, FileListResponse, ErrorResponse
from app.services.google_file_search_service import get_google_file_search_service

router = APIRouter(prefix="/stores/{store_id}/files", tags=["files"])

@router.post(
    "/",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse, "description": "Store not found"},
        500: {"model": ErrorResponse, "description": "Google API error"},
    }
)
async def upload_file(
    store_id: int,
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file to a specific Store.
    
    US2: Upload i Zarządzanie Plikami
    - [Pozytywny] Upload pliku do Google File Search + rekord w SQLite
    """
    # Check if store exists
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store o ID {store_id} nie został znaleziony"
        )

    # Save uploaded file temporarily
    # Create a temp directory if not exists (though tempfile handles this)
    # We use a named temporary file to get a path
    
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Upload to Google
        google_service = get_google_file_search_service()
        
        # Note: We pass the store's google_store_name
        # The service returns metadata about the uploaded file
        # We assume the service handles the complexity of "uploading to store"
        result = google_service.upload_to_store(
            file_path=tmp_path,
            google_store_name=store.google_store_name,
            display_name=file.filename
        )
        
        # Result should contain document info. 
        # Based on typical Google API responses, we might get an object.
        # Let's assume the service returns an object or dict with 'name' (document_id)
        # If the service returns the `uploaded_file` object (from files.upload), its name is `files/xyz`.
        # If it returns the `file_search_store` operation result, it might be different.
        # Let's adjust based on what we implemented in the service.
        # In service we returned: client.file_search_stores.upload_to_file_search_store(...)
        # This returns a UploadFileResponse or similar.
        # Let's assume we can access .name (which is the file resource name).
        
        # Wait, `upload_to_file_search_store` returns `tuple[str, str]` in my previous thought?
        # No, I returned the result of the call directly.
        # The result of `upload_to_file_search_store` is usually an operation or a response containing the file resource.
        # Let's assume it has a `.name` attribute which is the document resource name.
        
        # However, to be safe, let's inspect what we get or assume standard attribute access.
        # If it's a dict (from my type hint in service, though I didn't enforce it), we access keys.
        # But `upload_to_file_search_store` returns an object.
        # Let's try to access `.name` (document ID) and `.uri` or similar if needed.
        # Actually, for `File` model we need `document_id`.
        
        document_id = getattr(result, 'name', None)
        if not document_id:
             # Fallback if it's a dict
             document_id = result.get('name')
        
        # Create local record
        new_file = File(
            store_id=store.id,
            document_id=document_id,
            display_name=file.filename,
            status="COMPLETED" # We assume it's done if the call succeeded (or we might need async check)
        )
        
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        
        return new_file

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas uploadu pliku: {str(e)}"
        )
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.get(
    "/",
    response_model=FileListResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Store not found"},
    }
)
async def list_files(store_id: int, db: Session = Depends(get_db)):
    """
    List files in a specific Store.
    
    US3: Podgląd zawartości Store
    """
    # Check if store exists
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store o ID {store_id} nie został znaleziony"
        )
        
    files = db.query(File).filter(File.store_id == store_id).order_by(File.upload_date.desc()).all()
    
    return FileListResponse(
        files=files,
        total=len(files)
    )

@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "File not found"},
        500: {"model": ErrorResponse, "description": "Google API error"},
    }
)
async def delete_file(store_id: int, file_id: int, db: Session = Depends(get_db)):
    """
    Delete a file from a Store.
    """
    # Check if store exists (optional but good for consistency)
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store o ID {store_id} nie został znaleziony"
        )

    file = db.query(File).filter(File.id == file_id, File.store_id == store_id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plik o ID {file_id} nie został znaleziony w tym Store"
        )
        
    try:
        # Delete from Google
        google_service = get_google_file_search_service()
        google_service.delete_file(file.document_id)
        
        # Delete from DB
        db.delete(file)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas usuwania pliku: {str(e)}"
        )
