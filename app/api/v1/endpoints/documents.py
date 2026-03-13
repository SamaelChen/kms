"""Document management endpoints"""
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.crud import DocumentCRUD
from app.core.document_processor import document_processor
from app.models.document import DocumentUploadResponse, DocumentResponse, DocumentListResponse

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    intent_space: str = Form("General"),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a document"""
    # Validate file type
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["pdf", "docx"]:
        raise HTTPException(400, "Only PDF and DOCX files are supported")
    
    try:
        # Read file content
        content = await file.read()
        
        # Save file
        doc_id, file_path, file_size = await document_processor.save_upload(
            content, file.filename
        )
        
        # Create database record
        document = await DocumentCRUD.create(
            db=db,
            doc_id=doc_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext,
            intent_space=intent_space
        )
        
        # TODO: Trigger async processing
        
        return DocumentUploadResponse(
            document_id=doc_id,
            filename=file.filename,
            status="pending",
            message="Document uploaded successfully. Processing will begin shortly."
        )
        
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    intent_space: str = None,
    status: str = None,
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
    """Delete a document"""
    document = await DocumentCRUD.get_by_id(db, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    # Delete file
    await document_processor.delete_upload(document.file_path)
    
    # Delete database record
    await DocumentCRUD.delete(db, document_id)
    
    return {"message": "Document deleted successfully"}