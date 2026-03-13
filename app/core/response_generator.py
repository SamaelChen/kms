"""Response generation module using LLM"""
from typing import List, Tuple
import httpx

from app.config import settings


class ResponseGenerator:
    """Generate responses using local LLM"""
    
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.model = settings.LLM_MODEL
    
    async def generate(
        self,
        query: str,
        context_chunks: List[Tuple[dict, float]],
        intent_space: str
    ) -> str:
        """
        Generate response based on retrieved context
        
        Args:
            query: User query
            context_chunks: List of (chunk_metadata, score) tuples
            intent_space: Classified intent space
        
        Returns:
            Generated response with citations
        """
        if not context_chunks:
            return self._generate_no_context_response(query, intent_space)
        
        # Build context from chunks
        context_text = self._build_context(context_chunks)
        
        # Build prompt
        prompt = self._build_prompt(query, context_text, intent_space)
        
        # Generate response
        response = await self._call_llm(prompt)
        
        # Add citations
        response_with_citations = self._add_citations(response, context_chunks)
        
        return response_with_citations
    
    def _build_context(self, chunks: List[Tuple[dict, float]]) -> str:
        """Build context text from chunks"""
        context_parts = []
        
        for i, (chunk, score) in enumerate(chunks[:5], 1):  # Top 5 chunks
            text = chunk.get("text", "")
            doc_name = chunk.get("document_name", "Unknown")
            
            context_parts.append(
                f"[Source {i}] From {doc_name}:\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str, intent_space: str) -> str:
        """Build LLM prompt"""
        return f"""You are a helpful knowledge management assistant. Answer the user's question based on the provided context from the {intent_space} knowledge base.

Context:
{context}

User Question: {query}

Instructions:
1. Answer based ONLY on the provided context
2. If the context doesn't contain the answer, say "I don't have enough information to answer that question."
3. Be concise and accurate
4. Include citations to source documents when referencing specific information

Answer:"""
    
    async def _call_llm(self, prompt: str) -> str:
        """Call Ollama LLM"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 500
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    return f"Error: LLM returned status {response.status_code}"
                    
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _add_citations(self, response: str, chunks: List[Tuple[dict, float]]) -> str:
        """Add citations to response"""
        citations = []
        seen_docs = set()
        
        for chunk, score in chunks[:3]:
            doc_name = chunk.get("document_name", "Unknown")
            if doc_name not in seen_docs:
                citations.append(f"- {doc_name}")
                seen_docs.add(doc_name)
        
        if citations:
            response += "\n\n**Sources:**\n" + "\n".join(citations)
        
        return response
    
    def _generate_no_context_response(self, query: str, intent_space: str) -> str:
        """Generate response when no context found"""
        return f"""I couldn't find relevant information in the {intent_space} knowledge base to answer your question.

Your query: "{query}"

Suggestions:
- Try rephrasing your question
- Check if your question relates to a different category (HR, Legal, Finance)
- Upload relevant documents if this topic isn't covered yet"""


# Global response generator instance
response_generator = ResponseGenerator()