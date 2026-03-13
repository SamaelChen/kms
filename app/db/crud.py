"""
IntelliKnow KMS - Database CRUD Operations
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc, func
from datetime import datetime

from app.db.database import Document, QueryLog, IntentSpace


class DocumentCRUD:
    """CRUD operations for documents"""
    
    @staticmethod
    async def create(db: AsyncSession, doc_id: str, filename: str, file_path: str,
                     file_size: int, file_type: str, intent_space: str = "General") -> Document:
        document = Document(
            id=doc_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            intent_space=intent_space,
            status="pending"
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document
    
    @staticmethod
    async def get_by_id(db: AsyncSession, doc_id: str) -> Optional[Document]:
        result = await db.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, intent_space: Optional[str] = None,
                      status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Document]:
        query = select(Document)
        if intent_space:
            query = query.where(Document.intent_space == intent_space)
        if status:
            query = query.where(Document.status == status)
        query = query.order_by(desc(Document.created_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_status(db: AsyncSession, doc_id: str, status: str,
                           chunk_count: Optional[int] = None, error_message: Optional[str] = None):
        values = {"status": status, "updated_at": datetime.utcnow()}
        if chunk_count is not None:
            values["chunk_count"] = chunk_count
        if error_message:
            values["error_message"] = error_message
        
        await db.execute(update(Document).where(Document.id == doc_id).values(**values))
        await db.commit()
    
    @staticmethod
    async def delete(db: AsyncSession, doc_id: str) -> bool:
        result = await db.execute(delete(Document).where(Document.id == doc_id))
        await db.commit()
        return result.rowcount > 0


class QueryLogCRUD:
    """CRUD operations for query logs"""
    
    @staticmethod
    async def create(db: AsyncSession, query_text: str, intent_classified: str,
                     confidence_score: float, response_text: Optional[str] = None,
                     source_documents: Optional[str] = None, response_time_ms: Optional[float] = None,
                     frontend: Optional[str] = None, user_id: Optional[str] = None,
                     success: bool = True) -> QueryLog:
        log = QueryLog(
            query_text=query_text,
            intent_classified=intent_classified,
            confidence_score=confidence_score,
            response_text=response_text,
            source_documents=source_documents,
            response_time_ms=response_time_ms,
            frontend=frontend,
            user_id=user_id,
            success=success
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
    
    @staticmethod
    async def get_recent(db: AsyncSession, limit: int = 100) -> List[QueryLog]:
        result = await db.execute(
            select(QueryLog).order_by(desc(QueryLog.created_at)).limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        """Get query statistics"""
        total = await db.execute(select(func.count(QueryLog.id)))
        success = await db.execute(select(func.count(QueryLog.id)).where(QueryLog.success == True))
        avg_confidence = await db.execute(select(func.avg(QueryLog.confidence_score)))
        avg_response_time = await db.execute(select(func.avg(QueryLog.response_time_ms)))
        
        return {
            "total_queries": total.scalar() or 0,
            "successful_queries": success.scalar() or 0,
            "average_confidence": round(avg_confidence.scalar() or 0, 2),
            "average_response_time_ms": round(avg_response_time.scalar() or 0, 2)
        }


class IntentSpaceCRUD:
    """CRUD operations for intent spaces"""
    
    @staticmethod
    async def create(db: AsyncSession, space_id: str, name: str,
                     description: Optional[str] = None, keywords: Optional[str] = None) -> IntentSpace:
        space = IntentSpace(
            id=space_id,
            name=name,
            description=description,
            keywords=keywords
        )
        db.add(space)
        await db.commit()
        await db.refresh(space)
        return space
    
    @staticmethod
    async def get_by_id(db: AsyncSession, space_id: str) -> Optional[IntentSpace]:
        result = await db.execute(select(IntentSpace).where(IntentSpace.id == space_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[IntentSpace]:
        result = await db.execute(select(IntentSpace).where(IntentSpace.name == name))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[IntentSpace]:
        result = await db.execute(select(IntentSpace).order_by(IntentSpace.name))
        return list(result.scalars().all())
    
    @staticmethod
    async def update(db: AsyncSession, space_id: str, **kwargs):
        kwargs["updated_at"] = datetime.utcnow()
        await db.execute(update(IntentSpace).where(IntentSpace.id == space_id).values(**kwargs))
        await db.commit()
    
    @staticmethod
    async def delete(db: AsyncSession, space_id: str) -> bool:
        result = await db.execute(delete(IntentSpace).where(IntentSpace.id == space_id))
        await db.commit()
        return result.rowcount > 0