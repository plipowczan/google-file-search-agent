from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class FileBase(BaseModel):
    display_name: str

class FileCreate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
    store_id: int
    document_id: str
    upload_date: datetime
    status: str

    class Config:
        from_attributes = True

class FileListResponse(BaseModel):
    files: List[FileResponse]
    total: int
