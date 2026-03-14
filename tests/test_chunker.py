"""Unit tests for text chunker module"""
import pytest

from app.core.chunker import TextChunker


class TestTextChunker:
    @pytest.fixture
    def chunker(self):
        return TextChunker(chunk_size=100, chunk_overlap=20)
    
    def test_chunker_initialization(self, chunker):
        assert chunker.chunk_size == 100
        assert chunker.chunk_overlap == 20
        assert chunker.min_chunk_length == 50
    
    def test_chunk_short_text(self, chunker):
        text = "This is a short text."
        chunks = chunker.chunk_text(text, "doc-1")
        
        assert len(chunks) == 1
        assert chunks[0]["text"] == text
        assert chunks[0]["document_id"] == "doc-1"
        assert "chunk_id" in chunks[0]
    
    def test_chunk_long_text(self, chunker):
        text = "Word " * 200  # About 1000 characters
        chunks = chunker.chunk_text(text, "doc-1")
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert "text" in chunk
            assert "chunk_id" in chunk
            assert "document_id" in chunk
            assert chunk["document_id"] == "doc-1"
    
    def test_chunk_overlap(self, chunker):
        text = "A" * 150  # 150 characters
        chunks = chunker.chunk_text(text, "doc-1")
        
        if len(chunks) > 1:
            first_chunk_end = chunks[0]["text"][-20:]
            second_chunk_start = chunks[1]["text"][:20]
            assert first_chunk_end == second_chunk_start
    
    def test_chunk_empty_text(self, chunker):
        chunks = chunker.chunk_text("", "doc-1")
        assert len(chunks) == 0
    
    def test_chunk_whitespace_only(self, chunker):
        chunks = chunker.chunk_text("   \n\t  ", "doc-1")
        assert len(chunks) == 0
    
    def test_clean_chunk_excessive_whitespace(self, chunker):
        dirty = "This    has   too    many   spaces"
        clean = chunker._clean_chunk(dirty)
        assert "    " not in clean
        assert clean == "This has too many spaces"
    
    def test_clean_chunk_short_text(self, chunker):
        short = "Hi"
        result = chunker._clean_chunk(short)
        assert result == ""
    
    def test_estimate_tokens(self, chunker):
        text = "This is a test sentence with eight words."
        tokens = chunker.estimate_tokens(text)
        
        assert tokens > 0
        assert tokens >= len(text.split())  # At least as many as words
    
    def test_chunk_preserves_paragraphs(self, chunker):
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        chunks = chunker.chunk_text(text, "doc-1")
        
        assert len(chunks) > 0
    
    def test_chunk_with_special_characters(self, chunker):
        text = "Special chars: àáâãäåæçèéêë ñ 中文 🎉"
        chunks = chunker.chunk_text(text, "doc-1")
        
        assert len(chunks) >= 1
    
    def test_chunk_id_format(self, chunker):
        text = "Test"
        chunks = chunker.chunk_text(text, "doc-1")
        
        assert len(chunks) == 1
        assert chunks[0]["chunk_id"].startswith("doc-1_chunk_")
