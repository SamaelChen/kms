"""Intent space endpoints"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.crud import IntentSpaceCRUD
from app.models.intent import IntentSpaceResponse

router = APIRouter()


@router.get("/spaces", response_model=List[IntentSpaceResponse])
async def list_intent_spaces(db: AsyncSession = Depends(get_db)):
    spaces = await IntentSpaceCRUD.get_all(db)
    result = []
    for space in spaces:
        space_id = str(space.id)
        space_name = str(space.name)
        space_desc = str(space.description) if space.description is not None else None
        space_keywords = str(space.keywords) if space.keywords is not None else ""
        keywords_list = [k.strip() for k in space_keywords.split(",")] if space_keywords else []
        created = space.created_at if isinstance(space.created_at, datetime) else datetime.utcnow()
        updated = space.updated_at if isinstance(space.updated_at, datetime) else datetime.utcnow()
        
        result.append(IntentSpaceResponse(
            id=space_id,
            name=space_name,
            description=space_desc,
            keywords=keywords_list,
            document_count=0,
            created_at=created,
            updated_at=updated
        ))
    return result


@router.get("/spaces/{space_id}", response_model=IntentSpaceResponse)
async def get_intent_space(space_id: str, db: AsyncSession = Depends(get_db)):
    space = await IntentSpaceCRUD.get_by_id(db, space_id)
    if not space:
        raise HTTPException(404, "Intent space not found")
    
    space_id_str = str(space.id)
    space_name = str(space.name)
    space_desc = str(space.description) if space.description is not None else None
    space_keywords = str(space.keywords) if space.keywords is not None else ""
    keywords_list = [k.strip() for k in space_keywords.split(",")] if space_keywords else []
    created = space.created_at if isinstance(space.created_at, datetime) else datetime.utcnow()
    updated = space.updated_at if isinstance(space.updated_at, datetime) else datetime.utcnow()
    
    return IntentSpaceResponse(
        id=space_id_str,
        name=space_name,
        description=space_desc,
        keywords=keywords_list,
        document_count=0,
        created_at=created,
        updated_at=updated
    )
