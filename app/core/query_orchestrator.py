"""Query orchestrator module"""
import time
from typing import List, Tuple, Optional

from app.config import settings
from app.core.intent_classifier import intent_classifier
from app.core.knowledge_base import knowledge_base
from app.core.response_generator import response_generator
from app.models.query import QueryRequest, QueryResponse, Citation


class QueryOrchestrator:
    """Orchestrate query processing pipeline"""
    
    def __init__(self):
        self.intent_classifier = intent_classifier
        self.knowledge_base = knowledge_base
        self.response_generator = response_generator
    
    async def process(
        self,
        request: QueryRequest
    ) -> QueryResponse:
        """
        Process a query through the full pipeline
        
        Args:
            request: Query request with text and metadata
        
        Returns:
            Query response with answer and citations
        """
        start_time = time.time()
        
        # Step 1: Classify intent
        intent_space, confidence, method = await self.intent_classifier.classify(
            request.query
        )
        
        # Step 2: Search knowledge base
        search_results = await self.knowledge_base.search(
            query=request.query,
            intent_space=intent_space,
            top_k=5
        )
        
        # Step 3: Generate response
        response_text = await self.response_generator.generate(
            query=request.query,
            context_chunks=search_results,
            intent_space=intent_space
        )
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Build citations
        citations = self._build_citations(search_results)
        
        return QueryResponse(
            query=request.query,
            response=response_text,
            intent_classified=intent_space,
            confidence_score=confidence,
            citations=citations,
            response_time_ms=response_time_ms
        )
    
    def _build_citations(self, search_results: List[Tuple[dict, float]]) -> List[Citation]:
        """Build citation objects from search results"""
        citations = []
        seen_docs = set()
        
        for chunk, score in search_results:
            doc_id = chunk.get("document_id", "")
            if doc_id not in seen_docs:
                citation = Citation(
                    document_id=doc_id,
                    document_name=chunk.get("document_name", "Unknown"),
                    chunk_index=chunk.get("chunk_index", 0),
                    text_preview=chunk.get("text", "")[:200] + "..."
                )
                citations.append(citation)
                seen_docs.add(doc_id)
        
        return citations


# Global orchestrator instance
query_orchestrator = QueryOrchestrator()