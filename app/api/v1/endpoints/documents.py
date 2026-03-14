import asyncio
import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.crud import DocumentCRUD
from app.core.document_processor import document_processor
from app.models.document import DocumentUploadResponse, DocumentResponse, DocumentListResponse

router = APIRouter()

SUPPORTED_EXTENSIONS = ['pdf', 'docx', 'txt', 'md', 'xlsx', 'pptx']

logger = logging.getLogger(__name__)


async def _process_document_background(doc_id: str, file_path: str, intent_space: str):
    try:
        await document_processor.process(doc_id, file_path, intent_space)
    except Exception as e:
        logger.error(f"Background processing failed for {doc_id}: {e}")


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    intent_space: str = Form("General"),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(400, "Filename is required")
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(400, f"Only {', '.join(SUPPORTED_EXTENSIONS)} files are supported")
    
    try:
        content = await file.read()
        
        doc_id, file_path, file_size = await document_processor.save_upload(
            content, file.filename
        )
        
        document = await DocumentCRUD.create(
            db=db,
            doc_id=doc_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext,
            intent_space=intent_space
        )
        
        asyncio.create_task(
            _process_document_background(doc_id, file_path, intent_space)
        )
        
        return DocumentUploadResponse(
            document_id=doc_id,
            filename=file.filename,
            status="pending",
            message="Document uploaded successfully. Processing will begin shortly."
        )
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except IOError as e:
        logger.error(f"File operation failed: {e}")
        raise HTTPException(500, "File processing failed")
    except Exception as e:
        logger.error(f"Unexpected error in upload: {e}")
        raise HTTPException(500, "Upload failed")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    intent_space: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all documents"""
    documents = await DocumentCRUD.get_all(
        db=db,
        intent_space=intent_space,
        status=status,
        limit=limit,
        offset=offset
    )
    
    total = len(documents)
    
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    """Get document by ID"""
    document = await DocumentCRUD.get_by_id(db, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    document = await DocumentCRUD.get_by_id(db, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    file_path_value = document.file_path
    if file_path_value is not None:
        file_path = str(file_path_value)
        await document_processor.delete_upload(file_path)
    
    await DocumentCRUD.delete(db, document_id)
    
    return {"message": "Document deleted successfully"}