"""
Semantic text chunker for splitting documents into meaningful segments.
"""
import re
from typing import List
import nltk


class TextChunker:
    DEFAULT_MAX_TOKENS = 500
    TOKEN_ESTIMATE_RATIO = 0.75
    
    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS):
        self.max_tokens = max_tokens
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
    
    def estimate_tokens(self, text: str) -> int:
        word_count = len(text.split())
        return int(word_count / self.TOKEN_ESTIMATE_RATIO)
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into semantic chunks using paragraphs and sentences.
        
        Strategy: Split on paragraphs first, then sentences if needed.
        Ensures no chunk exceeds max_tokens while preserving meaning.
        """
        if not text or not text.strip():
            return []
        
        paragraphs = self._split_into_paragraphs(text)
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for paragraph in paragraphs:
            para_tokens = self.estimate_tokens(paragraph)
            
            if para_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                chunks.extend(self._chunk_large_paragraph(paragraph))
            elif current_tokens + para_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_tokens = para_tokens
            else:
                current_chunk.append(paragraph)
                current_tokens += para_tokens
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _chunk_large_paragraph(self, paragraph: str) -> List[str]:
        try:
            sentences = nltk.sent_tokenize(paragraph)
        except:
            sentences = self._simple_sentence_split(paragraph)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sent_tokens = self.estimate_tokens(sentence)
            
            if sent_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                chunks.extend(self._split_long_sentence(sentence))
            elif current_tokens + sent_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_tokens = sent_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sent_tokens
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        words = sentence.split()
        word_chunk = []
        word_count = 0
        chunks = []
        max_words = int(self.max_tokens * self.TOKEN_ESTIMATE_RATIO)
        
        for word in words:
            word_chunk.append(word)
            word_count += 1
            if word_count >= max_words:
                chunks.append(' '.join(word_chunk))
                word_chunk = []
                word_count = 0
        
        if word_chunk:
            chunks.append(' '.join(word_chunk))
        
        return chunks
    
    def _simple_sentence_split(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
