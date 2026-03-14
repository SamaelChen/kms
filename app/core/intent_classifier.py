"""Intent classification module"""
import re
from typing import Tuple, Optional
import httpx

from app.config import settings


class IntentClassifier:
    def __init__(self):
        self.confidence_threshold = settings.INTENT_CONFIDENCE_THRESHOLD
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.llm_model = settings.LLM_MODEL
        self.client: Optional[httpx.AsyncClient] = None
        
        self.intent_patterns = {
            "HR": [
                r"\b(hr|human resources|employee|staff|hiring|recruitment|onboarding|offboarding|payroll|benefit|leave|vacation|sick day|policy|handbook)\b",
                r"\b(contract|employment|salary|compensation|promotion|performance review|disciplinary)\b"
            ],
            "Legal": [
                r"\b(legal|contract|agreement|terms|conditions|compliance|regulation|law|liability|dispute|litigation)\b",
                r"\b(nda|non-disclosure|intellectual property|ip|trademark|copyright|patent|privacy policy|gdpr)\b"
            ],
            "Finance": [
                r"\b(finance|financial|budget|expense|reimbursement|invoice|payment|accounting|tax|audit)\b",
                r"\b(cost|revenue|profit|loss|investment|funding|purchase order|po|quote|pricing)\b"
            ]
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
                timeout=httpx.Timeout(15.0, connect=5.0)
            )
        return self.client
    
    async def close(self):
        if self.client and not self.client.is_closed:
            await self.client.aclose()
    
    async def classify(self, query: str) -> Tuple[str, float, str]:
        """
        Classify query into intent space
        
        Args:
            query: User query text
        
        Returns:
            Tuple of (intent_space, confidence_score, method)
        """
        query_lower = query.lower()
        
        # Try rule-based classification first
        intent, confidence = self._rule_based_classify(query_lower)
        if intent and confidence >= self.confidence_threshold:
            return intent, confidence, "rule_based"
        
        # Fall back to LLM classification
        intent, confidence = await self._llm_classify(query)
        if intent and confidence >= self.confidence_threshold:
            return intent, confidence, "llm"
        
        # Default to General if confidence is low
        return "General", 0.5, "fallback"
    
    def _rule_based_classify(self, query: str) -> Tuple[Optional[str], float]:
        """
        Classify using keyword patterns
        
        Returns:
            Tuple of (intent_space, confidence_score) or (None, 0)
        """
        scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return None, 0.0
        
        # Get intent with highest score
        best_intent = max(scores.items(), key=lambda x: x[1])[0]
        best_score = scores[best_intent]
        
        # Normalize confidence (rough estimate)
        confidence = min(0.7 + (best_score * 0.1), 0.95)
        
        return best_intent, confidence
    
    async def _llm_classify(self, query: str) -> Tuple[Optional[str], float]:
        try:
            prompt = f"""Classify the following query into one of these categories: HR, Legal, Finance, or General.

Query: "{query}"

Respond with only the category name and a confidence score (0-1) separated by a comma.
Example: HR, 0.85

Classification:"""
            
            client = await self._get_client()
            response = await client.post(
                self.ollama_url,
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                
                parts = text.split(",")
                if len(parts) >= 2:
                    intent = parts[0].strip()
                    confidence = float(parts[1].strip())
                    
                    valid_intents = ["HR", "Legal", "Finance", "General"]
                    if intent in valid_intents:
                        return intent, confidence
            
            return None, 0.0
            
        except Exception as e:
            print(f"LLM classification error: {e}")
            return None, 0.0


# Global classifier instance
intent_classifier = IntentClassifier()